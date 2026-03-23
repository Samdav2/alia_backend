"""
Assessment and Quiz models
"""
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime, JSON, Integer, Float
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class GUID(TypeDecorator):
    """Platform-independent GUID type."""
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            else:
                return value


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    topic_id = Column(GUID(), ForeignKey("topics.id"))
    time_limit = Column(Integer)  # in minutes
    passing_score = Column(Float, default=70.0)
    max_attempts = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    questions = Column(JSON, default=[])  # List of question objects
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    quiz_id = Column(GUID(), ForeignKey("quizzes.id"))
    user_id = Column(GUID(), ForeignKey("users.id"))
    score = Column(Float)
    answers = Column(JSON, default={})  # User's answers
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    time_taken = Column(Integer)  # in seconds
