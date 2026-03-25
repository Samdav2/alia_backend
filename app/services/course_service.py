"""
Course management service - Async compatible
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_, select, and_
from app.models.course import Course, Module, Topic, Enrollment
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate
import uuid


class CourseService:
    @staticmethod
    async def get_courses(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        level: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Course], int]:
        """Async: Get courses with optional filtering"""
        query = select(Course).filter(Course.is_active == True)

        if department:
            query = query.filter(Course.department == department)
        if level:
            query = query.filter(Course.level == level)
        if search:
            query = query.filter(
                or_(
                    Course.title.contains(search),
                    Course.description.contains(search),
                    Course.code.contains(search)
                )
            )

        # Get total count
        count_result = await db.execute(select(func.count(Course.id)).filter(Course.is_active == True))
        total = count_result.scalar() or 0

        # Get paginated results
        result = await db.execute(query.offset(skip).limit(limit))
        courses = result.scalars().all()

        return courses, total

    @staticmethod
    async def get_course_by_id(db: AsyncSession, course_id: str) -> Optional[Course]:
        """Async: Get course by ID with all relationships loaded"""
        from app.models.course import Module, Topic

        stmt = select(Course).filter(
            Course.id == course_id,
            Course.is_active == True
        ).options(
            selectinload(Course.modules)
            .selectinload(Module.topics)
            .selectinload(Topic.assessments)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_course(db: AsyncSession, course_data: CourseCreate, instructor_id: str) -> Course:
        """Async: Create a new course"""
        db_course = Course(
            code=course_data.code,
            title=course_data.title,
            description=course_data.description,
            department=course_data.department,
            level=course_data.level,
            duration=course_data.duration,
            tags=course_data.tags,
            thumbnail=course_data.thumbnail,
            instructor_id=instructor_id
        )

        db.add(db_course)
        await db.commit()
        await db.refresh(db_course)
        return db_course

    @staticmethod
    async def update_course(
        db: AsyncSession,
        course_id: str,
        course_update: CourseUpdate,
        instructor_id: str
    ) -> Optional[Course]:
        """Async: Update course"""
        result = await db.execute(select(Course).filter(
            Course.id == course_id,
            Course.instructor_id == instructor_id
        ))
        course = result.scalar_one_or_none()

        if not course:
            return None

        update_data = course_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        await db.commit()
        await db.refresh(course)
        return course

    @staticmethod
    async def delete_course(db: AsyncSession, course_id: str, user_role: str) -> bool:
        """Async: Soft delete course"""
        if user_role != "admin":
            return False

        result = await db.execute(select(Course).filter(Course.id == course_id))
        course = result.scalar_one_or_none()
        if course:
            course.is_active = False
            await db.commit()
            return True
        return False

    @staticmethod
    async def enroll_user(db: AsyncSession, user_id: str, course_id: str) -> Optional[Enrollment]:
        """Async: Enroll user in course"""
        # Check if already enrolled
        existing_result = await db.execute(select(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ))
        existing = existing_result.scalar_one_or_none()

        if existing:
            return None

        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id
        )

        db.add(enrollment)
        await db.commit()
        await db.refresh(enrollment)
        return enrollment

    @staticmethod
    async def unenroll_user(db: AsyncSession, user_id: str, course_id: str) -> bool:
        """Async: Unenroll user from course"""
        result = await db.execute(select(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ))
        enrollment = result.scalar_one_or_none()

        if enrollment:
            await db.delete(enrollment)
            await db.commit()
            return True
        return False

    @staticmethod
    async def get_user_enrollments(db: AsyncSession, user_id: str) -> List[Enrollment]:
        """Async: Get user enrollments"""
        result = await db.execute(select(Enrollment).filter(Enrollment.user_id == user_id))
        return result.scalars().all()

    @staticmethod
    async def get_course_modules(db: AsyncSession, course_id: str) -> List[Module]:
        """Async: Get course modules"""
        result = await db.execute(select(Module).filter(
            Module.course_id == course_id
        ).order_by(Module.order))
        return result.scalars().all()

    @staticmethod
    async def get_module_topics(db: AsyncSession, module_id: str) -> List[Topic]:
        """Async: Get module topics"""
        result = await db.execute(select(Topic).filter(
            Topic.module_id == module_id
        ).order_by(Topic.order))
        return result.scalars().all()

    @staticmethod
    async def get_topic_by_id(db: AsyncSession, topic_id: str) -> Optional[Topic]:
        """Async: Get topic by ID"""
        result = await db.execute(select(Topic).filter(Topic.id == topic_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def check_user_enrollment(db: AsyncSession, user_id: str, course_id: str) -> bool:
        """Async: Check if user is enrolled in course"""
        result = await db.execute(select(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ))
        enrollment = result.scalar_one_or_none()
        return enrollment is not None

    @staticmethod
    async def get_courses_with_enrollment_status(
        db: AsyncSession,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        level: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """Async: Get courses with enrollment status for user"""
        query = select(Course).filter(Course.is_active == True)

        if department:
            query = query.filter(Course.department == department)
        if level:
            query = query.filter(Course.level == level)
        if search:
            query = query.filter(
                or_(
                    Course.title.contains(search),
                    Course.description.contains(search),
                    Course.code.contains(search)
                )
            )

        # Get total count
        count_result = await db.execute(select(func.count(Course.id)).filter(Course.is_active == True))
        total = count_result.scalar() or 0

        # Get paginated results
        result = await db.execute(query.offset(skip).limit(limit))
        courses = result.scalars().all()

        # Add enrollment status to each course
        courses_with_status = []
        for course in courses:
            # Count enrollments for this course
            enrollment_count_result = await db.execute(select(func.count(Enrollment.id)).filter(
                Enrollment.course_id == course.id
            ))
            enrollment_count = enrollment_count_result.scalar() or 0

            course_dict = {
                'id': str(course.id),
                'code': course.code,
                'title': course.title,
                'description': course.description,
                'department': course.department,
                'level': course.level,
                'duration': course.duration,
                'tags': course.tags or [],
                'thumbnail': course.thumbnail,
                'instructor_id': str(course.instructor_id),
                'enrollment_count': enrollment_count,
                'rating': 0.0,  # Default rating since it's not in the model
                'is_active': course.is_active,
                'created_at': course.created_at,
                'is_enrolled': False  # Default value
            }

            # Check enrollment status if user is provided
            if user_id:
                course_dict['is_enrolled'] = await CourseService.check_user_enrollment(
                    db, user_id, str(course.id)
                )

            courses_with_status.append(course_dict)

        return courses_with_status, total
