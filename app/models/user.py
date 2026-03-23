"""
User model and related enums
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Enum, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid


# UUID type that works with both SQLite and PostgreSQL
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """
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


class UserRole(str, enum.Enum):
    STUDENT = "student"
    LECTURER = "lecturer"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    department = Column(String)
    student_id = Column(String, unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Preferences
    preferences = Column(JSON, default={
        "language": "English",
        "accessibility": {
            "bionicReading": False,
            "dyslexiaFont": False,
            "highContrast": "none",
            "voiceNavigation": False
        }
    })
    
    # Disability information
    disability_info = Column(JSON, default={
        "hasDisability": False,
        "disabilityType": [],
        "assistiveTechnology": [],
        "accommodationsNeeded": []
    })
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    courses_taught = relationship("Course", back_populates="instructor")
    enrollments = relationship("Enrollment", back_populates="user")
    progress_records = relationship("Progress", back_populates="user")
    analytics = relationship("Analytics", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    accessibility_usage = relationship("AccessibilityUsage", back_populates="user")