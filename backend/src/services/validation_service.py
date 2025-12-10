"""
Validation Service

This service ensures RAG integrity by validating that AI responses are
based only on textbook content and not external knowledge.
"""

from typing import Dict, Any, List
import logging
from src.services.ai_service import ai_service
from src.services.rag_service import rag_service

logger = logging.getLogger(__name__)

class ValidationService:
    def __init__(self):
        self.ai_service = ai_service
        self.rag_service = rag_service

    def validate_content_relevance(self, question: str, context: str) -> Dict[str, Any]:
        """
        Validate if a question can be answered based on textbook content.

        Args:
            question: The user's question
            context: The context to validate against

        Returns:
            Validation result with relevance score and reason
        """
        try:
            # Use the AI service's validation method if available
            if hasattr(self.ai_service, 'validate_answer_relevance'):
                # Create a mock answer to validate against
                mock_answer = f"Based on the textbook content, I can provide information about: {question}"
                return self.ai_service.validate_answer_relevance(question, mock_answer, context)

            # Fallback validation
            question_lower = question.lower()
            context_lower = context.lower()

            # Check for keyword overlap between question and context
            question_words = set(question_lower.split())
            context_words = set(context_lower.split())

            # Calculate overlap
            common_words = question_words.intersection(context_words)
            overlap_ratio = len(common_words) / max(len(question_words), 1)

            if overlap_ratio > 0.3:  # If more than 30% of question words appear in context
                return {
                    "canAnswer": True,
                    "reason": f"Question contains {len(common_words)} common words with context",
                    "relevanceScore": min(1.0, overlap_ratio)
                }
            else:
                return {
                    "canAnswer": False,
                    "reason": "Question and context have insufficient overlap",
                    "relevanceScore": overlap_ratio
                }
        except Exception as e:
            logger.error(f"Error validating content relevance: {e}")
            return {
                "canAnswer": False,
                "reason": f"Validation error: {str(e)}",
                "relevanceScore": 0.0
            }

    def validate_response_accuracy(self, question: str, answer: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that the AI response is accurate and based on the provided context.

        Args:
            question: Original question
            answer: AI-generated answer
            context: List of context chunks used to generate the answer

        Returns:
            Validation result with accuracy score and feedback
        """
        try:
            # Combine all context content
            context_content = " ".join([chunk.get('content', '') for chunk in context])

            # Use the AI service's validation method if available
            if hasattr(self.ai_service, 'validate_answer_relevance'):
                return self.ai_service.validate_answer_relevance(question, answer, context_content)

            # Fallback validation: check if answer contains information from context
            answer_lower = answer.lower()
            context_lower = context_content.lower()

            # Count how much of the answer is supported by context
            answer_sentences = answer.split('.')
            supported_sentences = 0

            for sentence in answer_sentences:
                if sentence.strip():
                    sentence_lower = sentence.lower()
                    # Check if this sentence appears in context (with some tolerance for variations)
                    if any(word in context_lower for word in sentence_lower.split()[:5]):  # Check first 5 words
                        supported_sentences += 1

            accuracy_score = supported_sentences / max(len(answer_sentences), 1)

            return {
                "accuracyScore": accuracy_score,
                "reason": f"{supported_sentences}/{len(answer_sentences)} sentences in answer are supported by context",
                "isAccurate": accuracy_score > 0.5
            }
        except Exception as e:
            logger.error(f"Error validating response accuracy: {e}")
            return {
                "accuracyScore": 0.0,
                "reason": f"Validation error: {str(e)}",
                "isAccurate": False
            }

    def validate_rag_pipeline(self, question: str, context_chunks: List[Dict[str, Any]], answer: str) -> Dict[str, Any]:
        """
        Validate the entire RAG pipeline for integrity.

        Args:
            question: Original user question
            context_chunks: Context chunks retrieved by the RAG system
            answer: Final answer generated by the AI

        Returns:
            Comprehensive validation result
        """
        try:
            # Validate content relevance
            context_content = " ".join([chunk.get('content', '') for chunk in context_chunks])
            relevance_result = self.validate_content_relevance(question, context_content)

            # Validate response accuracy
            accuracy_result = self.validate_response_accuracy(question, answer, context_chunks)

            # Overall validation
            overall_valid = relevance_result["canAnswer"] and accuracy_result["isAccurate"]

            return {
                "isValid": overall_valid,
                "relevance": relevance_result,
                "accuracy": accuracy_result,
                "message": "RAG pipeline validation passed" if overall_valid else "RAG pipeline validation failed",
                "confidence": (relevance_result.get("relevanceScore", 0) + accuracy_result.get("accuracyScore", 0)) / 2
            }
        except Exception as e:
            logger.error(f"Error validating RAG pipeline: {e}")
            return {
                "isValid": False,
                "relevance": {"canAnswer": False, "reason": f"Validation error: {str(e)}", "relevanceScore": 0.0},
                "accuracy": {"isAccurate": False, "reason": f"Validation error: {str(e)}", "accuracyScore": 0.0},
                "message": f"RAG pipeline validation error: {str(e)}",
                "confidence": 0.0
            }

    def validate_external_knowledge(self, question: str, answer: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that the answer doesn't contain external knowledge not present in context.

        Args:
            question: Original question
            answer: AI-generated answer
            context: Context used to generate the answer

        Returns:
            Validation result for external knowledge detection
        """
        try:
            # Combine all context content
            context_text = " ".join([chunk.get('content', '') for chunk in context])
            context_lower = context_text.lower()

            # Simple check: look for named entities or facts in answer that aren't in context
            answer_sentences = answer.split('.')
            external_content = []

            for sentence in answer_sentences:
                sentence_lower = sentence.lower().strip()
                if sentence_lower and not any(word in context_lower for word in sentence_lower.split()[:3]):
                    # This sentence might contain external information
                    external_content.append(sentence.strip())

            has_external = len(external_content) > 0

            return {
                "hasExternalKnowledge": has_external,
                "externalContent": external_content,
                "isRAGCompliant": not has_external,
                "message": "No external knowledge detected" if not has_external else f"Found potential external content: {external_content[:3]}"  # Limit to first 3
            }
        except Exception as e:
            logger.error(f"Error validating external knowledge: {e}")
            return {
                "hasExternalKnowledge": True,
                "externalContent": [],
                "isRAGCompliant": False,
                "message": f"Validation error: {str(e)}"
            }

# Global instance of the validation service
validation_service = ValidationService()