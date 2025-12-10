"""
Session Management Service

This service handles user session management for chat conversations,
including session creation, tracking, and history management.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import json
from ..models.user_session import UserSession
from ..models.ai_query import AIQuery, AIResponse
from ..database_service import db_service

class SessionService:
    def __init__(self):
        pass

    def create_session(self, user_id: Optional[str] = None, preferences: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new user session for chat conversations.

        Args:
            user_id: Optional user identifier
            preferences: Optional user preferences

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        user_session = UserSession(
            id=session_id,
            user_id=user_id,
            preferences=json.dumps(preferences) if preferences else None,
            is_active=1
        )

        db_service.create_user_session(user_session)
        return session_id

    def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Retrieve a user session by ID.

        Args:
            session_id: Session identifier

        Returns:
            UserSession object or None if not found
        """
        return db_service.get_user_session(session_id)

    def update_session_activity(self, session_id: str):
        """
        Update the last activity timestamp for a session.

        Args:
            session_id: Session identifier
        """
        db_service.update_user_session_activity(session_id)

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a specific session.

        Args:
            session_id: Session identifier

        Returns:
            List of conversation history items
        """
        # Get all AI queries for this session
        queries = db_service.get_ai_queries_by_session(session_id)

        history = []
        for query in queries:
            # Get the corresponding response for each query
            response = db_service.get_ai_response_by_query_id(query.id)

            history_item = {
                "id": str(query.id),
                "question": query.question,
                "timestamp": query.timestamp.isoformat() if query.timestamp else None,
                "type": "query"
            }
            history.append(history_item)

            if response:
                response_item = {
                    "id": str(response.id),
                    "answer": response.answer,
                    "timestamp": response.timestamp.isoformat() if response.timestamp else None,
                    "type": "response"
                }
                history.append(response_item)

        # Sort by timestamp
        history.sort(key=lambda x: x['timestamp'])
        return history

    def update_session_preferences(self, session_id: str, preferences: str):
        """
        Update user session preferences.

        Args:
            session_id: Session identifier
            preferences: JSON string of preferences
        """
        from sqlalchemy.orm import sessionmaker
        from src.services.database_service import engine

        # Get the session from the database
        Session = sessionmaker(bind=engine)
        db_session = Session()

        try:
            user_session = db_session.query(UserSession).filter(UserSession.id == session_id).first()
            if user_session:
                user_session.preferences = preferences
                db_session.commit()
        finally:
            db_session.close()

    def end_session(self, session_id: str):
        """
        End a user session by marking it as inactive.

        Args:
            session_id: Session identifier
        """
        db_service.deactivate_user_session(session_id)

    def validate_session(self, session_id: str) -> bool:
        """
        Validate if a session is active and exists.

        Args:
            session_id: Session identifier

        Returns:
            True if session is valid and active, False otherwise
        """
        session = self.get_session(session_id)
        return session is not None and session.is_active == 1

# Global instance of the session service
session_service = SessionService()