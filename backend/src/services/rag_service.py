"""
RAG (Retrieval-Augmented Generation) Service

This service connects the embedding service with AI responses to provide
contextual answers based on textbook content.
"""

from typing import List, Dict, Any, Optional
from src.services.embedding_service import embedding_service
from src.services.content_service import content_service
from src.models.ai_query import AIQuery, AIResponse
from src.database_service import db_service
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RagService:
    def __init__(self):
        self.embedding_service = embedding_service
        self.content_service = content_service

    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from textbook content based on the query.

        Args:
            query: User's question/query
            top_k: Number of most relevant chunks to retrieve

        Returns:
            List of relevant content chunks with metadata
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_service.generate_embedding(query)

            # Search for similar content in the vector database
            similar_chunks = self.embedding_service.search_similar(
                query_embedding=query_embedding,
                limit=top_k
            )

            # Return the retrieved context
            return similar_chunks
        except Exception as e:
            logger.error(f"Error retrieving context for query '{query}': {e}")
            return []

    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an AI response based on the query and retrieved context.

        Args:
            query: User's original question
            context_chunks: Relevant context retrieved from textbook
            user_id: Optional user ID for tracking

        Returns:
            Generated response with sources and confidence
        """
        try:
            # Create a prompt combining the query and context
            context_text = " ".join([chunk["content"] for chunk in context_chunks])

            # Mock AI response generation - in a real implementation, this would call an LLM
            # For now, we'll create a response based on the context and query
            answer = f"Based on the textbook content, I can provide information about: {query}. Here's what the textbook says: {context_text[:500]}..."

            # Calculate confidence based on the number of context chunks and their scores
            if context_chunks:
                avg_score = sum(chunk["score"] for chunk in context_chunks) / len(context_chunks)
                confidence = min(1.0, avg_score)  # Ensure confidence is between 0 and 1
            else:
                confidence = 0.1  # Low confidence if no context found

            # Prepare sources from the context chunks
            sources = []
            for chunk in context_chunks:
                source = {
                    "chapterId": chunk.get("chapter_id", "unknown"),
                    "chapterTitle": chunk.get("metadata", {}).get("title", "Unknown Chapter"),
                    "section": chunk.get("metadata", {}).get("section", "Unknown Section"),
                    "confidence": chunk.get("score", 0.0)
                }
                sources.append(source)

            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence
            }
        except Exception as e:
            logger.error(f"Error generating response for query '{query}': {e}")
            return {
                "answer": "I'm sorry, I couldn't generate a response based on the textbook content.",
                "sources": [],
                "confidence": 0.0
            }

    def query(self, question: str, context: Optional[str] = None, user_id: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query through the RAG pipeline.

        Args:
            question: The user's question
            context: Additional context provided by the user (e.g., selected text)
            user_id: User identifier for tracking
            session_id: Session identifier for conversation history

        Returns:
            Complete response with answer, sources, and metadata
        """
        try:
            # Combine the question with any provided context
            full_query = question
            if context:
                full_query = f"Question: {question}\nContext: {context}"

            # Retrieve relevant context from textbook content
            context_chunks = self.retrieve_context(full_query)

            # Generate response based on retrieved context
            response_data = self.generate_response(full_query, context_chunks, user_id)

            # Create AIQuery record in the database
            ai_query = AIQuery(
                user_id=user_id,
                question=question,
                context=context,
                session_id=session_id,
                timestamp=datetime.now()
            )
            db_service.create_ai_query(ai_query)

            # Create AIResponse record in the database
            ai_response = AIResponse(
                query_id=ai_query.id,
                answer=response_data["answer"],
                sources=response_data["sources"],
                confidence=response_data["confidence"],
                timestamp=datetime.now()
            )
            db_service.create_ai_response(ai_response)

            # Return the complete response
            return {
                "id": str(ai_response.id),
                "queryId": str(ai_query.id),
                "answer": response_data["answer"],
                "sources": response_data["sources"],
                "confidence": response_data["confidence"],
                "timestamp": ai_response.timestamp.isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing RAG query for question '{question}': {e}")
            return {
                "id": None,
                "queryId": None,
                "answer": "I'm sorry, I encountered an error processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }

# Global instance of the RAG service
rag_service = RagService()