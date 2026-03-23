"""
File model for file management
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
from app.models.base import GUID
import uuid


class File(Base):
    __tablename__ = "files"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String)
    
    # File metadata
    alt_text = Column(String)
    description = Column(String)
    
    # Context associations - NEW
    course_id = Column(GUID(), nullable=True)  # References courses.id
    module_id = Column(GUID(), nullable=True)  # References modules.id
    topic_id = Column(GUID(), nullable=True)   # References topics.id
    context = Column(String, nullable=False, default='general')  # 'course', 'module', 'topic', 'general'
    
    # Upload info
    uploaded_by = Column(GUID())  # user_id
    is_public = Column(Boolean, default=False)
    
    # File processing status - NEW
    status = Column(String, default='completed')  # 'uploading', 'processing', 'completed', 'failed'
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
