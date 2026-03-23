"""
Course management service
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models.course import Course, Module, Topic, Enrollment
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate
import uuid


class CourseService:
    @staticmethod
    def get_courses(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        level: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Course], int]:
        query = db.query(Course).filter(Course.is_active == True)
        
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
        
        total = query.count()
        courses = query.offset(skip).limit(limit).all()
        
        return courses, total

    @staticmethod
    def get_course_by_id(db: Session, course_id: str) -> Optional[Course]:
        return db.query(Course).filter(
            Course.id == course_id,
            Course.is_active == True
        ).first()

    @staticmethod
    def create_course(db: Session, course_data: CourseCreate, instructor_id: str) -> Course:
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
        db.commit()
        db.refresh(db_course)
        return db_course

    @staticmethod
    def update_course(
        db: Session,
        course_id: str,
        course_update: CourseUpdate,
        instructor_id: str
    ) -> Optional[Course]:
        course = db.query(Course).filter(
            Course.id == course_id,
            Course.instructor_id == instructor_id
        ).first()
        
        if not course:
            return None

        update_data = course_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        db.commit()
        db.refresh(course)
        return course

    @staticmethod
    def delete_course(db: Session, course_id: str, user_role: str) -> bool:
        if user_role != "admin":
            return False
            
        course = db.query(Course).filter(Course.id == course_id).first()
        if course:
            course.is_active = False
            db.commit()
            return True
        return False

    @staticmethod
    def enroll_user(db: Session, user_id: str, course_id: str) -> Optional[Enrollment]:
        # Check if already enrolled
        existing = db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first()
        
        if existing:
            return None

        enrollment = Enrollment(
            user_id=user_id,
            course_id=course_id
        )
        
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        return enrollment

    @staticmethod
    def unenroll_user(db: Session, user_id: str, course_id: str) -> bool:
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first()
        
        if enrollment:
            db.delete(enrollment)
            db.commit()
            return True
        return False

    @staticmethod
    def get_user_enrollments(db: Session, user_id: str) -> List[Enrollment]:
        return db.query(Enrollment).filter(Enrollment.user_id == user_id).all()

    @staticmethod
    def get_course_modules(db: Session, course_id: str) -> List[Module]:
        return db.query(Module).filter(
            Module.course_id == course_id
        ).order_by(Module.order).all()

    @staticmethod
    def get_module_topics(db: Session, module_id: str) -> List[Topic]:
        return db.query(Topic).filter(
            Topic.module_id == module_id
        ).order_by(Topic.order).all()

    @staticmethod
    def get_topic_by_id(db: Session, topic_id: str) -> Optional[Topic]:
        return db.query(Topic).filter(Topic.id == topic_id).first()

    @staticmethod
    def check_user_enrollment(db: Session, user_id: str, course_id: str) -> bool:
        """Check if a user is enrolled in a specific course"""
        enrollment = db.query(Enrollment).filter(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id
        ).first()
        return enrollment is not None

    @staticmethod
    def get_courses_with_enrollment_status(
        db: Session,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        department: Optional[str] = None,
        level: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get courses with enrollment status for a specific user"""
        query = db.query(Course).filter(Course.is_active == True)

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

        total = query.count()
        courses = query.offset(skip).limit(limit).all()

        # Add enrollment status to each course
        courses_with_status = []
        for course in courses:
            # Count enrollments for this course
            enrollment_count = db.query(Enrollment).filter(
                Enrollment.course_id == course.id
            ).count()
            
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
                course_dict['is_enrolled'] = CourseService.check_user_enrollment(
                    db, user_id, str(course.id)
                )

            courses_with_status.append(course_dict)

        return courses_with_status, total
