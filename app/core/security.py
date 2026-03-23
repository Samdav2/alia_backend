"""
Security utilities and dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User
import redis
from app.database import get_redis
from app.config import get_settings

settings = get_settings()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = AuthService.verify_token(credentials.credentials)
        if payload is None or payload.get("type") != "access":
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = AuthService.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user
async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> User:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None

    try:
        payload = AuthService.verify_token(credentials.credentials)
        if payload is None or payload.get("type") != "access":
            return None

        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        user = AuthService.get_user_by_id(db, user_id=user_id)
        if user is None or not user.is_active:
            return None

        return user
    except Exception:
        return None


def require_roles(allowed_roles: list):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


# Rate limiting decorator
def rate_limit(key_prefix: str, limit: int, window: int = 60):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            redis_client = get_redis()
            
            # Skip rate limiting if Redis is not available
            if redis_client is None:
                return await func(*args, **kwargs)
            
            # Extract user identifier (could be IP or user ID)
            user_key = f"{key_prefix}:rate_limit"  # Simplified for demo
            
            try:
                current = redis_client.get(user_key)
                if current is None:
                    redis_client.setex(user_key, window, 1)
                else:
                    current = int(current)
                    if current >= limit:
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Rate limit exceeded"
                        )
                    redis_client.incr(user_key)
            except Exception:
                # If Redis fails, allow the request to proceed
                pass
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator