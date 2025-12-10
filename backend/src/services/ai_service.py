"""
AI Service

This service interfaces with OpenAI API or local models to generate responses
based on retrieved context from the RAG system.
"""

from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        """
        Initialize the AI service with OpenAI client.
        Falls back to a simple mock implementation if API key is not available.
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.use_mock = False

        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                # Test the client connection
                self.client.models.list()
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.use_mock = True
        else:
            logger.warning("OPENAI_API_KEY not found, using mock AI service")
            self.use_mock = True

    def generate_response(self, query: str, context: List[Dict[str, Any]], user_id: Optional[str] = None) -> str:
        """
        Generate an AI response based on the query and context.

        Args:
            query: User's question
            context: List of relevant context chunks
            user_id: Optional user ID

        Returns:
            Generated response string
        """
        if self.use_mock:
            return self._generate_mock_response(query, context)

        try:
            # Format the context for the prompt
            context_text = "\n\n".join([
                f"Chapter: {chunk['chapterTitle']}\nSection: {chunk['section']}\nContent: {chunk['content'][:500]}..."
                for chunk in context
            ])

            # Create the prompt
            prompt = f"""
            You are an AI assistant for a textbook on Physical AI and Humanoid Robotics.
            Answer the user's question based only on the provided textbook content.

            Context from textbook:
            {context_text}

            User's question: {query}

            Please provide a helpful answer based only on the textbook content provided above.
            If the question cannot be answered based on the provided content, politely explain that the information is not in the textbook.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant for a textbook on Physical AI and Humanoid Robotics. Answer questions based only on the provided textbook content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            # Fall back to mock response if there's an error
            return self._generate_mock_response(query, context)

    def _generate_mock_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """
        Generate a mock response when OpenAI API is not available.

        Args:
            query: User's question
            context: List of relevant context chunks

        Returns:
            Mock response string
        """
        if not context:
            return f"Based on the textbook content, I can provide information about: {query}. However, I couldn't find specific relevant content in the textbook to answer your question in detail."

        # Combine context to form a response
        context_preview = " ".join([chunk['content'][:200] for chunk in context[:2]])  # Take first 2 chunks, first 200 chars each
        return f"Based on the textbook content, I can provide information about: {query}. Here's what the textbook says: {context_preview}..."

    def validate_answer_relevance(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        """
        Validate if the generated answer is relevant to the question and based on the context.

        Args:
            question: Original question
            answer: Generated answer
            context: Context used to generate the answer

        Returns:
            Validation result with relevance score and reason
        """
        if self.use_mock:
            # Simple mock validation
            question_lower = question.lower()
            answer_lower = answer.lower()

            # Check if answer contains keywords from question
            question_words = question_lower.split()
            found_words = sum(1 for word in question_words if word in answer_lower)
            relevance_score = min(1.0, found_words / max(len(question_words), 1))

            if relevance_score > 0.5:
                return {
                    "canAnswer": True,
                    "reason": "Answer contains relevant keywords from the question",
                    "relevanceScore": relevance_score
                }
            else:
                return {
                    "canAnswer": False,
                    "reason": "Answer doesn't seem to address the question",
                    "relevanceScore": relevance_score
                }

        try:
            # Create validation prompt
            validation_prompt = f"""
            You are evaluating if an AI response is relevant to a user's question and based on the provided context.

            Question: {question}

            Answer: {answer}

            Context: {context}

            Please evaluate:
            1. Does the answer address the question?
            2. Is the answer based on the provided context?
            3. Rate the relevance on a scale of 0 to 1.

            Respond in JSON format with keys: canAnswer (boolean), reason (string), relevanceScore (float between 0 and 1).
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an evaluator for AI responses. Respond with a JSON object containing canAnswer, reason, and relevanceScore."},
                    {"role": "user", "content": validation_prompt}
                ],
                max_tokens=200,
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            # Parse the JSON response
            import json
            validation_result = json.loads(response.choices[0].message.content.strip())
            return validation_result

        except Exception as e:
            logger.error(f"Error validating answer relevance: {e}")
            # Fall back to mock validation
            question_lower = question.lower()
            answer_lower = answer.lower()

            question_words = question_lower.split()
            found_words = sum(1 for word in question_words if word in answer_lower)
            relevance_score = min(1.0, found_words / max(len(question_words), 1))

            return {
                "canAnswer": relevance_score > 0.3,
                "reason": f"Mock validation result - relevance score: {relevance_score}",
                "relevanceScore": relevance_score
            }

# Global instance of the AI service
ai_service = AIService()