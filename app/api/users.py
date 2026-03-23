"""
User management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate, UserListResponse
from app.services.user_service import UserService
from app.core.security import get_current_user, require_roles
from app.models.user import User

router = APIRouter(prefix="/api/users", tags=["User Management"])


@router.get("/profile", response_model=dict)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    
    user = UserService.get_user_profile(db, str(current_user.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "data": UserResponse.from_orm(user)
    }


@router.put("/profile", response_model=dict)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    
    updated_user = UserService.update_user_profile(db, str(current_user.id), user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "data": UserResponse.from_orm(updated_user)
    }


@router.get("", response_model=dict)
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get all users (Admin only)"""
    
    skip = (page - 1) * limit
    users, total = UserService.get_users(db, skip, limit, role, department)
    
    total_pages = (total + limit - 1) // limit
    
    return {
        "success": True,
        "data": {
            "users": [UserListResponse.from_orm(user) for user in users],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages
            }
        }
    }


@router.put("/{user_id}/deactivate", response_model=dict)
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Deactivate user account (Admin only)"""
    
    success = UserService.deactivate_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "message": "User deactivated successfully"
    }


@router.put("/{user_id}/activate", response_model=dict)
async def activate_user(
    user_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Activate user account (Admin only)"""
    
    success = UserService.activate_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "message": "User activated successfully"
    }