"""
User schemas
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class AccessibilityPreferences(BaseModel):
    bionic_reading: bool = False
    dyslexia_font: bool = False
    high_contrast: str = "none"
    voice_navigation: bool = False


class UserPreferences(BaseModel):
    language: str = "English"
    accessibility: AccessibilityPreferences = AccessibilityPreferences()


class DisabilityInfo(BaseModel):
    has_disability: bool = False
    disability_type: List[str] = []
    assistive_technology: List[str] = []
    accommodations_needed: List[str] = []


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str
    department: Optional[str] = None
    student_id: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    disability_info: Optional[DisabilityInfo] = None


class UserResponse(UserBase):
    id: str  # UUID as string
    is_active: bool
    preferences: UserPreferences
    disability_info: Optional[DisabilityInfo] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    id: str  # UUID as string
    full_name: str
    email: str
    role: str
    department: Optional[str] = None
    is_active: bool
    created_at: datetime

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True