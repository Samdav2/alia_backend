"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserRegister, UserLogin, Token, RefreshToken
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.core.security import rate_limit
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=dict)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account"""
    
    # Check if user already exists
    existing_user = AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = AuthService.create_user(db, user_data.dict())
    
    # Create tokens
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "success": True,
        "data": {
            "user": {
                "id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "department": user.department
            },
            "token": access_token,
            "refresh_token": refresh_token
        }
    }


@router.post("/login", response_model=dict)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and get access token"""
    
    user = AuthService.authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Update last login
    UserService.update_last_login(db, str(user.id))
    
    # Create tokens
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "success": True,
        "data": {
            "user": {
                "id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role
            },
            "token": access_token,
            "refresh_token": refresh_token
        }
    }


@router.post("/logout", response_model=dict)
async def logout():
    """Logout user and invalidate token"""
    # In a real implementation, you would add the token to a blacklist
    return {
        "success": True,
        "message": "Logged out successfully"
    }


@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_data: RefreshToken, db: Session = Depends(get_db)):
    """Refresh access token"""
    
    payload = AuthService.verify_token(refresh_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    user = AuthService.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )
    
    # Create new tokens
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    new_refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "success": True,
        "data": {
            "token": access_token,
            "refresh_token": new_refresh_token
        }
    }