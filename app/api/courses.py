"""
Course management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseListResponse, CourseDetailResponse,
    EnrollmentCreate, EnrollmentResponse, TopicResponse, ModuleResponse
)
from app.services.course_service import CourseService
from app.core.security import get_current_user, require_roles, get_current_user_optional
from app.models.user import User
from app.services.file_service import FileService
from app.config import get_settings
from datetime import datetime, timezone
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
    db: AsyncSession = Depends(get_db)
):
    """Get all courses with enrollment status for current user"""

    skip = (page - 1) * limit
    user_id = str(current_user.id) if current_user else None

    courses, total = await CourseService.get_courses_with_enrollment_status(
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
    db: AsyncSession = Depends(get_db)
):
    """Get specific course details with enrollment status"""

    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")

    course = await CourseService.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Convert course to dict and add enrollment status
    course_data = CourseDetailResponse.from_orm(course).dict()

    # Check enrollment status if user is authenticated
    is_staff = current_user and current_user.role in ["lecturer", "admin"]
    now = datetime.now(timezone.utc)

    if current_user:
        course_data['is_enrolled'] = await CourseService.check_user_enrollment(
            db, str(current_user.id), course_id
        )
    else:
        course_data['is_enrolled'] = False

    # Apply locking logic to modules and topics
    for module in course_data.get('modules', []):
        m_available_at = datetime.fromisoformat(module['available_at']) if isinstance(module['available_at'], str) else module['available_at']
        module['is_locked'] = not is_staff and m_available_at and m_available_at > now
        if module['is_locked']:
            module['availability_message'] = f"Available on {m_available_at.strftime('%Y-%m-%d %H:%M:%S')}"
            module['topics'] = [] # Hide topics in locked module
        else:
            for topic in module.get('topics', []):
                t_available_at = datetime.fromisoformat(topic['available_at']) if isinstance(topic['available_at'], str) else topic['available_at']
                topic['is_locked'] = not is_staff and t_available_at and t_available_at > now
                if topic['is_locked']:
                    topic['availability_message'] = f"Available on {t_available_at.strftime('%Y-%m-%d %H:%M:%S')}"
                    topic['content'] = "Locked until scheduled time"
                    topic['media_files'] = []

    return {
        "success": True,
        "data": course_data
    }


@router.post("", response_model=dict)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Create new course (Lecturer/Admin only)"""

    course = await CourseService.create_course(db, course_data, str(current_user.id))

    if not course:
        raise HTTPException(
            status_code=400,
            detail=f"Course with code '{course_data.code}' already exists"
        )

    return {
        "success": True,
        "data": CourseDetailResponse.from_orm(course)
    }


@router.put("/{course_id}", response_model=dict)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Update course (Lecturer/Admin only)"""

    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")

    course = await CourseService.update_course(db, course_id, course_update, str(current_user.id))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found or access denied")

    return {
        "success": True,
        "data": CourseDetailResponse.from_orm(course)
    }


@router.post("/{course_id}/picture", response_model=dict)
async def upload_course_picture(
    course_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Upload course picture and update thumbnail (Lecturer/Admin only)"""

    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")

    # 1. Validate course ownership or admin status
    course = await CourseService.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role != "admin" and str(course.instructor_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this course")

    # 2. Use FileService to save the file
    try:
        db_file = await FileService.save_uploaded_file(
            db=db,
            file=file,
            uploaded_by=str(current_user.id),
            context='course',
            course_id=course_id,
            file_type='image'
        )

        # 3. Update course thumbnail with the new file URL
        settings = get_settings()
        thumbnail_url = f"{settings.base_url}/api/files/download/{db_file.id}"

        await CourseService.update_course_thumbnail(
            db, course_id, thumbnail_url, str(course.instructor_id)
        )

        return {
            "success": True,
            "data": {
                "course_id": course_id,
                "thumbnail_url": thumbnail_url,
                "file_id": str(db_file.id)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{course_id}", response_model=dict)
async def delete_course(
    course_id: str,
    current_user: User = Depends(require_roles(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Delete course (Admin only)"""

    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")

    success = await CourseService.delete_course(db, course_id, current_user.role)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")

    return {
        "success": True,
        "message": "Course deleted successfully"
    }


@router.get("/{course_id}/modules", response_model=dict)
async def get_course_modules(
    course_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get course modules"""

    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")

    modules = await CourseService.get_course_modules(db, course_id)

    is_staff = current_user and current_user.role in ["lecturer", "admin"]
    now = datetime.now(timezone.utc)

    # Convert modules to serializable format
    modules_data = []
    for module in modules:
        is_locked = not is_staff and module.available_at and module.available_at > now
        module_data = {
            "id": str(module.id),
            "title": module.title,
            "description": module.description,
            "order": module.order,
            "course_id": str(module.course_id),
            "available_at": module.available_at,
            "is_locked": is_locked,
            "availability_message": f"Available on {module.available_at.strftime('%Y-%m-%d %H:%M:%S')}" if is_locked else None,
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
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get module topics"""

    # Validate UUID formats
    try:
        uuid.UUID(course_id)
        uuid.UUID(module_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID or module ID format")

    topics = await CourseService.get_module_topics(db, module_id)

    is_staff = current_user and current_user.role in ["lecturer", "admin"]
    now = datetime.now(timezone.utc)

    # Convert topics to serializable format
    topics_data = []
    for topic in topics:
        is_locked = not is_staff and topic.available_at and topic.available_at > now
        topic_data = {
            "id": str(topic.id),
            "title": topic.title,
            "description": topic.description,
            "duration": topic.duration,
            "order": topic.order,
            "content_type": topic.content_type,
            "content": topic.content if not is_locked else "Locked until scheduled time",
            "media_files": topic.media_files if not is_locked else [],
            "prerequisites": topic.prerequisites or [],
            "learning_objectives": topic.learning_objectives or [],
            "module_id": str(topic.module_id),
            "available_at": topic.available_at,
            "is_locked": is_locked,
            "availability_message": f"Available on {topic.available_at.strftime('%Y-%m-%d %H:%M:%S')}" if is_locked else None,
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
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Get specific topic content"""

    # Validate UUID formats
    try:
        uuid.UUID(course_id)
        uuid.UUID(topic_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID or topic ID format")

    topic = await CourseService.get_topic_by_id(db, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    is_staff = current_user and current_user.role in ["lecturer", "admin"]
    now = datetime.now(timezone.utc)

    is_locked = not is_staff and topic.available_at and topic.available_at > now
    if is_locked:
        raise HTTPException(
            status_code=403,
            detail=f"This content is locked until {topic.available_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

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
        "available_at": topic.available_at,
        "is_locked": False,
        "assessments": [],  # Placeholder for assessments
        "created_at": topic.created_at,
        "updated_at": topic.updated_at
    }

    return {
        "success": True,
        "data": topic_data
    }
