"""
Progress tracking models
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid


# UUID type that works with both SQLite and PostgreSQL
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


class ProgressStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Progress(Base):
    __tablename__ = "progress"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"))
    course_id = Column(GUID(), ForeignKey("courses.id"))
    
    # Progress metrics
    completed_topics = Column(Integer, default=0)
    total_topics = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    time_spent = Column(Integer, default=0)  # in minutes
    current_topic_id = Column(GUID())
    
    # Timestamps
    last_accessed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="progress_records")
    course = relationship("Course", back_populates="progress_records")
    topic_progress = relationship("TopicProgress", back_populates="progress")


class TopicProgress(Base):
    __tablename__ = "topic_progress"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    progress_id = Column(GUID(), ForeignKey("progress.id"))
    topic_id = Column(GUID(), ForeignKey("topics.id"))
    
    # Progress details
    status = Column(String, default=ProgressStatus.NOT_STARTED)
    time_spent = Column(Integer, default=0)  # in minutes
    score = Column(Float, default=0.0)
    completed_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    progress = relationship("Progress", back_populates="topic_progress")
    topic = relationship("Topic", back_populates="topic_progress")