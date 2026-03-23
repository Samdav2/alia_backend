"""
Course management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseListResponse, CourseDetailResponse,
    EnrollmentCreate, EnrollmentResponse, TopicResponse, ModuleResponse
)
from app.services.course_service import CourseService
from app.core.security import get_current_user, require_roles, get_current_user_optional
from app.models.user import User
import uuid

router = APIRouter(prefix="/api/courses", tags=["Course Management"])


@router.get("", response_model=dict)
async def get_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    department: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get all courses with enrollment status for current user"""
    
    skip = (page - 1) * limit
    user_id = str(current_user.id) if current_user else None
    
    courses, total = CourseService.get_courses_with_enrollment_status(
        db, user_id, skip, limit, department, level, search
    )
    
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


@router.get("/{course_id}", response_model=dict)
async def get_course(
    course_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get specific course details with enrollment status"""
    
    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    course = CourseService.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Convert course to dict and add enrollment status
    course_data = CourseDetailResponse.from_orm(course).dict()
    
    # Check enrollment status if user is authenticated
    if current_user:
        course_data['is_enrolled'] = CourseService.check_user_enrollment(
            db, str(current_user.id), course_id
        )
    else:
        course_data['is_enrolled'] = False
    
    return {
        "success": True,
        "data": course_data
    }


@router.post("", response_model=dict)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: Session = Depends(get_db)
):
    """Create new course (Lecturer/Admin only)"""
    
    course = CourseService.create_course(db, course_data, str(current_user.id))
    
    return {
        "success": True,
        "data": CourseDetailResponse.from_orm(course)
    }


@router.put("/{course_id}", response_model=dict)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: Session = Depends(get_db)
):
    """Update course (Lecturer/Admin only)"""
    
    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    course = CourseService.update_course(db, course_id, course_update, str(current_user.id))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    
    return {
        "success": True,
        "data": CourseDetailResponse.from_orm(course)
    }


@router.delete("/{course_id}", response_model=dict)
async def delete_course(
    course_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db)
):
    """Delete course (Admin only)"""
    
    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    success = CourseService.delete_course(db, course_id, current_user.role)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {
        "success": True,
        "message": "Course deleted successfully"
    }


@router.get("/{course_id}/modules", response_model=dict)
async def get_course_modules(
    course_id: str,
    db: Session = Depends(get_db)
):
    """Get course modules"""
    
    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    modules = CourseService.get_course_modules(db, course_id)
    
    # Convert modules to serializable format
    modules_data = []
    for module in modules:
        module_data = {
            "id": str(module.id),
            "title": module.title,
            "description": module.description,
            "order": module.order,
            "course_id": str(module.course_id),
            "topics": [],  # Don't include topics here to avoid deep nesting
            "created_at": module.created_at,
            "updated_at": module.updated_at
        }
        modules_data.append(module_data)
    
    return {
        "success": True,
        "data": {"modules": modules_data}
    }


@router.get("/{course_id}/modules/{module_id}/topics", response_model=dict)
async def get_module_topics(
    course_id: str,
    module_id: str,
    db: Session = Depends(get_db)
):
    """Get module topics"""
    
    # Validate UUID formats
    try:
        uuid.UUID(course_id)
        uuid.UUID(module_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID or module ID format")
    
    topics = CourseService.get_module_topics(db, module_id)
    
    # Convert topics to serializable format
    topics_data = []
    for topic in topics:
        topic_data = {
            "id": str(topic.id),
            "title": topic.title,
            "description": topic.description,
            "duration": topic.duration,
            "order": topic.order,
            "content_type": topic.content_type,
            "content": topic.content,
            "media_files": topic.media_files or [],
            "prerequisites": topic.prerequisites or [],
            "learning_objectives": topic.learning_objectives or [],
            "module_id": str(topic.module_id),
            "assessments": [],  # Placeholder for assessments
            "created_at": topic.created_at,
            "updated_at": topic.updated_at
        }
        topics_data.append(topic_data)
    
    return {
        "success": True,
        "data": {"topics": topics_data}
    }


@router.get("/{course_id}/topics/{topic_id}", response_model=dict)
async def get_topic(
    course_id: str,
    topic_id: str,
    db: Session = Depends(get_db)
):
    """Get specific topic content"""
    
    # Validate UUID formats
    try:
        uuid.UUID(course_id)
        uuid.UUID(topic_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID or topic ID format")
    
    topic = CourseService.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Convert to schema response
    topic_data = {
        "id": str(topic.id),
        "title": topic.title,
        "description": topic.description,
        "duration": topic.duration,
        "order": topic.order,
        "content_type": topic.content_type,
        "content": topic.content,
        "media_files": topic.media_files or [],
        "prerequisites": topic.prerequisites or [],
        "learning_objectives": topic.learning_objectives or [],
        "module_id": str(topic.module_id),
        "assessments": [],  # Placeholder for assessments
        "created_at": topic.created_at,
        "updated_at": topic.updated_at
    }
    
    return {
        "success": True,
        "data": topic_data
    }