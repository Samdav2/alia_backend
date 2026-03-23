"""
Analytics API routes
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.analytics import PerformanceAnalytics, AccessibilityAnalytics
from app.services.analytics_service import AnalyticsService
from app.core.security import get_current_user, require_roles
from app.models.user import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/performance", response_model=dict)
async def get_performance_analytics(
    period: str = Query("month", regex="^(week|month|semester)$"),
    course_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get performance analytics"""
    
    analytics = AnalyticsService.get_performance_analytics(
        db, str(current_user.id), period, course_id
    )
    
    return {
        "success": True,
        "data": analytics
    }


@router.get("/accessibility", response_model=dict)
async def get_accessibility_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get accessibility usage analytics"""
    
    analytics = AnalyticsService.get_accessibility_analytics(db, str(current_user.id))
    
    return {
        "success": True,
        "data": analytics
    }


@router.post("/accessibility/{feature}", response_model=dict)
async def track_accessibility_usage(
    feature: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track accessibility feature usage"""
    
    valid_features = ["bionic_reading", "voice_navigation", "text_to_speech", "high_contrast"]
    if feature not in valid_features:
        raise HTTPException(status_code=400, detail="Invalid feature")
    
    AnalyticsService.update_accessibility_usage(db, str(current_user.id), feature)
    
    return {
        "success": True,
        "message": f"Tracked usage of {feature}"
    }