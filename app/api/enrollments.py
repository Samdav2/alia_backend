"""
Enrollment management API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.course import EnrollmentCreate, EnrollmentResponse
from app.services.course_service import CourseService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/enrollments", tags=["Enrollments"])


@router.get("", response_model=dict)
async def get_enrollments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's enrollments"""

    enrollments = await CourseService.get_user_enrollments(db, str(current_user.id))

    return {
        "success": True,
        "data": {
            "enrollments": [EnrollmentResponse.from_orm(enrollment) for enrollment in enrollments]
        }
    }


@router.post("", response_model=dict)
async def enroll_in_course(
    enrollment_data: EnrollmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enroll in a course"""

    # Check if course exists
    course = await CourseService.get_course_by_id(db, enrollment_data.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    enrollment = await CourseService.enroll_user(db, str(current_user.id), enrollment_data.course_id)
    if not enrollment:
        raise HTTPException(status_code=400, detail="Already enrolled in this course")

    return {
        "success": True,
        "data": EnrollmentResponse.from_orm(enrollment)
    }


@router.delete("/{course_id}", response_model=dict)
async def unenroll_from_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unenroll from a course"""

    success = await CourseService.unenroll_user(db, str(current_user.id), course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    return {
        "success": True,
        "message": "Successfully unenrolled from course"
    }
