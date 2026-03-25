"""
Lecturer-specific API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.database import get_db
from app.schemas.course import CourseCreate, CourseUpdate, ModuleCreate, TopicCreate
from app.schemas.assessment import QuizCreate, QuizUpdate
from app.services.course_service import CourseService
from app.services.lecturer_service import LecturerService
from app.core.security import get_current_user, require_roles
from app.models.user import User
import uuid

router = APIRouter(prefix="/api/lecturer", tags=["Lecturer"])


@router.get("/courses/my")
async def get_my_courses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Get lecturer's own courses"""
    skip = (page - 1) * limit
    courses, total = await LecturerService.get_lecturer_courses(
        db, str(current_user.id), skip, limit, status
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


@router.put("/courses/{course_id}/publish")
async def publish_course(
    course_id: str,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Publish a course"""
    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    success = await LecturerService.publish_course(db, course_id, str(current_user.id))
    if not success:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    
    return {
        "success": True,
        "message": "Course published successfully"
    }


@router.put("/courses/{course_id}/unpublish")
async def unpublish_course(
    course_id: str,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Unpublish a course"""
    # Validate UUID format
    try:
        uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    success = await LecturerService.unpublish_course(db, course_id, str(current_user.id))
    if not success:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    
    return {
        "success": True,
        "message": "Course unpublished successfully"
    }


@router.post("/courses/{course_id}/modules")
async def create_module(
    course_id: str,
    module_data: ModuleCreate,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new module in a course"""
    module = await LecturerService.create_module(db, course_id, module_data, str(current_user.id))
    if not module:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    
    return {
        "success": True,
        "data": module
    }


@router.put("/courses/modules/{module_id}")
async def update_module(
    module_id: str,
    module_data: dict,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Update a module"""
    module = await LecturerService.update_module(db, module_id, module_data, str(current_user.id))
    if not module:
        raise HTTPException(status_code=404, detail="Module not found or access denied")
    
    return {
        "success": True,
        "data": module
    }


@router.delete("/courses/modules/{module_id}")
async def delete_module(
    module_id: str,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Delete a module"""
    success = await LecturerService.delete_module(db, module_id, str(current_user.id))
    if not success:
        raise HTTPException(status_code=404, detail="Module not found or access denied")
    
    return {
        "success": True,
        "message": "Module deleted successfully"
    }


@router.put("/courses/{course_id}/modules/reorder")
async def reorder_modules(
    course_id: str,
    module_orders: dict,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Reorder modules in a course"""
    success = await LecturerService.reorder_modules(
        db, course_id, module_orders.get("module_orders", []), str(current_user.id)
    )
    if not success:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    
    return {
        "success": True,
        "message": "Modules reordered successfully"
    }


@router.post("/courses/modules/{module_id}/topics")
async def create_topic(
    module_id: str,
    topic_data: TopicCreate,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new topic in a module"""
    topic = await LecturerService.create_topic(db, module_id, topic_data, str(current_user.id))
    if not topic:
        raise HTTPException(status_code=404, detail="Module not found or access denied")
    
    return {
        "success": True,
        "data": topic
    }


@router.put("/courses/topics/{topic_id}")
async def update_topic(
    topic_id: str,
    topic_data: dict,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Update a topic"""
    topic = await LecturerService.update_topic(db, topic_id, topic_data, str(current_user.id))
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found or access denied")
    
    return {
        "success": True,
        "data": topic
    }


@router.delete("/courses/topics/{topic_id}")
async def delete_topic(
    topic_id: str,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Delete a topic"""
    success = await LecturerService.delete_topic(db, topic_id, str(current_user.id))
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found or access denied")
    
    return {
        "success": True,
        "message": "Topic deleted successfully"
    }


@router.put("/courses/modules/{module_id}/topics/reorder")
async def reorder_topics(
    module_id: str,
    topic_orders: dict,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Reorder topics in a module"""
    success = await LecturerService.reorder_topics(
        db, module_id, topic_orders.get("topic_orders", []), str(current_user.id)
    )
    if not success:
        raise HTTPException(status_code=404, detail="Module not found or access denied")
    
    return {
        "success": True,
        "message": "Topics reordered successfully"
    }


@router.get("/courses/{course_id}/enrollments")
async def get_course_enrollments(
    course_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Get enrollments for a course"""
    skip = (page - 1) * limit
    enrollments, total = await LecturerService.get_course_enrollments(
        db, course_id, str(current_user.id), skip, limit, status
    )
    
    if enrollments is None:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    
    total_pages = (total + limit - 1) // limit
    
    return {
        "success": True,
        "data": {
            "enrollments": enrollments,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages
            }
        }
    }


@router.get("/courses/{course_id}/analytics")
async def get_course_analytics(
    course_id: str,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a course"""
    analytics = await LecturerService.get_course_analytics(db, course_id, str(current_user.id))
    if not analytics:
        raise HTTPException(status_code=404, detail="Course not found or access denied")
    
    return {
        "success": True,
        "data": analytics
    }


@router.get("/courses/{course_id}/students/{student_id}/progress")
async def get_student_progress(
    course_id: str,
    student_id: str,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Get specific student's progress in a course"""
    progress = await LecturerService.get_student_progress(
        db, course_id, student_id, str(current_user.id)
    )
    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found or access denied")
    
    return {
        "success": True,
        "data": progress
    }


@router.get("/class-demographics")
async def get_class_demographics(
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Get demographics of all students in lecturer's courses"""
    demographics = await LecturerService.get_class_demographics(db, str(current_user.id))
    
    return {
        "success": True,
        "data": demographics
    }


@router.get("/alerts")
async def get_lecturer_alerts(
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Get alerts about students needing attention"""
    alerts = await LecturerService.get_lecturer_alerts(db, str(current_user.id))
    
    return {
        "success": True,
        "data": {
            "alerts": alerts
        }
    }


@router.post("/notifications")
async def send_notification_to_students(
    notification_data: dict,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Send notification to students"""
    success = await LecturerService.send_notification_to_students(
        db,
        str(current_user.id),
        notification_data.get("course_id"),
        notification_data.get("recipient_type"),
        notification_data.get("student_ids", []),
        notification_data.get("title"),
        notification_data.get("message"),
        notification_data.get("type")
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to send notifications")
    
    return {
        "success": True,
        "message": "Notifications sent successfully"
    }



@router.post("/quizzes")
async def create_quiz(
    quiz_data: QuizCreate,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new quiz for a topic"""
    quiz = await LecturerService.create_quiz(db, quiz_data, str(current_user.id))
    if not quiz:
        raise HTTPException(status_code=404, detail="Topic not found or access denied")
    
    return {
        "success": True,
        "data": quiz
    }


@router.put("/quizzes/{quiz_id}")
async def update_quiz(
    quiz_id: str,
    quiz_data: QuizUpdate,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Update a quiz"""
    quiz = await LecturerService.update_quiz(db, quiz_id, quiz_data, str(current_user.id))
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found or access denied")
    
    return {
        "success": True,
        "data": quiz
    }


@router.delete("/quizzes/{quiz_id}")
async def delete_quiz(
    quiz_id: str,
    current_user: User = Depends(require_roles(["lecturer", "admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Delete a quiz"""
    success = await LecturerService.delete_quiz(db, quiz_id, str(current_user.id))
    if not success:
        raise HTTPException(status_code=404, detail="Quiz not found or access denied")
    
    return {
        "success": True,
        "message": "Quiz deleted successfully"
    }
