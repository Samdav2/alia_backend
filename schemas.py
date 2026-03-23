from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

class UserPreferences(BaseModel):
    dyslexia_mode: bool = False
    high_contrast: bool = False
    audio_speed: float = 1.0
    voice_nav_active: bool = False

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    preferences: Dict[str, Any]

    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    raw_content: str

class CourseCreate(CourseBase):
    lecturer_id: int

class Course(CourseBase):
    id: int
    lecturer_id: int

    class Config:
        from_attributes = True

class AnalyticsBase(BaseModel):
    student_id: int
    course_id: int
    engagement_score: int

class Analytics(AnalyticsBase):
    id: int

    class Config:
        from_attributes = True

class SummarizeRequest(BaseModel):
    text: str

class AssessmentRequest(BaseModel):
    course_id: int
    student_id: int
    current_score: int
