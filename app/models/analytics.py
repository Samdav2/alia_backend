from __future__ import annotations
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional, Any, Dict, TYPE_CHECKING
from datetime import datetime
import uuid
from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, Boolean, func

if TYPE_CHECKING:
    from .user import User

class Analytics(Base, table=True):
    __tablename__ = "analytics"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id")

    # Performance metrics
    total_time_spent: int = Field(default=0)  # in minutes
    courses_completed: int = Field(default=0)
    average_score: float = Field(default=0.0)
    streak_days: int = Field(default=0)

    # Weekly activity data
    weekly_activity: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))

    # Course-specific progress
    course_progress: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))

    # Timestamps
    period_start: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    period_end: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

    # Relationships
    user: "User" = Relationship(back_populates="analytics")

class AccessibilityUsage(Base, table=True):
    __tablename__ = "accessibility_usage"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id")

    # Feature usage counters
    bionic_reading_usage: int = Field(default=0)
    voice_navigation_usage: int = Field(default=0)
    text_to_speech_usage: int = Field(default=0)
    high_contrast_usage: int = Field(default=0)

    # Accessibility score
    accessibility_score: float = Field(default=0.0)

    # Recommendations
    recommendations: List[str] = Field(default=[], sa_column=Column(JSON))

    # Timestamps
    date: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

    # Relationships
    user: "User" = Relationship(back_populates="accessibility_usage")
