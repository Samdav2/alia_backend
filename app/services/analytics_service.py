"""
Analytics service
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.analytics import Analytics, AccessibilityUsage
from app.models.progress import Progress
from app.models.course import Enrollment
from datetime import datetime, timedelta
import uuid


class AnalyticsService:
    @staticmethod
    def get_performance_analytics(
        db: Session,
        user_id: str,
        period: str = "month",
        course_id: str = None
    ) -> Dict[str, Any]:
        # Calculate date range
        end_date = datetime.utcnow()
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        else:  # semester
            start_date = end_date - timedelta(days=120)
        
        # Get user progress records
        query = db.query(Progress).filter(Progress.user_id == user_id)
        if course_id:
            query = query.filter(Progress.course_id == course_id)
        
        progress_records = query.all()
        
        # Calculate overview metrics
        total_time_spent = sum(p.time_spent for p in progress_records)
        courses_completed = len([p for p in progress_records if p.completion_percentage == 100])
        
        # Calculate average score (placeholder - would need assessment data)
        average_score = 85.0  # This would be calculated from actual assessment results
        
        # Calculate streak days (placeholder)
        streak_days = 5  # This would be calculated from daily activity
        
        # Get course progress
        course_progress = []
        for progress in progress_records:
            course_progress.append({
                "course_id": progress.course_id,
                "course_name": "Course Name",  # Would join with Course table
                "progress": progress.completion_percentage,
                "time_spent": progress.time_spent,
                "last_accessed": progress.last_accessed_at
            })
        
        # Generate weekly activity (placeholder)
        weekly_activity = []
        for i in range(7):
            date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            weekly_activity.append({
                "date": date,
                "time_spent": 60,  # Would be calculated from actual data
                "topics_completed": 2
            })
        
        return {
            "overview": {
                "total_time_spent": total_time_spent,
                "courses_completed": courses_completed,
                "average_score": average_score,
                "streak_days": streak_days
            },
            "course_progress": course_progress,
            "weekly_activity": weekly_activity
        }

    @staticmethod
    def get_accessibility_analytics(db: Session, user_id: str) -> Dict[str, Any]:
        # Get or create accessibility usage record
        usage = db.query(AccessibilityUsage).filter(
            AccessibilityUsage.user_id == user_id
        ).first()
        
        if not usage:
            usage = AccessibilityUsage(
                user_id=user_id
            )
            db.add(usage)
            db.commit()
            db.refresh(usage)
        
        return {
            "feature_usage": {
                "bionic_reading": usage.bionic_reading_usage,
                "voice_navigation": usage.voice_navigation_usage,
                "text_to_speech": usage.text_to_speech_usage,
                "high_contrast": usage.high_contrast_usage
            },
            "accessibility_score": usage.accessibility_score,
            "recommendations": usage.recommendations
        }

    @staticmethod
    def update_accessibility_usage(
        db: Session,
        user_id: str,
        feature: str
    ):
        usage = db.query(AccessibilityUsage).filter(
            AccessibilityUsage.user_id == user_id
        ).first()
        
        if not usage:
            usage = AccessibilityUsage(
                user_id=user_id
            )
            db.add(usage)
        
        # Increment feature usage
        if feature == "bionic_reading":
            usage.bionic_reading_usage += 1
        elif feature == "voice_navigation":
            usage.voice_navigation_usage += 1
        elif feature == "text_to_speech":
            usage.text_to_speech_usage += 1
        elif feature == "high_contrast":
            usage.high_contrast_usage += 1
        
        db.commit()

    @staticmethod
    def get_admin_dashboard_stats(db: Session) -> Dict[str, Any]:
        # Get basic stats
        from app.models.user import User
        from app.models.course import Course, Enrollment
        
        total_users = db.query(func.count(User.id)).scalar()
        total_courses = db.query(func.count(Course.id)).scalar()
        total_enrollments = db.query(func.count(Enrollment.id)).scalar()
        
        # Active users (logged in within last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = db.query(func.count(User.id)).filter(
            User.last_login >= thirty_days_ago
        ).scalar()
        
        return {
            "stats": {
                "total_users": total_users,
                "total_courses": total_courses,
                "total_enrollments": total_enrollments,
                "active_users": active_users
            },
            "recent_activity": [],  # Would be populated with actual activity data
            "system_health": {
                "status": "healthy",
                "uptime": 99.9,
                "response_time": 150
            }
        }