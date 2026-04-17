"""
User management service - Async compatible
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.models.user import User
from app.schemas.user import UserUpdate
from datetime import datetime
import uuid
from typing import List, Optional, Dict, Any, Union


class UserService:
    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: Union[str, uuid.UUID]) -> Optional[User]:
        """Async: Get user profile by ID"""
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user_profile(db: AsyncSession, user_id: Union[str, uuid.UUID], user_update: UserUpdate) -> Optional[User]:
        """Async: Update user profile"""
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None

        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def get_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        department: Optional[str] = None
    ) -> tuple[List[User], int]:
        """Async: Get list of users with optional filtering"""
        query = select(User)

        if role:
            query = query.filter(User.role == role)
        if department:
            query = query.filter(User.department == department)

        # Get total count
        count_result = await db.execute(select(func.count(User.id)).select_from(User))
        if role:
            count_result = await db.execute(select(func.count(User.id)).filter(User.role == role))
        if department:
            count_result = await db.execute(select(func.count(User.id)).filter(User.department == department))

        total = count_result.scalar() or 0

        # Get paginated results
        result = await db.execute(query.offset(skip).limit(limit))
        users = result.scalars().all()

        return users, total

    @staticmethod
    async def update_last_login(db: AsyncSession, user_id: Union[str, uuid.UUID]):
        """Async: Update user last login timestamp"""
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.last_login = datetime.utcnow()
            await db.commit()

    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: str) -> bool:
        """Async: Deactivate user account"""
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_active = False
            await db.commit()
            return True
        return False

    @staticmethod
    async def activate_user(db: AsyncSession, user_id: str) -> bool:
        """Async: Activate user account"""
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_active = True
            await db.commit()
            return True
        return False
