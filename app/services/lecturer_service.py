"""
Lecturer service for course and student management
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.course import Course, Module, Topic, Enrollment
from app.models.progress import Progress, TopicProgress
from app.models.user import User
from app.models.notification import Notification
from app.schemas.course import ModuleCreate, TopicCreate
from datetime import datetime, timedelta
import uuid


class LecturerService:
    @staticmethod
    def get_lecturer_courses(
        db: Session,
        lecturer_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Tuple[List[Course], int]:
        """Get all courses by a lecturer"""
        query = db.query(Course).filter(Course.instructor_id == lecturer_id)
        
        if status:
            if status == "active":
                query = query.filter(Course.is_active == True)
            elif status == "draft":
                query = query.filter(Course.is_active == False)
        
        total = query.count()
        courses = query.offset(skip).limit(limit).all()
        
        return courses, total

    @staticmethod
    def publish_course(db: Session, course_id: str, lecturer_id: str) -> bool:
        """Publish a course"""
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not course:
            return False
        
        course.is_active = True
        db.commit()
        return True

    @staticmethod
    def unpublish_course(db: Session, course_id: str, lecturer_id: str) -> bool:
        """Unpublish a course"""
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not course:
            return False
        
        course.is_active = False
        db.commit()
        return True

    @staticmethod
    def create_module(
        db: Session,
        course_id: str,
        module_data: ModuleCreate,
        lecturer_id: str
    ) -> Optional[Module]:
        """Create a new module"""
        # Verify course ownership
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not course:
            return None
        
        module = Module(
            title=module_data.title,
            description=module_data.description,
            order=module_data.order,
            course_id=course_id
        )
        
        db.add(module)
        db.commit()
        db.refresh(module)
        return module

    @staticmethod
    def update_module(
        db: Session,
        module_id: str,
        module_data: dict,
        lecturer_id: str
    ) -> Optional[Module]:
        """Update a module"""
        module = db.query(Module).join(Course).filter(
            Module.id == module_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not module:
            return None
        
        for key, value in module_data.items():
            if hasattr(module, key):
                setattr(module, key, value)
        
        db.commit()
        db.refresh(module)
        return module

    @staticmethod
    def delete_module(db: Session, module_id: str, lecturer_id: str) -> bool:
        """Delete a module"""
        module = db.query(Module).join(Course).filter(
            Module.id == module_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not module:
            return False
        
        db.delete(module)
        db.commit()
        return True

    @staticmethod
    def reorder_modules(
        db: Session,
        course_id: str,
        module_orders: List[dict],
        lecturer_id: str
    ) -> bool:
        """Reorder modules"""
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not course:
            return False
        
        for order_data in module_orders:
            module = db.query(Module).filter(
                Module.id == order_data["module_id"],
                Module.course_id == course_id
            ).first()
            
            if module:
                module.order = order_data["order"]
        
        db.commit()
        return True

    @staticmethod
    def create_topic(
        db: Session,
        module_id: str,
        topic_data: TopicCreate,
        lecturer_id: str
    ) -> Optional[Topic]:
        """Create a new topic"""
        # Verify module ownership through course
        module = db.query(Module).join(Course).filter(
            Module.id == module_id,
            Course.instructor_id == lecturer_id
        ).first()
        
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
            module_id=module_id
        )
        
        db.add(topic)
        db.commit()
        db.refresh(topic)
        return topic

    @staticmethod
    def update_topic(
        db: Session,
        topic_id: str,
        topic_data: dict,
        lecturer_id: str
    ) -> Optional[Topic]:
        """Update a topic"""
        topic = db.query(Topic).join(Module).join(Course).filter(
            Topic.id == topic_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not topic:
            return None
        
        for key, value in topic_data.items():
            if hasattr(topic, key):
                setattr(topic, key, value)
        
        db.commit()
        db.refresh(topic)
        return topic

    @staticmethod
    def delete_topic(db: Session, topic_id: str, lecturer_id: str) -> bool:
        """Delete a topic"""
        topic = db.query(Topic).join(Module).join(Course).filter(
            Topic.id == topic_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not topic:
            return False
        
        db.delete(topic)
        db.commit()
        return True

    @staticmethod
    def reorder_topics(
        db: Session,
        module_id: str,
        topic_orders: List[dict],
        lecturer_id: str
    ) -> bool:
        """Reorder topics"""
        module = db.query(Module).join(Course).filter(
            Module.id == module_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not module:
            return False
        
        for order_data in topic_orders:
            topic = db.query(Topic).filter(
                Topic.id == order_data["topic_id"],
                Topic.module_id == module_id
            ).first()
            
            if topic:
                topic.order = order_data["order"]
        
        db.commit()
        return True

    @staticmethod
    def get_course_enrollments(
        db: Session,
        course_id: str,
        lecturer_id: str,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> Optional[Tuple[List[dict], int]]:
        """Get enrollments for a course"""
        # Verify course ownership
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not course:
            return None
        
        query = db.query(Enrollment).filter(Enrollment.course_id == course_id)
        
        if status:
            query = query.filter(Enrollment.status == status)
        
        total = query.count()
        enrollments = query.offset(skip).limit(limit).all()
        
        # Enrich with user and progress data
        result = []
        for enrollment in enrollments:
            user = db.query(User).filter(User.id == enrollment.user_id).first()
            progress = db.query(Progress).filter(
                Progress.user_id == enrollment.user_id,
                Progress.course_id == course_id
            ).first()
            
            result.append({
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
        
        return result, total

    @staticmethod
    def get_course_analytics(
        db: Session,
        course_id: str,
        lecturer_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get analytics for a course"""
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not course:
            return None
        
        # Get enrollment stats
        total_enrollments = db.query(func.count(Enrollment.id)).filter(
            Enrollment.course_id == course_id
        ).scalar()
        
        active_students = db.query(func.count(Enrollment.id)).filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "active"
        ).scalar()
        
        completed_students = db.query(func.count(Enrollment.id)).filter(
            Enrollment.course_id == course_id,
            Enrollment.status == "completed"
        ).scalar()
        
        completion_rate = (completed_students / total_enrollments * 100) if total_enrollments > 0 else 0
        
        # Get average progress
        avg_progress = db.query(func.avg(Progress.completion_percentage)).filter(
            Progress.course_id == course_id
        ).scalar() or 0
        
        # Get struggling students (progress < 30%)
        struggling = db.query(Progress).join(User).filter(
            Progress.course_id == course_id,
            Progress.completion_percentage < 30
        ).limit(10).all()
        
        struggling_students = [
            {
                "user_id": str(p.user_id),
                "full_name": db.query(User).filter(User.id == p.user_id).first().full_name,
                "progress": p.completion_percentage,
                "average_score": 0  # Placeholder
            }
            for p in struggling
        ]
        
        return {
            "total_enrollments": total_enrollments,
            "active_students": active_students,
            "completion_rate": round(completion_rate, 2),
            "average_progress": round(avg_progress, 2),
            "average_quiz_score": 78,  # Placeholder
            "struggling_students": struggling_students
        }

    @staticmethod
    def get_student_progress(
        db: Session,
        course_id: str,
        student_id: str,
        lecturer_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific student's progress"""
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not course:
            return None
        
        student = db.query(User).filter(User.id == student_id).first()
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == student_id,
            Enrollment.course_id == course_id
        ).first()
        progress = db.query(Progress).filter(
            Progress.user_id == student_id,
            Progress.course_id == course_id
        ).first()
        
        if not student or not enrollment:
            return None
        
        topic_progress = db.query(TopicProgress).filter(
            TopicProgress.progress_id == progress.id
        ).all() if progress else []
        
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
    def get_class_demographics(db: Session, lecturer_id: str) -> Dict[str, Any]:
        """Get demographics of all students in lecturer's courses"""
        # Get all students enrolled in lecturer's courses
        students = db.query(User).join(Enrollment).join(Course).filter(
            Course.instructor_id == lecturer_id,
            User.role == "student"
        ).distinct().all()
        
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
    def get_lecturer_alerts(db: Session, lecturer_id: str) -> List[Dict[str, Any]]:
        """Get alerts about students needing attention"""
        alerts = []
        
        # Get courses
        courses = db.query(Course).filter(Course.instructor_id == lecturer_id).all()
        
        for course in courses:
            # Find students who haven't accessed course in 7 days
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            inactive_progress = db.query(Progress).join(User).filter(
                Progress.course_id == course.id,
                Progress.last_accessed_at < seven_days_ago
            ).all()
            
            for progress in inactive_progress:
                user = db.query(User).filter(User.id == progress.user_id).first()
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
    def send_notification_to_students(
        db: Session,
        lecturer_id: str,
        course_id: str,
        recipient_type: str,
        student_ids: List[str],
        title: str,
        message: str,
        notification_type: str
    ) -> bool:
        """Send notification to students"""
        # Verify course ownership
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not course:
            return False
        
        # Determine recipients
        recipients = []
        if recipient_type == "all":
            enrollments = db.query(Enrollment).filter(
                Enrollment.course_id == course_id,
                Enrollment.status == "active"
            ).all()
            recipients = [e.user_id for e in enrollments]
        elif recipient_type == "specific":
            recipients = student_ids
        elif recipient_type == "struggling":
            # Get students with progress < 30%
            progress_records = db.query(Progress).filter(
                Progress.course_id == course_id,
                Progress.completion_percentage < 30
            ).all()
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
        
        db.commit()
        return True


    @staticmethod
    def create_quiz(
        db: Session,
        quiz_data,
        lecturer_id: str
    ):
        """Create a new quiz"""
        from app.models.assessment import Quiz
        from app.models.course import Topic, Module, Course
        
        # Verify topic ownership through course
        topic = db.query(Topic).join(Module).join(Course).filter(
            Topic.id == quiz_data.topic_id,
            Course.instructor_id == lecturer_id
        ).first()
        
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
        db.commit()
        db.refresh(quiz)
        return quiz

    @staticmethod
    def update_quiz(
        db: Session,
        quiz_id: str,
        quiz_data,
        lecturer_id: str
    ):
        """Update a quiz"""
        from app.models.assessment import Quiz
        from app.models.course import Topic, Module, Course
        
        quiz = db.query(Quiz).join(Topic).join(Module).join(Course).filter(
            Quiz.id == quiz_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not quiz:
            return None
        
        update_data = quiz_data.dict(exclude_unset=True)
        if 'questions' in update_data:
            update_data['questions'] = [q.dict() if hasattr(q, 'dict') else q for q in update_data['questions']]
        
        for key, value in update_data.items():
            if hasattr(quiz, key):
                setattr(quiz, key, value)
        
        db.commit()
        db.refresh(quiz)
        return quiz

    @staticmethod
    def delete_quiz(db: Session, quiz_id: str, lecturer_id: str) -> bool:
        """Delete a quiz"""
        from app.models.assessment import Quiz
        from app.models.course import Topic, Module, Course
        
        quiz = db.query(Quiz).join(Topic).join(Module).join(Course).filter(
            Quiz.id == quiz_id,
            Course.instructor_id == lecturer_id
        ).first()
        
        if not quiz:
            return False
        
        db.delete(quiz)
        db.commit()
        return True
