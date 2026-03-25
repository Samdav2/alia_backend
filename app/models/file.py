from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from datetime import datetime
import uuid
from app.database import Base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, func

class File(Base, table=True):
    __tablename__ = "files"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    filename: str = Field(nullable=False)
    original_filename: str = Field(nullable=False)
    file_path: str = Field(nullable=False)
    file_type: str = Field(nullable=False)
    file_size: int = Field(nullable=False)
    mime_type: Optional[str] = Field(default=None)

    # File metadata
    alt_text: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)

    # Context associations
    course_id: Optional[uuid.UUID] = Field(default=None)
    module_id: Optional[uuid.UUID] = Field(default=None)
    topic_id: Optional[uuid.UUID] = Field(default=None)
    context: str = Field(nullable=False, default='general')  # 'course', 'module', 'topic', 'general'

    # Upload info
    uploaded_by: Optional[uuid.UUID] = Field(default=None)  # user_id
    is_public: bool = Field(default=False)

    # File processing status
    status: str = Field(default='completed')  # 'uploading', 'processing', 'completed', 'failed'

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
