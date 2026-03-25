from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid
from app.database import Base
from sqlalchemy import Column, String, Text, ForeignKey, Boolean, DateTime, func

if TYPE_CHECKING:
    from .user import User

class Announcement(Base, table=True):
    __tablename__ = "announcements"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    title: str = Field(nullable=False)
    content: str = Field(sa_column=Column(Text, nullable=False))
    author_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    target_audience: str = Field(default="all")  # all, students, lecturers, department
    priority: str = Field(default="normal")  # low, normal, high, urgent
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = Field(
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
    author: Optional["User"] = Relationship()
