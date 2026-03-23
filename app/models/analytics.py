"""
Analytics and accessibility usage models
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
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


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"))
    
    # Performance metrics
    total_time_spent = Column(Integer, default=0)  # in minutes
    courses_completed = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    streak_days = Column(Integer, default=0)
    
    # Weekly activity data
    weekly_activity = Column(JSON, default=[])
    
    # Course-specific progress
    course_progress = Column(JSON, default=[])
    
    # Timestamps
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analytics")


class AccessibilityUsage(Base):
    __tablename__ = "accessibility_usage"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"))
    
    # Feature usage counters
    bionic_reading_usage = Column(Integer, default=0)
    voice_navigation_usage = Column(Integer, default=0)
    text_to_speech_usage = Column(Integer, default=0)
    high_contrast_usage = Column(Integer, default=0)
    
    # Accessibility score
    accessibility_score = Column(Float, default=0.0)
    
    # Recommendations
    recommendations = Column(JSON, default=[])
    
    # Timestamps
    date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="accessibility_usage")