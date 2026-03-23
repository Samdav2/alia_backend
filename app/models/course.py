"""
Course, Module, Topic, and Enrollment models
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.base import GUID
import enum
import uuid


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


class Course(Base):
    __tablename__ = "courses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    department = Column(String, nullable=False)
    level = Column(String, default=CourseLevel.BEGINNER)
    duration = Column(String)  # e.g., "12 weeks"
    tags = Column(JSON, default=[])
    thumbnail = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Instructor
    instructor_id = Column(GUID(), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    instructor = relationship("User", back_populates="courses_taught")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course")
    progress_records = relationship("Progress", back_populates="course")


class Module(Base):
    __tablename__ = "modules"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    order = Column(Integer, nullable=False)
    
    # Course relationship
    course_id = Column(GUID(), ForeignKey("courses.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    topics = relationship("Topic", back_populates="module", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    duration = Column(String)  # e.g., "30 minutes"
    order = Column(Integer, nullable=False)
    content_type = Column(String, default=ContentType.TEXT)
    content = Column(Text)
    media_files = Column(JSON, default=[])
    prerequisites = Column(JSON, default=[])
    learning_objectives = Column(JSON, default=[])
    
    # Module relationship
    module_id = Column(GUID(), ForeignKey("modules.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("Module", back_populates="topics")
    topic_progress = relationship("TopicProgress", back_populates="topic")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(GUID(), ForeignKey("users.id"))
    course_id = Column(GUID(), ForeignKey("courses.id"))
    status = Column(String, default=EnrollmentStatus.ACTIVE)
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now())
    completion_date = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")