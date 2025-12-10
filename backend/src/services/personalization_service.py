"""
Personalization Service
This module provides functionality for personalizing textbook content based on user preferences.
"""
import json
from typing import Dict, Optional, Any
from datetime import datetime
from src.utils.logging import get_logger
from src.services.session_service import session_service


logger = get_logger(__name__)


class PersonalizationService:
    """
    Service to handle content personalization
    """
    def __init__(self):
        self.personalization_rules = {
            "beginner": {
                "simplify_content": True,
                "add_examples": True,
                "reduce_complexity": True
            },
            "intermediate": {
                "simplify_content": False,
                "add_examples": True,
                "reduce_complexity": False
            },
            "advanced": {
                "simplify_content": False,
                "add_examples": False,
                "reduce_complexity": False
            }
        }
        logger.info("Personalization service initialized")

    def get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """
        Get user preferences from session

        Args:
            session_id: User session ID

        Returns:
            Dictionary of user preferences
        """
        # Get user session
        user_session = session_service.get_session(session_id)
        if not user_session or not user_session.preferences:
            # Return default preferences
            return {
                "language": "en",
                "reading_level": "intermediate",
                "learning_style": "visual",
                "personalization_enabled": True
            }

        try:
            preferences = json.loads(user_session.preferences)
            return preferences
        except (json.JSONDecodeError, TypeError):
            # If preferences are not valid JSON, return defaults
            return {
                "language": "en",
                "reading_level": "intermediate",
                "learning_style": "visual",
                "personalization_enabled": True
            }

    def set_user_preferences(self, session_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Set user preferences in session

        Args:
            session_id: User session ID
            preferences: Dictionary of user preferences

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update session with new preferences
            session_service.update_session_preferences(session_id, json.dumps(preferences))
            logger.info(f"Updated preferences for session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating preferences for session {session_id}: {e}")
            return False

    def personalize_content(self, content: str, user_preferences: Dict[str, Any]) -> str:
        """
        Personalize content based on user preferences

        Args:
            content: Original content to personalize
            user_preferences: User preferences dictionary

        Returns:
            Personalized content
        """
        logger.info(f"Personalizing content for user with reading level: {user_preferences.get('reading_level', 'intermediate')}")

        personalized_content = content

        # Apply personalization based on reading level
        reading_level = user_preferences.get("reading_level", "intermediate")
        if reading_level in self.personalization_rules:
            rules = self.personalization_rules[reading_level]

            if rules.get("simplify_content"):
                # Simplify content for beginners
                personalized_content = self._simplify_content(personalized_content)

            if rules.get("add_examples"):
                # Add examples for intermediate learners
                personalized_content = self._add_examples(personalized_content)

            if rules.get("reduce_complexity"):
                # Reduce complexity for beginners
                personalized_content = self._reduce_complexity(personalized_content)

        # Apply other personalization features based on learning style
        learning_style = user_preferences.get("learning_style", "visual")
        if learning_style == "visual":
            # Add more visual elements or structure for visual learners
            personalized_content = self._enhance_visual_elements(personalized_content)

        return personalized_content

    def _simplify_content(self, content: str) -> str:
        """
        Simplify content for beginner learners
        """
        # In a real implementation, this would use NLP techniques to simplify text
        # For now, we'll just add a note that content has been simplified
        return f"[SIMPLIFIED CONTENT] {content} [END SIMPLIFIED CONTENT]"

    def _add_examples(self, content: str) -> str:
        """
        Add examples to content for intermediate learners
        """
        # In a real implementation, this would add relevant examples
        # For now, we'll just add a placeholder
        return f"{content}\n\n[ADDITIONAL EXAMPLES FOR INTERMEDIATE LEARNERS]\n[END EXAMPLES]"

    def _reduce_complexity(self, content: str) -> str:
        """
        Reduce complexity of content for beginner learners
        """
        # In a real implementation, this would break down complex concepts
        # For now, we'll just add a note
        return f"[COMPLEXITY REDUCED] {content} [END COMPLEXITY REDUCTION]"

    def _enhance_visual_elements(self, content: str) -> str:
        """
        Enhance visual elements for visual learners
        """
        # In a real implementation, this might add more structure or formatting
        # For now, we'll just add a note
        return f"<!-- VISUAL ELEMENTS ENHANCED -->\n{content}\n<!-- END VISUAL ENHANCEMENT -->"


# Global instance
personalization_service = PersonalizationService()