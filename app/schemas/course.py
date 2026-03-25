"""
Course-related schemas
"""
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import uuid


class MediaFile(BaseModel):
    type: str  # image, video, pdf, doc
    url: str
    title: str
    description: Optional[str] = None
    alt_text: Optional[str] = None


class AssessmentQuestion(BaseModel):
    id: str
    question: str
    type: str  # multiple_choice, true_false, short_answer
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class Assessment(BaseModel):
    id: str
    type: str  # quiz, assignment
    title: str
    questions: List[AssessmentQuestion]

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration: Optional[str] = None
    content_type: str = "text"
    content: Optional[str] = None
    media_files: List[MediaFile] = []
    prerequisites: List[str] = []
    learning_objectives: List[str] = []


class TopicCreate(TopicBase):
    order: int
    module_id: str


class TopicResponse(TopicBase):
    id: str
    order: int
    module_id: str
    assessments: List[Assessment] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('id', 'module_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None


class ModuleCreate(ModuleBase):
    order: int
    course_id: str


class ModuleResponse(ModuleBase):
    id: str
    order: int
    course_id: str
    topics: List[TopicResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('id', 'course_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    department: str
    level: str = "beginner"
    duration: Optional[str] = None
    tags: List[str] = []
    thumbnail: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    level: Optional[str] = None
    duration: Optional[str] = None
    tags: Optional[List[str]] = None
    thumbnail: Optional[str] = None


class CourseListResponse(CourseBase):
    id: str
    instructor_id: str
    enrollment_count: int = 0
    rating: float = 0.0
    is_active: bool
    is_enrolled: bool = False
    created_at: datetime

    @field_validator('id', 'instructor_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class CourseDetailResponse(CourseBase):
    id: str
    instructor_id: str
    modules: List[ModuleResponse] = []
    enrollment_count: int = 0
    rating: float = 0.0
    is_active: bool
    is_enrolled: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('id', 'instructor_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class EnrollmentCreate(BaseModel):
    course_id: str


class EnrollmentResponse(BaseModel):
    id: str
    course_id: str
    course: CourseListResponse
    enrollment_date: datetime
    status: str
    completion_date: Optional[datetime] = None

    @field_validator('id', 'course_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True
