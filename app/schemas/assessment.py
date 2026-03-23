"""
Assessment-related schemas
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class QuestionOption(BaseModel):
    id: str
    text: str


class QuizQuestion(BaseModel):
    id: str
    question: str
    type: str  # multiple_choice, true_false, short_answer
    options: Optional[List[QuestionOption]] = None
    correct_answer: str
    explanation: Optional[str] = None
    points: float = 1.0


class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    time_limit: Optional[int] = None
    passing_score: float = 70.0
    max_attempts: int = 3


class QuizCreate(QuizBase):
    topic_id: str
    questions: List[QuizQuestion]


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time_limit: Optional[int] = None
    passing_score: Optional[float] = None
    max_attempts: Optional[int] = None
    questions: Optional[List[QuizQuestion]] = None
    is_active: Optional[bool] = None


class QuizResponse(QuizBase):
    id: str
    topic_id: str
    is_active: bool
    questions: List[QuizQuestion]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
