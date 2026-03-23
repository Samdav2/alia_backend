"""
Notifications API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.notification import NotificationsResponse
from app.services.notification_service import NotificationService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=dict)
async def get_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    
    result = NotificationService.get_user_notifications(db, str(current_user.id))
    
    return {
        "success": True,
        "data": result
    }


@router.put("/{notification_id}/read", response_model=dict)
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    
    success = NotificationService.mark_notification_as_read(
        db, notification_id, str(current_user.id)
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {
        "success": True,
        "message": "Notification marked as read"
    }


@router.put("/read-all", response_model=dict)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    
    NotificationService.mark_all_as_read(db, str(current_user.id))
    
    return {
        "success": True,
        "message": "All notifications marked as read"
    }