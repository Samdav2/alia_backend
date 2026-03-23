"""
Admin API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.user_service import UserService
from app.services.admin_service import AdminService
from app.core.security import require_roles
from app.models.user import User
import uuid

router = APIRouter(prefix="/api/admin", tags=["Administration"])


@router.get("/dashboard", response_model=dict)
async def get_admin_dashboard(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get admin dashboard data"""
    
    dashboard_data = AnalyticsService.get_admin_dashboard_stats(db)
    
    return {
        "success": True,
        "data": dashboard_data
    }


@router.get("/users/{user_id}/accessibility", response_model=dict)
async def get_user_accessibility_report(
    user_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get user accessibility report"""
    
    user = UserService.get_user_profile(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    accessibility_data = AnalyticsService.get_accessibility_analytics(db, user_id)
    
    return {
        "success": True,
        "data": {
            "user_id": user.id,
            "disability_info": user.disability_info,
            "feature_usage": accessibility_data["feature_usage"],
            "recommendations": accessibility_data["recommendations"]
        }
    }


# User Management Endpoints
@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get all users with filters"""
    skip = (page - 1) * limit
    users, total = AdminService.get_all_users(db, skip, limit, role, search, is_active)
    
    total_pages = (total + limit - 1) // limit
    
    return {
        "success": True,
        "data": {
            "users": users,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages
            }
        }
    }


@router.post("/users")
async def create_user(
    user_data: dict,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Create a new user"""
    user = AdminService.create_user(db, user_data)
    
    return {
        "success": True,
        "data": user,
        "message": "User created successfully"
    }


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: dict,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Update a user"""
    user = AdminService.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "data": user,
        "message": "User updated successfully"
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Delete a user"""
    success = AdminService.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "message": "User deleted successfully"
    }


@router.post("/users/bulk-action")
async def bulk_user_action(
    action_data: dict,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Perform bulk action on users"""
    success = AdminService.bulk_user_action(
        db,
        action_data.get("user_ids", []),
        action_data.get("action"),
        action_data.get("data")
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Bulk action failed")
    
    return {
        "success": True,
        "message": f"Bulk action '{action_data.get('action')}' completed successfully"
    }


# Course Management Endpoints
@router.get("/courses")
async def get_all_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get all courses with admin view"""
    skip = (page - 1) * limit
    courses, total = AdminService.get_all_courses_admin(db, skip, limit, status, department)
    
    total_pages = (total + limit - 1) // limit
    
    return {
        "success": True,
        "data": {
            "courses": courses,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages
            }
        }
    }


@router.put("/courses/{course_id}/approve")
async def approve_course(
    course_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Approve a course"""
    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    success = AdminService.approve_course(db, course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {
        "success": True,
        "message": "Course approved successfully"
    }


@router.put("/courses/{course_id}/reject")
async def reject_course(
    course_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Reject a course"""
    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    success = AdminService.reject_course(db, course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {
        "success": True,
        "message": "Course rejected successfully"
    }


@router.put("/courses/{course_id}/status")
async def change_course_status(
    course_id: str,
    status_data: dict,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Change course status (draft/published)"""
    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    success = AdminService.change_course_status(
        db, 
        course_id, 
        status_data.get("status", "published")
    )
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    
    status = status_data.get("status", "published")
    message = f"Course {'published' if status == 'published' else 'set to draft'} successfully"
    
    return {
        "success": True,
        "message": message
    }


@router.put("/courses/{course_id}/feature")
async def feature_course(
    course_id: str,
    feature_data: dict,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Feature or unfeature a course"""
    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    success = AdminService.feature_course(db, course_id, feature_data.get("featured", True))
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {
        "success": True,
        "message": "Course featured status updated successfully"
    }


# System Analytics Endpoints
@router.get("/statistics")
async def get_system_statistics(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics"""
    stats = AdminService.get_system_statistics(db)
    
    return {
        "success": True,
        "data": stats
    }


@router.get("/accessibility-report")
async def get_accessibility_report(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get system-wide accessibility report"""
    report = AdminService.get_accessibility_report(db)
    
    return {
        "success": True,
        "data": report
    }


@router.get("/performance-metrics")
async def get_performance_metrics(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get system performance metrics"""
    metrics = AdminService.get_performance_metrics(db)
    
    return {
        "success": True,
        "data": metrics
    }


# System Health Endpoint
@router.get("/system-health")
async def get_system_health(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get system health status"""
    health = AdminService.get_system_health(db)
    
    return {
        "success": True,
        "data": health
    }


# Announcement Management Endpoints
@router.post("/announcements")
async def create_announcement(
    announcement_data: dict,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Create a new announcement"""
    announcement = AdminService.create_announcement(db, announcement_data, str(current_user.id))
    
    return {
        "success": True,
        "data": announcement,
        "message": "Announcement created successfully"
    }


@router.get("/announcements")
async def get_all_announcements(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get all announcements"""
    skip = (page - 1) * limit
    announcements, total = AdminService.get_all_announcements(db, skip, limit, is_active)
    
    total_pages = (total + limit - 1) // limit
    
    return {
        "success": True,
        "data": {
            "announcements": announcements,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages
            }
        }
    }


@router.put("/announcements/{announcement_id}")
async def update_announcement(
    announcement_id: str,
    announcement_data: dict,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Update an announcement"""
    announcement = AdminService.update_announcement(db, announcement_id, announcement_data)
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    return {
        "success": True,
        "data": announcement,
        "message": "Announcement updated successfully"
    }


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Delete an announcement"""
    success = AdminService.delete_announcement(db, announcement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    return {
        "success": True,
        "message": "Announcement deleted successfully"
    }


# Department Management Endpoints
@router.get("/departments")
async def get_all_departments(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get all departments"""
    departments = AdminService.get_all_departments(db)
    
    return {
        "success": True,
        "data": {
            "departments": departments
        }
    }


@router.post("/departments")
async def create_department(
    department_data: dict,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Create a new department"""
    department = AdminService.create_department(db, department_data)
    
    return {
        "success": True,
        "data": department,
        "message": "Department created successfully"
    }


@router.put("/departments/{department_id}")
async def update_department(
    department_id: str,
    department_data: dict,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Update a department"""
    department = AdminService.update_department(db, department_id, department_data)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return {
        "success": True,
        "data": department,
        "message": "Department updated successfully"
    }


@router.delete("/departments/{department_id}")
async def delete_department(
    department_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Delete a department"""
    success = AdminService.delete_department(db, department_id)
    if not success:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return {
        "success": True,
        "message": "Department deleted successfully"
    }


# Audit Log Endpoint
@router.get("/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Get audit logs"""
    skip = (page - 1) * limit
    logs, total = AdminService.get_audit_logs(db, skip, limit, user_id, action, resource_type)
    
    total_pages = (total + limit - 1) // limit
    
    return {
        "success": True,
        "data": {
            "logs": logs,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages
            }
        }
    }