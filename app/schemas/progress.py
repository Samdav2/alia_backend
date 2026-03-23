"""
Progress tracking schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TopicProgressUpdate(BaseModel):
    status: str  # not_started, in_progress, completed
    time_spent: Optional[int] = 0
    score: Optional[float] = 0.0


class TopicProgressResponse(BaseModel):
    topic_id: str
    status: str
    time_spent: int
    score: float
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProgressResponse(BaseModel):
    course_id: str
    user_id: str
    completed_topics: int
    total_topics: int
    completion_percentage: float
    time_spent: int
    current_topic: Optional[str] = None
    last_accessed_at: Optional[datetime] = None
    topic_progress: List[TopicProgressResponse] = []

    class Config:
        from_attributes = True