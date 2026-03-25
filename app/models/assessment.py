from __future__ import annotations
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional, Any, Dict
from datetime import datetime
import uuid
from app.database import Base
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime, JSON, Integer, Float, func

class Quiz(Base, table=True):
    __tablename__ = "quizzes"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    topic_id: uuid.UUID = Field(foreign_key="topics.id")
    time_limit: Optional[int] = Field(default=None)  # in minutes
    passing_score: float = Field(default=70.0)
    max_attempts: int = Field(default=3)
    is_active: bool = Field(default=True)
    questions: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))  # List of question objects

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
    topic: Optional["Topic"] = Relationship()
    attempts: List["QuizAttempt"] = Relationship(back_populates="quiz")

class QuizAttempt(Base, table=True):
    __tablename__ = "quiz_attempts"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    quiz_id: uuid.UUID = Field(foreign_key="quizzes.id")
    user_id: uuid.UUID = Field(foreign_key="users.id")
    score: Optional[float] = Field(default=None)
    answers: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))  # User's answers
    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    time_taken: Optional[int] = Field(default=None)  # in seconds

    # Relationships
    quiz: "Quiz" = Relationship(back_populates="attempts")
    user: "User" = Relationship()
