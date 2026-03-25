from __future__ import annotations
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, Any, Dict, TYPE_CHECKING
from datetime import datetime
import uuid
from app.database import Base
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, JSON, func

if TYPE_CHECKING:
    from .user import User

class AuditLog(Base, table=True):
    __tablename__ = "audit_logs"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.id")
    action: str = Field(nullable=False)  # create, update, delete, login, etc.
    resource_type: str = Field(nullable=False)  # user, course, enrollment, etc.
    resource_id: Optional[str] = Field(default=None)
    details: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), index=True)
    )

    # Relationships
    user: Optional["User"] = Relationship()
