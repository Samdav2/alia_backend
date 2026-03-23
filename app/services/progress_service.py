"""
Progress tracking service
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.progress import Progress, TopicProgress
from app.models.course import Course, Topic
from app.schemas.progress import TopicProgressUpdate
from datetime import datetime
import uuid


class ProgressService:
    @staticmethod
    def get_course_progress(db: Session, user_id: str, course_id: str) -> Optional[Progress]:
        return db.query(Progress).filter(
            Progress.user_id == user_id,
            Progress.course_id == course_id
        ).first()

    @staticmethod
    def create_or_update_progress(
        db: Session,
        user_id: str,
        course_id: str
    ) -> Progress:
        progress = ProgressService.get_course_progress(db, user_id, course_id)
        
        if not progress:
            # Create new progress record
            progress = Progress(
                user_id=user_id,
                course_id=course_id,
                last_accessed_at=datetime.utcnow()
            )
            db.add(progress)
        else:
            progress.last_accessed_at = datetime.utcnow()
        
        # Calculate total topics
        total_topics = db.query(Topic).join(
            Topic.module
        ).filter(
            Topic.module.has(course_id=course_id)
        ).count()
        
        progress.total_topics = total_topics
        
        # Calculate completed topics
        completed_count = db.query(TopicProgress).filter(
            TopicProgress.progress_id == progress.id,
            TopicProgress.status == "completed"
        ).count()
        
        progress.completed_topics = completed_count
        progress.completion_percentage = (completed_count / total_topics * 100) if total_topics > 0 else 0
        
        db.commit()
        db.refresh(progress)
        return progress

    @staticmethod
    def update_topic_progress(
        db: Session,
        user_id: str,
        course_id: str,
        topic_id: str,
        progress_update: TopicProgressUpdate
    ) -> Optional[TopicProgress]:
        # Get or create progress record
        progress = ProgressService.create_or_update_progress(db, user_id, course_id)
        
        # Get or create topic progress
        topic_progress = db.query(TopicProgress).filter(
            TopicProgress.progress_id == progress.id,
            TopicProgress.topic_id == topic_id
        ).first()
        
        if not topic_progress:
            topic_progress = TopicProgress(
                progress_id=progress.id,
                topic_id=topic_id
            )
            db.add(topic_progress)
        
        # Update topic progress
        topic_progress.status = progress_update.status
        topic_progress.time_spent += progress_update.time_spent or 0
        topic_progress.score = progress_update.score or topic_progress.score
        
        if progress_update.status == "completed" and not topic_progress.completed_at:
            topic_progress.completed_at = datetime.utcnow()
        
        # Update current topic in progress
        if progress_update.status == "in_progress":
            progress.current_topic_id = topic_id
        
        # Update total time spent
        progress.time_spent += progress_update.time_spent or 0
        
        db.commit()
        db.refresh(topic_progress)
        
        # Recalculate progress
        ProgressService.create_or_update_progress(db, user_id, course_id)
        
        return topic_progress

    @staticmethod
    def get_topic_progress_list(db: Session, progress_id: str):
        return db.query(TopicProgress).filter(
            TopicProgress.progress_id == progress_id
        ).all()