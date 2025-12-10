import uuid
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from src.utils.logging import get_logger
from src.services.database_service import get_db, UserSession
from sqlalchemy.orm import Session


logger = get_logger(__name__)


class SessionManager:
    def __init__(self):
        self.session_timeout = 3600  # 1 hour in seconds
        self.active_sessions = {}  # In-memory session store (use Redis in production)

    def create_session(self, user_id: Optional[str] = None, preferences: Optional[Dict] = None) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())

        # Create session data
        session_data = {
            'id': session_id,
            'user_id': user_id or f"anonymous_{session_id[:8]}",
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'preferences': preferences or {},
            'expires_at': datetime.utcnow() + timedelta(seconds=self.session_timeout)
        }

        # Store in memory (in production, use Redis or database)
        self.active_sessions[session_id] = session_data

        logger.info(f"Created new session: {session_id} for user: {session_data['user_id']}")

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by session ID"""
        if session_id not in self.active_sessions:
            return None

        session_data = self.active_sessions[session_id]

        # Check if session has expired
        if datetime.utcnow() > session_data['expires_at']:
            self.delete_session(session_id)
            return None

        # Update last activity
        session_data['last_activity'] = datetime.utcnow()
        return session_data

    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session data"""
        if session_id not in self.active_sessions:
            return False

        session_data = self.active_sessions[session_id]

        # Update provided fields
        for key, value in kwargs.items():
            if key in session_data:
                session_data[key] = value

        session_data['last_activity'] = datetime.utcnow()
        return True

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.utcnow()
        expired_sessions = [
            sid for sid, data in self.active_sessions.items()
            if current_time > data['expires_at']
        ]

        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")

    def is_valid_session(self, session_id: str) -> bool:
        """Check if session is valid and not expired"""
        return self.get_session(session_id) is not None


class AuthService:
    def __init__(self):
        self.session_manager = SessionManager()
        self.secret_key = "default-secret-key-change-in-production"  # Should be in config

    def generate_session_token(self, session_id: str) -> str:
        """Generate a signed token for the session"""
        # In a real implementation, use JWT or similar
        # For now, we'll use a simple hash-based approach
        token_data = f"{session_id}:{int(time.time())}"
        signature = hashlib.sha256(f"{token_data}:{self.secret_key}".encode()).hexdigest()
        return f"{token_data}:{signature}"

    def verify_session_token(self, token: str) -> Optional[str]:
        """Verify a session token and return session_id if valid"""
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return None

            session_id, timestamp, signature = parts
            expected_timestamp = int(timestamp)

            # Check if token is expired (valid for 1 hour)
            if time.time() - expected_timestamp > 3600:
                return None

            # Verify signature
            expected_token_data = f"{session_id}:{timestamp}"
            expected_signature = hashlib.sha256(f"{expected_token_data}:{self.secret_key}".encode()).hexdigest()

            if signature == expected_signature:
                return session_id
        except Exception as e:
            logger.error(f"Error verifying token: {e}")

        return None

    def create_user_session(self, user_id: Optional[str] = None, preferences: Optional[Dict] = None) -> Dict[str, str]:
        """Create a new user session with token"""
        session_id = self.session_manager.create_session(user_id, preferences)
        token = self.generate_session_token(session_id)

        return {
            'session_id': session_id,
            'token': token
        }

    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a session token and return session data"""
        session_id = self.verify_session_token(token)
        if not session_id:
            return None

        return self.session_manager.get_session(session_id)


# Global instance
auth_service = AuthService()