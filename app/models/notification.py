from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import enum
import uuid
from app.database import Base
from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Text, Enum, func

if TYPE_CHECKING:
    from .user import User

class NotificationType(str, enum.Enum):
    COURSE_UPDATE = "course_update"
    ASSIGNMENT_DUE = "assignment_due"
    ACHIEVEMENT = "achievement"
    SYSTEM = "system"

class Notification(Base, table=True):
    __tablename__ = "notifications"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id")

    # Notification details
    # Use sa_column for Enum to ensure it's handled correctly by SQLAlchemy/PostgreSQL
    type: NotificationType = Field(
        default=NotificationType.SYSTEM,
        sa_column=Column(Enum(NotificationType))
    )
    title: str = Field(nullable=False)
    message: str = Field(sa_column=Column(Text, nullable=False))
    action_url: Optional[str] = Field(default=None)
    is_read: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    read_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )

    # Relationships
    user: "User" = Relationship(back_populates="notifications")
