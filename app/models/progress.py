from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional, Any, Dict, TYPE_CHECKING
from datetime import datetime
import enum
import uuid
from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON, Enum, func

if TYPE_CHECKING:
    from .user import User
    from .course import Course, Topic

class ProgressStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Progress(Base, table=True):
    __tablename__ = "progress"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id")
    course_id: uuid.UUID = Field(foreign_key="courses.id")

    # Progress metrics
    completed_topics: int = Field(default=0)
    total_topics: int = Field(default=0)
    completion_percentage: float = Field(default=0.0)
    time_spent: int = Field(default=0)  # in minutes
    current_topic_id: Optional[uuid.UUID] = Field(default=None)

    # Timestamps
    last_accessed_at: Optional[datetime] = Field(
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
    user: "User" = Relationship(back_populates="progress_records")
    course: "Course" = Relationship(back_populates="progress_records")
    topic_progress: List["TopicProgress"] = Relationship(back_populates="progress")

class TopicProgress(Base, table=True):
    __tablename__ = "topic_progress"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    progress_id: uuid.UUID = Field(foreign_key="progress.id")
    topic_id: uuid.UUID = Field(foreign_key="topics.id")

    # Progress details
    status: ProgressStatus = Field(
        default=ProgressStatus.NOT_STARTED,
        sa_column=Column(Enum(ProgressStatus))
    )
    time_spent: int = Field(default=0)  # in minutes
    score: float = Field(default=0.0)
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )

    # Relationships
    progress: "Progress" = Relationship(back_populates="topic_progress")
    topic: "Topic" = Relationship(back_populates="topic_progress")
