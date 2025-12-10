from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from ..database_service import Base


class Textbook(Base):
    __tablename__ = "textbooks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, index=True)
    version = Column(String, default="1.0")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    chapters = relationship("Chapter", order_by="Chapter.order", back_populates="textbook")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    textbook_id = Column(UUID(as_uuid=True), ForeignKey("textbooks.id"))
    title = Column(String, index=True)
    content = Column(Text)
    order = Column(Integer)
    word_count = Column(Integer)
    reading_time = Column(String)
    embedding_vector = Column(String)  # Store as JSON string for now
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    textbook = relationship("Textbook", back_populates="chapters")