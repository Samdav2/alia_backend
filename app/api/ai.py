"""
AI service API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.ai import (
    ChatRequest, ChatResponse, SimplifyRequest, SimplifyResponse,
    VoiceSessionResponse, TranscribeRequest, TranscribeResponse
)
from app.services.ai_service import AIService
from app.core.security import get_current_user, rate_limit
from app.models.user import User
import uuid

router = APIRouter(prefix="/api/ai", tags=["AI Services"])


@router.post("/chat", response_model=dict)
@rate_limit("ai_chat", 30)
async def chat_with_ai(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send message to AI assistant"""
    
    try:
        response = await AIService.process_chat_message(
            chat_request.message,
            chat_request.context,
            str(current_user.id)
        )
        
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI service error")


@router.post("/simplify", response_model=dict)
@rate_limit("ai_simplify", 20)
async def simplify_content(
    simplify_request: SimplifyRequest,
    current_user: User = Depends(get_current_user)
):
    """Simplify content for better understanding"""
    
    try:
        response = await AIService.simplify_content(
            simplify_request.content,
            simplify_request.level,
            simplify_request.language
        )
        
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI service error")


@router.post("/voice/session", response_model=dict)
async def start_voice_session(
    current_user: User = Depends(get_current_user)
):
    """Start voice chat session"""
    
    session_id = str(uuid.uuid4())
    
    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "supported_languages": ["English", "Igbo", "Hausa", "Yoruba"],
            "max_duration": 300  # 5 minutes
        }
    }


@router.post("/voice/transcribe", response_model=dict)
@rate_limit("voice_transcribe", 10)
async def transcribe_voice(
    transcribe_request: TranscribeRequest,
    current_user: User = Depends(get_current_user)
):
    """Transcribe voice input"""
    
    try:
        response = await AIService.transcribe_audio(
            transcribe_request.audio_data,
            transcribe_request.language,
            transcribe_request.session_id
        )
        
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Voice transcription error")