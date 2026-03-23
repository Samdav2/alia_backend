"""
AI service schemas
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ConversationMessage(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: str


class ChatContext(BaseModel):
    course_id: Optional[str] = None
    topic_id: Optional[str] = None
    conversation_history: List[ConversationMessage] = []


class ChatRequest(BaseModel):
    message: str
    context: ChatContext


class RelatedTopic(BaseModel):
    id: str
    title: str
    course_id: str


class ChatResponse(BaseModel):
    response: str
    suggestions: List[str] = []
    related_topics: List[RelatedTopic] = []


class SimplifyRequest(BaseModel):
    content: str
    level: str = "basic"  # basic, intermediate, advanced
    language: str = "English"


class SimplifyResponse(BaseModel):
    simplified_content: str
    key_points: List[str]
    examples: List[str]


class VoiceSessionResponse(BaseModel):
    session_id: str
    supported_languages: List[str]
    max_duration: int


class TranscribeRequest(BaseModel):
    session_id: str
    audio_data: str  # base64 encoded
    language: str = "English"


class TranscribeResponse(BaseModel):
    transcription: str
    confidence: float
    ai_response: str