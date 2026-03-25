"""
Notification service - Async compatible
"""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, update
from app.models.notification import Notification
from datetime import datetime
import uuid


class NotificationService:
    @staticmethod
    async def get_user_notifications(db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Async: Get user notifications"""
        result = await db.execute(select(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()))
        notifications = result.scalars().all()
        
        unread_result = await db.execute(select(func.count(Notification.id)).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ))
        unread_count = unread_result.scalar() or 0
        
        return {
            "notifications": notifications,
            "unread_count": unread_count
        }

    @staticmethod
    async def mark_notification_as_read(db: AsyncSession, notification_id: str, user_id: str) -> bool:
        """Async: Mark notification as read"""
        result = await db.execute(select(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ))
        notification = result.scalar_one_or_none()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            await db.commit()
            return True
        return False

    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        action_url: str = None
    ) -> Notification:
        """Async: Create notification"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            action_url=action_url
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification

    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user_id: str):
        """Async: Mark all notifications as read"""
        await db.execute(update(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).values(
            is_read=True,
            read_at=datetime.utcnow()
        ))
        await db.commit()
