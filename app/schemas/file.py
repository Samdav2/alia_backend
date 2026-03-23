"""
File management schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime
import uuid


class FileUploadRequest(BaseModel):
    """Request schema for file upload with context"""
    file_type: Optional[Literal['thumbnail', 'video', 'document', 'resource', 'image']] = 'document'
    course_id: Optional[str] = None
    module_id: Optional[str] = None
    topic_id: Optional[str] = None
    context: Literal['course', 'module', 'topic', 'general'] = 'general'
    alt_text: Optional[str] = None
    description: Optional[str] = None


class FileUploadResponse(BaseModel):
    """Response schema for file upload"""
    file_id: str
    filename: str
    original_filename: str
    url: str
    type: str
    size: int
    context: str
    course_id: Optional[str] = None
    module_id: Optional[str] = None
    topic_id: Optional[str] = None
    uploaded_at: datetime
    uploaded_by: str


class FileResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    mime_type: Optional[str] = None
    alt_text: Optional[str] = None
    description: Optional[str] = None
    is_public: bool
    
    # Context fields
    course_id: Optional[str] = None
    module_id: Optional[str] = None
    topic_id: Optional[str] = None
    context: str
    status: str
    uploaded_by: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None

    @field_validator('id', 'course_id', 'module_id', 'topic_id', 'uploaded_by', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v):
        if v is None:
            return v
        if isinstance(v, uuid.UUID):
            return str(v)
        return v

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    """Response for listing files with context"""
    files: list[FileResponse]
    total: int
    context: str
    context_id: Optional[str] = None
