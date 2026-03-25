from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import enum
import uuid
from app.database import Base
from sqlalchemy import Column, JSON, Enum, DateTime, func, Text, String

class UserRole(str, enum.Enum):
    STUDENT = "student"
    LECTURER = "lecturer"
    ADMIN = "admin"

class User(Base, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    full_name: str = Field(nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    role: UserRole = Field(default=UserRole.STUDENT, sa_column=Column(Enum(UserRole)))
    department: Optional[str] = Field(default=None)
    student_id: Optional[str] = Field(default=None, unique=True)
    is_active: bool = Field(default=True)

    # Preferences
    preferences: Dict[str, Any] = Field(
        default={
            "language": "English",
            "accessibility": {
                "bionicReading": False,
                "dyslexiaFont": False,
                "highContrast": "none",
                "voiceNavigation": False
            }
        },
        sa_column=Column(JSON)
    )

    # Disability information
    disability_info: Dict[str, Any] = Field(
        default={
            "hasDisability": False,
            "disabilityType": [],
            "assistiveTechnology": [],
            "accommodationsNeeded": []
        },
        sa_column=Column(JSON)
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
    last_login: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )

    # Relationships
    # Note: Use string forward references for other models to avoid circular imports
    courses_taught: List["Course"] = Relationship(back_populates="instructor")
    enrollments: List["Enrollment"] = Relationship(back_populates="user")
    progress_records: List["Progress"] = Relationship(back_populates="user")
    analytics: List["Analytics"] = Relationship(back_populates="user")
    notifications: List["Notification"] = Relationship(back_populates="user")
    accessibility_usage: List["AccessibilityUsage"] = Relationship(back_populates="user")
