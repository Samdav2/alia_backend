"""
Authentication service - Async compatible
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.config import get_settings
import uuid

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            return None

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Async: Authenticate user by email and password"""
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict) -> User:
        """Async: Create a new user"""
        # Create user with UUID
        db_user = User(
            full_name=user_data["full_name"],
            email=user_data["email"],
            hashed_password=AuthService.get_password_hash(user_data["password"]),
            role=user_data["role"],
            department=user_data["department"],
            student_id=user_data.get("student_id")
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Async: Get user by email"""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """Async: Get user by ID"""
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()
