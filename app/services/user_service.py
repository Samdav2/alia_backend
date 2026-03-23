"""
User management service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.schemas.user import UserUpdate
from datetime import datetime


class UserService:
    @staticmethod
    def get_user_profile(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update_user_profile(db: Session, user_id: str, user_update: UserUpdate) -> Optional[User]:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        department: Optional[str] = None
    ) -> tuple[List[User], int]:
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        if department:
            query = query.filter(User.department == department)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total

    @staticmethod
    def update_last_login(db: Session, user_id: str):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            db.commit()

    @staticmethod
    def deactivate_user(db: Session, user_id: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def activate_user(db: Session, user_id: str) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = True
            db.commit()
            return True
        return False