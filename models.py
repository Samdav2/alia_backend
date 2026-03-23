from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum

class UserRole(str, enum.Enum):
    STUDENT = "Student"
    LECTURER = "Lecturer"
    ADMIN = "Admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    preferences = Column(JSON, default={
        "dyslexia_mode": False,
        "high_contrast": False,
        "audio_speed": 1.0,
        "voice_nav_active": False
    })

    courses = relationship("Course", back_populates="lecturer")
    analytics = relationship("Analytics", back_populates="student")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    raw_content = Column(Text)
    lecturer_id = Column(Integer, ForeignKey("users.id"))

    lecturer = relationship("User", back_populates="courses")
    analytics = relationship("Analytics", back_populates="course")

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    engagement_score = Column(Integer, default=0)

    student = relationship("User", back_populates="analytics")
    course = relationship("Course", back_populates="analytics")
