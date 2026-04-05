"""
Lecturer service for course and student management - Async compatible
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import func, and_, select
from app.models.course import Course, Module, Topic, Enrollment
from app.models.progress import Progress, TopicProgress
from app.models.user import User
from app.models.notification import Notification
from app.schemas.course import ModuleCreate, TopicCreate
from datetime import datetime, timedelta
import uuid


class LecturerService:
    @staticmethod
    async def get_lecturer_courses(
        db: AsyncSession,
        lecturer_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[Course], int]:
        """Async: Get all courses by a lecturer"""
        query = select(Course).filter(Course.instructor_id == lecturer_id)

        if status:
            if status == "active":
                query = query.filter(Course.is_active == True)
            elif status == "draft":
                query = query.filter(Course.is_active == False)

        count_result = await db.execute(select(func.count(Course.id)).filter(Course.instructor_id == lecturer_id))
        total = count_result.scalar() or 0

        result = await db.execute(query.offset(skip).limit(limit))
        courses = result.scalars().all()

        return courses, total

    @staticmethod
    async def publish_course(db: AsyncSession, course_id: str, lecturer_id: str) -> bool:
        """Async: Publish a course"""
        result = await db.execute(select(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ))
        course = result.scalar_one_or_none()

        if not course:
            return False

        course.is_active = True
        await db.commit()
        return True

    @staticmethod
    async def unpublish_course(db: AsyncSession, course_id: str, lecturer_id: str) -> bool:
        """Async: Unpublish a course"""
        result = await db.execute(select(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ))
        course = result.scalar_one_or_none()

        if not course:
            return False

        course.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def create_module(
        db: AsyncSession,
        course_id: str,
        module_data: ModuleCreate,
        lecturer_id: str
    ) -> Optional[Module]:
        """Async: Create a new module"""
        # Verify course ownership
        result = await db.execute(select(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ))
        course = result.scalar_one_or_none()

        if not course:
            return None

        module = Module(
            title=module_data.title,
            description=module_data.description,
            order=module_data.order,
            course_id=course_id,
            available_at=module_data.available_at
        )

        db.add(module)
        await db.commit()

        # Return with relationships loaded to avoid MissingGreenlet in Pydantic serialization
        stmt = select(Module).filter(Module.id == module.id).options(selectinload(Module.topics))
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def update_module(
        db: AsyncSession,
        module_id: str,
        module_data: dict,
        lecturer_id: str
    ) -> Optional[Module]:
        """Async: Update a module"""
        result = await db.execute(select(Module).join(Course).filter(
            Module.id == module_id,
            Course.instructor_id == lecturer_id
        ))
        module = result.scalar_one_or_none()

        if not module:
            return None

        for key, value in module_data.items():
            if hasattr(module, key):
                setattr(module, key, value)

        await db.commit()

        # Return with relationships loaded to avoid MissingGreenlet in Pydantic serialization
        stmt = select(Module).filter(Module.id == module.id).options(selectinload(Module.topics))
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def delete_module(db: AsyncSession, module_id: str, lecturer_id: str) -> bool:
        """Async: Delete a module"""
        result = await db.execute(select(Module).join(Course).filter(
            Module.id == module_id,
            Course.instructor_id == lecturer_id
        ))
        module = result.scalar_one_or_none()

        if not module:
            return False

        await db.delete(module)
        await db.commit()
        return True

    @staticmethod
    async def reorder_modules(
        db: AsyncSession,
        course_id: str,
        module_orders: List[dict],
        lecturer_id: str
    ) -> bool:
        """Async: Reorder modules"""
        result = await db.execute(select(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ))
        course = result.scalar_one_or_none()

        if not course:
            return False

        for order_data in module_orders:
            result = await db.execute(select(Module).filter(
                Module.id == order_data["module_id"],
                Module.course_id == course_id
            ))
            module = result.scalar_one_or_none()

            if module:
                module.order = order_data["order"]

        await db.commit()
        return True

    @staticmethod
    async def create_topic(
        db: AsyncSession,
        module_id: str,
        topic_data: TopicCreate,
        lecturer_id: str
    ) -> Optional[Topic]:
        """Async: Create a new topic"""
        # Verify module ownership through course
        result = await db.execute(select(Module).join(Course).filter(
            Module.id == module_id,
            Course.instructor_id == lecturer_id
        ))
        module = result.scalar_one_or_none()

        if not module:
            return None

        topic = Topic(
            title=topic_data.title,
            description=topic_data.description,
            duration=topic_data.duration,
            order=topic_data.order,
            content_type=topic_data.content_type,
            content=topic_data.content,
            media_files=topic_data.media_files,
            prerequisites=topic_data.prerequisites,
            learning_objectives=topic_data.learning_objectives,
            module_id=module_id,
            available_at=topic_data.available_at
        )

        db.add(topic)
        await db.commit()

        # Return with relationships loaded to avoid MissingGreenlet in Pydantic serialization
        stmt = select(Topic).filter(Topic.id == topic.id).options(selectinload(Topic.assessments))
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def update_topic(
        db: AsyncSession,
        topic_id: str,
        topic_data: dict,
        lecturer_id: str
    ) -> Optional[Topic]:
        """Async: Update a topic"""
        result = await db.execute(select(Topic).join(Module).join(Course).filter(
            Topic.id == topic_id,
            Course.instructor_id == lecturer_id
        ))
        topic = result.scalar_one_or_none()

        if not topic:
            return None

        for key, value in topic_data.items():
            if hasattr(topic, key):
                setattr(topic, key, value)

        await db.commit()

        # Return with relationships loaded to avoid MissingGreenlet in Pydantic serialization
        stmt = select(Topic).filter(Topic.id == topic.id).options(selectinload(Topic.assessments))
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def delete_topic(db: AsyncSession, topic_id: str, lecturer_id: str) -> bool:
        """Async: Delete a topic"""
        result = await db.execute(select(Topic).join(Module).join(Course).filter(
            Topic.id == topic_id,
            Course.instructor_id == lecturer_id
        ))
        topic = result.scalar_one_or_none()

        if not topic:
            return False

        await db.delete(topic)
        await db.commit()
        return True

    @staticmethod
    async def reorder_topics(
        db: AsyncSession,
        module_id: str,
        topic_orders: List[dict],
        lecturer_id: str
    ) -> bool:
        """Async: Reorder topics"""
        result = await db.execute(select(Module).join(Course).filter(
            Module.id == module_id,
            Course.instructor_id == lecturer_id
        ))
        module = result.scalar_one_or_none()

        if not module:
            return False

        for order_data in topic_orders:
            result = await db.execute(select(Topic).filter(
                Topic.id == order_data["topic_id"],
                Topic.module_id == module_id
            ))
            topic = result.scalar_one_or_none()

            if topic:
                topic.order = order_data["order"]

        await db.commit()
        return True

    @staticmethod
    async def get_course_enrollments(
        db: AsyncSession,
        course_id: str,
        lecturer_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Optional[Tuple[List[dict], int]]:
        """Async: Get enrollments for a course"""
        # Verify course ownership
        result = await db.execute(select(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ))
        course = result.scalar_one_or_none()

        if not course:
            return None

        query = select(Enrollment).filter(Enrollment.course_id == course_id)

        if status:
            query = query.filter(Enrollment.status == status)

        count_result = await db.execute(select(func.count(Enrollment.id)).filter(Enrollment.course_id == course_id))
        total = count_result.scalar() or 0

        result = await db.execute(query.offset(skip).limit(limit))
        enrollments = result.scalars().all()

        # Enrich with user and progress data
        result_list = []
        for enrollment in enrollments:
            user_result = await db.execute(select(User).filter(User.id == enrollment.user_id))
            user = user_result.scalar_one_or_none()

            progress_result = await db.execute(select(Progress).filter(
                Progress.user_id == enrollment.user_id,
                Progress.course_id == course_id
            ))
            progress = progress_result.scalar_one_or_none()

            result_list.append({
                "id": str(enrollment.id),
                "user": {
                    "id": str(user.id),
                    "full_name": user.full_name,
                    "email": user.email
                } if user else None,
                "enrolled_at": enrollment.enrollment_date,
                "progress_percentage": progress.completion_percentage if progress else 0,
                "status": enrollment.status
            })

        return result_list, total

    @staticmethod
    async def get_course_analytics(
        db: AsyncSession,
        course_id: str,
        lecturer_id: str
    ) -> Optional[Dict[str, Any]]:
        """Async: Get analytics for a course"""
        result = await db.execute(select(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ))
        course = result.scalar_one_or_none()

        if not course:
            return None

        # Get enrollment stats
        total_result = await db.execute(select(func.count(Enrollment.id)).filter(
            Enrollment.course_id == course_id
        ))
        total_enrollments = total_result.scalar() or 0

        active_result = await db.execute(select(func.count(Enrollment.id)).filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "active"
        ))
        active_students = active_result.scalar() or 0

        completed_result = await db.execute(select(func.count(Enrollment.id)).filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "completed"
        ))
        completed_students = completed_result.scalar() or 0

        completion_rate = (completed_students / total_enrollments * 100) if total_enrollments > 0 else 0

        # Get average progress
        avg_result = await db.execute(select(func.avg(Progress.completion_percentage)).filter(
            Progress.course_id == course_id
        ))
        avg_progress = avg_result.scalar() or 0

        # Get struggling students (progress < 30%)
        struggle_result = await db.execute(select(Progress).filter(
            Progress.course_id == course_id,
            Progress.completion_percentage < 30
        ).limit(10))
        struggling = struggle_result.scalars().all()

        struggling_students = []
        for p in struggling:
            user_result = await db.execute(select(User).filter(User.id == p.user_id))
            user = user_result.scalar_one_or_none()
            if user:
                struggling_students.append({
                    "user_id": str(p.user_id),
                    "full_name": user.full_name,
                    "progress": p.completion_percentage,
                    "average_score": 0  # Placeholder
                })

        return {
            "total_enrollments": total_enrollments,
            "active_students": active_students,
            "completion_rate": round(completion_rate, 2),
            "average_progress": round(avg_progress, 2),
            "average_quiz_score": 78,  # Placeholder
            "struggling_students": struggling_students
        }

    @staticmethod
    async def get_student_progress(
        db: AsyncSession,
        course_id: str,
        student_id: str,
        lecturer_id: str
    ) -> Optional[Dict[str, Any]]:
        """Async: Get specific student's progress"""
        result = await db.execute(select(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ))
        course = result.scalar_one_or_none()

        if not course:
            return None

        student_result = await db.execute(select(User).filter(User.id == student_id))
        student = student_result.scalar_one_or_none()

        enrollment_result = await db.execute(select(Enrollment).filter(
            Enrollment.user_id == student_id,
            Enrollment.course_id == course_id
        ))
        enrollment = enrollment_result.scalar_one_or_none()

        progress_result = await db.execute(select(Progress).filter(
            Progress.user_id == student_id,
            Progress.course_id == course_id
        ))
        progress = progress_result.scalar_one_or_none()

        if not student or not enrollment:
            return None

        topic_progress_result = await db.execute(select(TopicProgress).filter(
            TopicProgress.progress_id == progress.id
        )) if progress else None
        topic_progress = topic_progress_result.scalars().all() if topic_progress_result else []

        return {
            "student": {
                "id": str(student.id),
                "full_name": student.full_name,
                "email": student.email
            },
            "enrollment": {
                "enrolled_at": enrollment.enrollment_date,
                "status": enrollment.status
            },
            "topic_progress": [
                {
                    "topic_id": str(tp.topic_id),
                    "status": tp.status,
                    "time_spent": tp.time_spent,
                    "completed_at": tp.completed_at
                }
                for tp in topic_progress
            ]
        }

    @staticmethod
    async def get_class_demographics(db: AsyncSession, lecturer_id: str) -> Dict[str, Any]:
        """Async: Get demographics of all students in lecturer's courses"""
        # Get all students enrolled in lecturer's courses
        result = await db.execute(select(User).join(Enrollment).join(Course).filter(
            Course.instructor_id == lecturer_id,
            User.role == "student"
        ).distinct())
        students = result.scalars().all()

        total_students = len(students)

        # Count by department
        by_department = {}
        for student in students:
            dept = student.department or "Unknown"
            by_department[dept] = by_department.get(dept, 0) + 1

        # Count by disability
        by_disability = {}
        for student in students:
            if student.disability_info and student.disability_info.get("has_disability"):
                for disability_type in student.disability_info.get("disability_type", []):
                    by_disability[disability_type] = by_disability.get(disability_type, 0) + 1

        return {
            "total_students": total_students,
            "by_department": [
                {"department": k, "count": v}
                for k, v in by_department.items()
            ],
            "by_disability": [
                {"type": k, "count": v}
                for k, v in by_disability.items()
            ]
        }

    @staticmethod
    async def get_lecturer_alerts(db: AsyncSession, lecturer_id: str) -> List[Dict[str, Any]]:
        """Async: Get alerts about students needing attention"""
        alerts = []

        # Get courses
        result = await db.execute(select(Course).filter(Course.instructor_id == lecturer_id))
        courses = result.scalars().all()

        for course in courses:
            # Find students who haven't accessed course in 7 days
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            inactive_result = await db.execute(select(Progress).join(User).filter(
                Progress.course_id == course.id,
                Progress.last_accessed_at < seven_days_ago
            ))
            inactive_progress = inactive_result.scalars().all()

            for progress in inactive_progress:
                user_result = await db.execute(select(User).filter(User.id == progress.user_id))
                user = user_result.scalar_one_or_none()
                if user:
                    alerts.append({
                        "id": str(uuid.uuid4()),
                        "type": "struggling_student",
                        "severity": "high",
                        "student": {
                            "id": str(user.id),
                            "full_name": user.full_name
                        },
                        "course": {
                            "id": str(course.id),
                            "title": course.title
                        },
                        "message": f"Student has not accessed course in 7 days",
                        "created_at": datetime.utcnow()
                    })

        return alerts[:20]  # Limit to 20 alerts

    @staticmethod
    async def send_notification_to_students(
        db: AsyncSession,
        lecturer_id: str,
        course_id: str,
        recipient_type: str,
        student_ids: List[str],
        title: str,
        message: str,
        notification_type: str
    ) -> bool:
        """Async: Send notification to students"""
        # Verify course ownership
        result = await db.execute(select(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ))
        course = result.scalar_one_or_none()

        if not course:
            return False

        # Determine recipients
        recipients = []
        if recipient_type == "all":
            enroll_result = await db.execute(select(Enrollment).filter(
                Enrollment.course_id == course_id,
                Enrollment.status == "active"
            ))
            enrollments = enroll_result.scalars().all()
            recipients = [e.user_id for e in enrollments]
        elif recipient_type == "specific":
            recipients = student_ids
        elif recipient_type == "struggling":
            # Get students with progress < 30%
            prog_result = await db.execute(select(Progress).filter(
                Progress.course_id == course_id,
                Progress.completion_percentage < 30
            ))
            progress_records = prog_result.scalars().all()
            recipients = [p.user_id for p in progress_records]

        # Create notifications
        for user_id in recipients:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                action_url=f"/courses/{course_id}"
            )
            db.add(notification)

        await db.commit()
        return True


    @staticmethod
    async def create_quiz(
        db: AsyncSession,
        quiz_data,
        lecturer_id: str
    ):
        """Async: Create a new quiz"""
        from app.models.assessment import Quiz
        from app.models.course import Topic, Module, Course

        # Verify topic ownership through course
        result = await db.execute(select(Topic).join(Module).join(Course).filter(
            Topic.id == quiz_data.topic_id,
            Course.instructor_id == lecturer_id
        ))
        topic = result.scalar_one_or_none()

        if not topic:
            return None

        quiz = Quiz(
            title=quiz_data.title,
            description=quiz_data.description,
            topic_id=quiz_data.topic_id,
            time_limit=quiz_data.time_limit,
            passing_score=quiz_data.passing_score,
            max_attempts=quiz_data.max_attempts,
            questions=[q.dict() for q in quiz_data.questions]
        )

        db.add(quiz)
        await db.commit()
        await db.refresh(quiz)
        return quiz

    @staticmethod
    async def update_quiz(
        db: AsyncSession,
        quiz_id: str,
        quiz_data,
        lecturer_id: str
    ):
        """Async: Update a quiz"""
        from app.models.assessment import Quiz
        from app.models.course import Topic, Module, Course

        result = await db.execute(select(Quiz).join(Topic).join(Module).join(Course).filter(
            Quiz.id == quiz_id,
            Course.instructor_id == lecturer_id
        ))
        quiz = result.scalar_one_or_none()

        if not quiz:
            return None

        update_data = quiz_data.dict(exclude_unset=True)
        if 'questions' in update_data:
            update_data['questions'] = [q.dict() if hasattr(q, 'dict') else q for q in update_data['questions']]

        for key, value in update_data.items():
            if hasattr(quiz, key):
                setattr(quiz, key, value)

        await db.commit()
        await db.refresh(quiz)
        return quiz

    @staticmethod
    async def delete_quiz(db: AsyncSession, quiz_id: str, lecturer_id: str) -> bool:
        """Async: Delete a quiz"""
        from app.models.assessment import Quiz
        from app.models.course import Topic, Module, Course

        result = await db.execute(select(Quiz).join(Topic).join(Module).join(Course).filter(
            Quiz.id == quiz_id,
            Course.instructor_id == lecturer_id
        ))
        quiz = result.scalar_one_or_none()

        if not quiz:
            return False

        await db.delete(quiz)
        await db.commit()
        return True
