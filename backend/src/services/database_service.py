from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from src.utils.config import settings
import logging

logger = logging.getLogger(__name__)

# Database setup
if settings.neon_db_url:
    engine = create_engine(settings.neon_db_url)
else:
    # Fallback to SQLite for development if no Neon DB URL provided
    engine = create_engine("sqlite:///./textbook.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class Textbook(Base):
    __tablename__ = "textbooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True)
    version = Column(String, default="1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = Column(UUID(as_uuid=True), ForeignKey("textbooks.id"))
    title = Column(String, index=True)
    content = Column(Text)
    order = Column(Integer, index=True)  # Added index for ordering
    word_count = Column(Integer)
    reading_time = Column(String)
    embedding_vector = Column(String)  # Store as JSON string for now
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), index=True)

    # Relationship
    textbook = relationship("Textbook", back_populates="chapters")


class AIQuery(Base):
    __tablename__ = "ai_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True)  # Can be session ID if no user auth
    question = Column(Text)
    context = Column(Text)
    session_id = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class AIResponse(Base):
    __tablename__ = "ai_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("ai_queries.id"))
    answer = Column(Text)
    sources = Column(Text)  # JSON string of sources
    confidence = Column(Integer)  # 0-100
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    query = relationship("AIQuery", back_populates="response")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    preferences = Column(Text)  # JSON string of user preferences
    is_active = Column(Integer, default=1)  # Boolean as integer for SQLite compatibility


# Add relationships
Textbook.chapters = relationship("Chapter", order_by=Chapter.order, back_populates="textbook")
AIQuery.response = relationship("AIResponse", back_populates="query")


# Create tables
def init_db():
    """Initialize the database and create tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database service class to handle database operations
class DatabaseService:
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def get_db(self):
        """Dependency to get DB session"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_user_session(self, user_session):
        """Create a new user session"""
        db = self.SessionLocal()
        try:
            db.add(user_session)
            db.commit()
            db.refresh(user_session)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_user_session(self, session_id):
        """Retrieve a user session by ID"""
        db = self.SessionLocal()
        try:
            return db.query(UserSession).filter(UserSession.id == session_id).first()
        finally:
            db.close()

    def update_user_session_activity(self, session_id):
        """Update the last activity timestamp for a session"""
        db = self.SessionLocal()
        try:
            user_session = db.query(UserSession).filter(UserSession.id == session_id).first()
            if user_session:
                user_session.last_activity = func.now()
                db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def deactivate_user_session(self, session_id):
        """End a user session by marking it as inactive"""
        db = self.SessionLocal()
        try:
            user_session = db.query(UserSession).filter(UserSession.id == session_id).first()
            if user_session:
                user_session.is_active = 0
                db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def create_ai_query(self, ai_query):
        """Create a new AI query record"""
        db = self.SessionLocal()
        try:
            db.add(ai_query)
            db.commit()
            db.refresh(ai_query)
            return ai_query
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def create_ai_response(self, ai_response):
        """Create a new AI response record"""
        db = self.SessionLocal()
        try:
            db.add(ai_response)
            db.commit()
            db.refresh(ai_response)
            return ai_response
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_ai_queries_by_session(self, session_id):
        """Get all AI queries for a specific session"""
        db = self.SessionLocal()
        try:
            return db.query(AIQuery).filter(AIQuery.session_id == session_id).all()
        finally:
            db.close()

    def get_ai_response_by_query_id(self, query_id):
        """Get AI response by query ID"""
        db = self.SessionLocal()
        try:
            return db.query(AIResponse).filter(AIResponse.query_id == query_id).first()
        finally:
            db.close()

    def get_chapters(self, limit: int = 10, offset: int = 0):
        """Get chapters with pagination"""
        db = self.SessionLocal()
        try:
            return db.query(Chapter).order_by(Chapter.order).offset(offset).limit(limit).all()
        finally:
            db.close()

    def get_chapter_by_id(self, chapter_id):
        """Get chapter by ID"""
        db = self.SessionLocal()
        try:
            return db.query(Chapter).filter(Chapter.id == chapter_id).first()
        finally:
            db.close()

    def get_chapter_toc(self, chapter_id):
        """Get table of contents for a chapter"""
        # This would return the structure of the chapter
        # For now, return basic information
        chapter = self.get_chapter_by_id(chapter_id)
        if chapter:
            # In a real implementation, this would parse the content to extract sections
            return {
                "chapterId": str(chapter.id),
                "title": chapter.title,
                "sections": []  # Placeholder - would be populated by parsing content
            }
        return None


# Global instance of the database service
db_service = DatabaseService()

# Initialize database on startup
init_db()