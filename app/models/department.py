from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from datetime import datetime
import uuid
from app.database import Base
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, func

class Department(Base, table=True):
    __tablename__ = "departments"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    name: str = Field(unique=True, nullable=False, index=True)
    code: str = Field(unique=True, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    head_of_department: Optional[str] = Field(default=None)
    contact_email: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    student_count: int = Field(default=0)
    course_count: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )
