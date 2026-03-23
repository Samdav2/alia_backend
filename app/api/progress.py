"""
Progress tracking API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.progress import ProgressResponse, TopicProgressUpdate
from app.services.progress_service import ProgressService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/progress", tags=["Progress Tracking"])


@router.get("/{course_id}", response_model=dict)
async def get_course_progress(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get course progress"""
    
    progress = ProgressService.get_course_progress(db, str(current_user.id), course_id)
    if not progress:
        # Create initial progress record
        progress = ProgressService.create_or_update_progress(db, str(current_user.id), course_id)
    
    # Get topic progress
    topic_progress = ProgressService.get_topic_progress_list(db, progress.id)
    
    return {
        "success": True,
        "data": {
            "course_id": progress.course_id,
            "user_id": progress.user_id,
            "completed_topics": progress.completed_topics,
            "total_topics": progress.total_topics,
            "completion_percentage": progress.completion_percentage,
            "time_spent": progress.time_spent,
            "current_topic": progress.current_topic_id,
            "last_accessed_at": progress.last_accessed_at,
            "topic_progress": topic_progress
        }
    }


@router.post("/{course_id}/topics/{topic_id}", response_model=dict)
async def update_topic_progress(
    course_id: str,
    topic_id: str,
    progress_update: TopicProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update topic progress"""
    
    topic_progress = ProgressService.update_topic_progress(
        db, str(current_user.id), course_id, topic_id, progress_update
    )
    
    if not topic_progress:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    return {
        "success": True,
        "data": {
            "topic_id": topic_progress.topic_id,
            "status": topic_progress.status,
            "time_spent": topic_progress.time_spent,
            "score": topic_progress.score,
            "completed_at": topic_progress.completed_at
        }
    }