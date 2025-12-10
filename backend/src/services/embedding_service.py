from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any
from src.utils.config import settings
import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from src.services.cache_service import cache_service
import hashlib

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding service with a lightweight model.

        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

        # Initialize Qdrant client for storage and retrieval
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=10
        )
        self.collection_name = "textbook_embeddings"
        self._ensure_collection_exists()

    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model {self.model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model {self.model_name}: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text with caching.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")

        # Create cache key based on the text content
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"embedding:{text_hash}"

        # Check cache first
        cached_embedding = cache_service.get(cache_key)
        if cached_embedding is not None:
            logger.debug(f"Embedding cache hit for text hash: {text_hash}")
            return cached_embedding

        try:
            embedding = self.model.encode([text])
            # Convert to list of floats for JSON serialization
            result = embedding[0].tolist()

            # Cache the result
            cache_service.set(cache_key, result, ttl=3600)  # Cache for 1 hour
            logger.debug(f"Embedding cached for text hash: {text_hash}")

            return result
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            raise

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with caching.

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        if not self.model:
            raise RuntimeError("Embedding model not loaded")

        # Check cache for each text and build result
        results = []
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            text_hash = hashlib.md5(text.encode()).hexdigest()
            cache_key = f"embedding:{text_hash}"

            cached_embedding = cache_service.get(cache_key)
            if cached_embedding is not None:
                logger.debug(f"Embedding cache hit for text hash: {text_hash}")
                results.append(cached_embedding)
            else:
                results.append(None)  # Placeholder
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Generate embeddings for uncached texts
        if uncached_texts:
            try:
                uncached_embeddings = self.model.encode(uncached_texts)
                uncached_embeddings_list = [embedding.tolist() for embedding in uncached_embeddings]

                # Update results and cache
                for idx, (text, embedding) in enumerate(zip(uncached_texts, uncached_embeddings_list)):
                    text_hash = hashlib.md5(text.encode()).hexdigest()
                    cache_key = f"embedding:{text_hash}"

                    # Update the results list
                    results[uncached_indices[idx]] = embedding

                    # Cache the result
                    cache_service.set(cache_key, embedding, ttl=3600)  # Cache for 1 hour
                    logger.debug(f"Embedding cached for text hash: {text_hash}")

            except Exception as e:
                logger.error(f"Failed to generate embeddings for texts: {e}")
                raise

        return results

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score between 0 and 1
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            # Ensure the result is between 0 and 1
            return max(0.0, min(1.0, float(similarity)))
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0

    def _ensure_collection_exists(self):
        """Ensure the embeddings collection exists in Qdrant"""
        try:
            collections = self.client.get_collections()
            collection_exists = any(col.name == self.collection_name for col in collections.collections)

            if not collection_exists:
                # Use the size of our embedding model (all-MiniLM-L6-v2 produces 384-dim vectors)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def store_embeddings(self, chapter_id: str, content: str, embedding: List[float], metadata: Dict[str, Any] = None):
        """Store embeddings for a chapter in Qdrant"""
        try:
            point = models.PointStruct(
                id=chapter_id,
                vector=embedding,
                payload={
                    "chapter_id": chapter_id,
                    "content": content,
                    "metadata": metadata or {}
                }
            )

            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            logger.info(f"Stored embedding for chapter: {chapter_id}")
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            raise

    def search_similar(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar content based on embedding with caching"""
        # Create cache key based on query embedding and limit
        query_str = f"{query_embedding}_{limit}"
        query_hash = hashlib.md5(query_str.encode()).hexdigest()
        cache_key = f"search_result:{query_hash}"

        # Check cache first
        cached_result = cache_service.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Search result cache hit for query hash: {query_hash}")
            return cached_result

        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )

            processed_results = [
                {
                    "chapter_id": result.payload.get("chapter_id"),
                    "content": result.payload.get("content"),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score
                }
                for result in results
            ]

            # Cache the result (shorter TTL for search results as content might change)
            cache_service.set(cache_key, processed_results, ttl=300)  # Cache for 5 minutes

            return processed_results
        except Exception as e:
            logger.error(f"Error searching for similar content: {e}")
            raise

    def delete_by_chapter_id(self, chapter_id: str):
        """Delete embeddings for a specific chapter"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="payload.chapter_id",
                                match=models.MatchValue(value=chapter_id)
                            )
                        ]
                    )
                )
            )
            logger.info(f"Deleted embeddings for chapter: {chapter_id}")
        except Exception as e:
            logger.error(f"Error deleting embeddings: {e}")
            raise


# Global instance
embedding_service = EmbeddingService()