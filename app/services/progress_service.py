"""
Progress tracking service - Async compatible
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.progress import Progress, TopicProgress
from app.models.course import Course, Topic, Module
from app.schemas.progress import TopicProgressUpdate
from datetime import datetime
import uuid


class ProgressService:
    @staticmethod
    async def get_course_progress(db: AsyncSession, user_id: str, course_id: str) -> Optional[Progress]:
        """Async: Get course progress for user"""
        result = await db.execute(select(Progress).filter(
            Progress.user_id == user_id,
            Progress.course_id == course_id
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_or_update_progress(
        db: AsyncSession,
        user_id: str,
        course_id: str
    ) -> Progress:
        """Async: Create or update progress record"""
        progress = await ProgressService.get_course_progress(db, user_id, course_id)

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
        total_topics_result = await db.execute(
            select(func.count(Topic.id)).join(Module).filter(
                Module.course_id == course_id
            )
        )
        total_topics = total_topics_result.scalar() or 0

        progress.total_topics = total_topics

        # Calculate completed topics
        completed_count_result = await db.execute(select(func.count(TopicProgress.id)).filter(
            TopicProgress.progress_id == progress.id,
            TopicProgress.status == "completed"
        ))
        completed_count = completed_count_result.scalar() or 0

        progress.completed_topics = completed_count
        progress.completion_percentage = (completed_count / total_topics * 100) if total_topics > 0 else 0

        await db.commit()
        await db.refresh(progress)
        return progress

    @staticmethod
    async def update_topic_progress(
        db: AsyncSession,
        user_id: str,
        course_id: str,
        topic_id: str,
        progress_update: TopicProgressUpdate
    ) -> Optional[TopicProgress]:
        """Async: Update topic progress"""
        # Get or create progress record
        progress = await ProgressService.create_or_update_progress(db, user_id, course_id)

        # Get or create topic progress
        result = await db.execute(select(TopicProgress).filter(
            TopicProgress.progress_id == progress.id,
            TopicProgress.topic_id == topic_id
        ))
        topic_progress = result.scalar_one_or_none()

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

        await db.commit()
        await db.refresh(topic_progress)

        # Recalculate progress
        await ProgressService.create_or_update_progress(db, user_id, course_id)

        return topic_progress

    @staticmethod
    async def get_topic_progress_list(db: AsyncSession, progress_id: str):
        """Async: Get list of topic progress records"""
        result = await db.execute(select(TopicProgress).filter(
            TopicProgress.progress_id == progress_id
        ))
        return result.scalars().all()
