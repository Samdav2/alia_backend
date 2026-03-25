from __future__ import annotations
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional, Any, Dict, TYPE_CHECKING
from datetime import datetime
import enum
import uuid
from app.database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON, Float, Enum, func

if TYPE_CHECKING:
    from .user import User
    from .progress import Progress
    from .assessment import Quiz

class CourseLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class EnrollmentStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"

class ContentType(str, enum.Enum):
    TEXT = "text"
    VIDEO = "video"
    INTERACTIVE = "interactive"

class Course(Base, table=True):
    __tablename__ = "courses"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    code: str = Field(unique=True, index=True, nullable=False)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    department: str = Field(nullable=False)
    level: CourseLevel = Field(
        default=CourseLevel.BEGINNER,
        sa_column=Column(Enum(CourseLevel))
    )
    duration: Optional[str] = Field(default=None)  # e.g., "12 weeks"
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    thumbnail: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)

    # Instructor
    instructor_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")

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
    instructor: Optional[User] = Relationship(back_populates="courses_taught")
    modules: List[Module] = Relationship(back_populates="course", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    enrollments: List[Enrollment] = Relationship(back_populates="course")
    progress_records: List[Progress] = Relationship(back_populates="course")

class Module(Base, table=True):
    __tablename__ = "modules"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    order: int = Field(nullable=False)

    # Course relationship
    course_id: uuid.UUID = Field(foreign_key="courses.id")

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
    course: "Course" = Relationship(back_populates="modules")
    topics: List["Topic"] = Relationship(back_populates="module", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class Topic(Base, table=True):
    __tablename__ = "topics"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    duration: Optional[str] = Field(default=None)  # e.g., "30 minutes"
    order: int = Field(nullable=False)
    content_type: str = Field(default=ContentType.TEXT)
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    media_files: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))
    prerequisites: List[str] = Field(default=[], sa_column=Column(JSON))
    learning_objectives: List[str] = Field(default=[], sa_column=Column(JSON))

    # Module relationship
    module_id: uuid.UUID = Field(foreign_key="modules.id")

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
    module: Module = Relationship(back_populates="topics")
    topic_progress: List[TopicProgress] = Relationship(back_populates="topic")
    assessments: List[Quiz] = Relationship(back_populates="topic", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class Enrollment(Base, table=True):
    __tablename__ = "enrollments"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: uuid.UUID = Field(foreign_key="users.id")
    course_id: uuid.UUID = Field(foreign_key="courses.id")
    status: EnrollmentStatus = Field(
        default=EnrollmentStatus.ACTIVE,
        sa_column=Column(Enum(EnrollmentStatus))
    )
    enrollment_date: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    completion_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )

    # Relationships
    user: User = Relationship(back_populates="enrollments")
    course: Course = Relationship(back_populates="enrollments")
