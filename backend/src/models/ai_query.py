from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database_service import Base


class AIQuery(Base):
    __tablename__ = "ai_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, index=True)  # Can be session ID if no user auth
    question = Column(Text)
    context = Column(Text)
    session_id = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    response = relationship("AIResponse", back_populates="query")


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