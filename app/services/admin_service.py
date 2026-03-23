"""
Admin service for system management
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models.user import User
from app.models.course import Course, Enrollment
from app.models.department import Department
from app.models.announcement import Announcement
from app.models.audit import AuditLog
from app.models.analytics import Analytics, AccessibilityUsage
from app.services.auth_service import AuthService
from datetime import datetime, timedelta
import uuid


class AdminService:
    @staticmethod
    def get_all_users(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """Get all users with filters"""
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        
        if search:
            query = query.filter(
                or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.student_id.ilike(f"%{search}%")
                )
            )
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total

    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        """Create a new user"""
        user = User(
            full_name=user_data["full_name"],
            email=user_data["email"],
            hashed_password=AuthService.get_password_hash(user_data["password"]),
            role=user_data.get("role", "student"),
            department=user_data.get("department"),
            student_id=user_data.get("student_id"),
            is_active=user_data.get("is_active", True)
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user_id: str, user_data: dict) -> Optional[User]:
        """Update a user"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return None
        
        for key, value in user_data.items():
            if key == "password":
                user.hashed_password = AuthService.get_password_hash(value)
            elif hasattr(user, key):
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: str) -> bool:
        """Delete a user"""
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def bulk_user_action(
        db: Session,
        user_ids: List[str],
        action: str,
        data: Optional[dict] = None
    ) -> bool:
        """Perform bulk action on users"""
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        
        if not users:
            return False
        
        if action == "activate":
            for user in users:
                user.is_active = True
        elif action == "deactivate":
            for user in users:
                user.is_active = False
        elif action == "delete":
            for user in users:
                db.delete(user)
        elif action == "update_role" and data:
            for user in users:
                user.role = data.get("role")
        
        db.commit()
        return True

    @staticmethod
    def get_all_courses_admin(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        department: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        """Get all courses with admin view"""
        query = db.query(Course)
        
        if status == "active":
            query = query.filter(Course.is_active == True)
        elif status == "inactive":
            query = query.filter(Course.is_active == False)
        
        if department:
            query = query.filter(Course.department == department)
        
        total = query.count()
        courses = query.offset(skip).limit(limit).all()
        
        result = []
        for course in courses:
            instructor = db.query(User).filter(User.id == course.instructor_id).first()
            enrollment_count = db.query(func.count(Enrollment.id)).filter(
                Enrollment.course_id == course.id
            ).scalar()
            
            result.append({
                "id": str(course.id),
                "code": course.code,
                "title": course.title,
                "department": course.department,
                "instructor": {
                    "id": str(instructor.id),
                    "full_name": instructor.full_name
                } if instructor else None,
                "enrollment_count": enrollment_count,
                "is_active": course.is_active,
                "created_at": course.created_at
            })
        
        return result, total

    @staticmethod
    def approve_course(db: Session, course_id: str) -> bool:
        """Approve a course"""
        course = db.query(Course).filter(Course.id == course_id).first()
        
        if not course:
            return False
        
        course.is_active = True
        db.commit()
        return True

    @staticmethod
    def reject_course(db: Session, course_id: str) -> bool:
        """Reject a course"""
        course = db.query(Course).filter(Course.id == course_id).first()
        
        if not course:
            return False
        
        course.is_active = False
        db.commit()
        return True

    @staticmethod
    def change_course_status(db: Session, course_id: str, status: str) -> bool:
        """Change course status (draft/published)"""
        course = db.query(Course).filter(Course.id == course_id).first()
        
        if not course:
            return False
        
        # Map status to is_active field
        if status == "published":
            course.is_active = True
        elif status == "draft":
            course.is_active = False
        else:
            return False  # Invalid status
        
        db.commit()
        return True

    @staticmethod
    def feature_course(db: Session, course_id: str, featured: bool) -> bool:
        """Feature or unfeature a course"""
        course = db.query(Course).filter(Course.id == course_id).first()
        
        if not course:
            return False
        
        # Add featured flag to course tags
        tags = course.tags or []
        if featured and "featured" not in tags:
            tags.append("featured")
        elif not featured and "featured" in tags:
            tags.remove("featured")
        
        course.tags = tags
        db.commit()
        return True

    @staticmethod
    def get_system_statistics(db: Session) -> Dict[str, Any]:
        """Get system-wide statistics"""
        total_users = db.query(func.count(User.id)).scalar()
        total_students = db.query(func.count(User.id)).filter(User.role == "student").scalar()
        total_lecturers = db.query(func.count(User.id)).filter(User.role == "lecturer").scalar()
        total_courses = db.query(func.count(Course.id)).scalar()
        active_courses = db.query(func.count(Course.id)).filter(Course.is_active == True).scalar()
        total_enrollments = db.query(func.count(Enrollment.id)).scalar()
        
        # Active users (logged in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = db.query(func.count(User.id)).filter(
            User.last_login >= thirty_days_ago
        ).scalar()
        
        return {
            "total_users": total_users,
            "total_students": total_students,
            "total_lecturers": total_lecturers,
            "active_users": active_users,
            "total_courses": total_courses,
            "active_courses": active_courses,
            "total_enrollments": total_enrollments
        }

    @staticmethod
    def get_accessibility_report(db: Session) -> Dict[str, Any]:
        """Get system-wide accessibility report"""
        # Users with disabilities
        users_with_disabilities = db.query(User).all()
        disability_count = sum(
            1 for u in users_with_disabilities 
            if u.disability_info and u.disability_info.get("hasDisability")
        )
        
        # Accessibility feature usage
        feature_usage = db.query(
            AccessibilityUsage.feature_name,
            func.count(AccessibilityUsage.id).label("usage_count")
        ).group_by(AccessibilityUsage.feature_name).all()
        
        return {
            "users_with_disabilities": disability_count,
            "total_users": db.query(func.count(User.id)).scalar(),
            "feature_usage": [
                {"feature": f.feature_name, "count": f.usage_count}
                for f in feature_usage
            ]
        }

    @staticmethod
    def get_performance_metrics(db: Session) -> Dict[str, Any]:
        """Get system performance metrics"""
        # Average course completion rate
        total_enrollments = db.query(func.count(Enrollment.id)).scalar()
        completed_enrollments = db.query(func.count(Enrollment.id)).filter(
            Enrollment.status == "completed"
        ).scalar()
        
        completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments > 0 else 0
        
        # Average time to complete courses
        # This is a placeholder - would need actual completion time tracking
        avg_completion_time = "8 weeks"
        
        return {
            "completion_rate": round(completion_rate, 2),
            "average_completion_time": avg_completion_time,
            "total_enrollments": total_enrollments,
            "completed_enrollments": completed_enrollments
        }

    @staticmethod
    def get_system_health(db: Session) -> Dict[str, Any]:
        """Get system health status"""
        try:
            # Test database connection
            db.execute("SELECT 1")
            db_status = "healthy"
        except:
            db_status = "unhealthy"
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "database": db_status,
            "timestamp": datetime.utcnow()
        }

    @staticmethod
    def create_announcement(db: Session, announcement_data: dict, author_id: str) -> Announcement:
        """Create a new announcement"""
        announcement = Announcement(
            title=announcement_data["title"],
            content=announcement_data["content"],
            author_id=author_id,
            target_audience=announcement_data.get("target_audience", "all"),
            priority=announcement_data.get("priority", "normal"),
            expires_at=announcement_data.get("expires_at")
        )
        
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        return announcement

    @staticmethod
    def get_all_announcements(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Announcement], int]:
        """Get all announcements"""
        query = db.query(Announcement)
        
        if is_active is not None:
            query = query.filter(Announcement.is_active == is_active)
        
        total = query.count()
        announcements = query.order_by(Announcement.created_at.desc()).offset(skip).limit(limit).all()
        
        return announcements, total

    @staticmethod
    def update_announcement(
        db: Session,
        announcement_id: str,
        announcement_data: dict
    ) -> Optional[Announcement]:
        """Update an announcement"""
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        
        if not announcement:
            return None
        
        for key, value in announcement_data.items():
            if hasattr(announcement, key):
                setattr(announcement, key, value)
        
        db.commit()
        db.refresh(announcement)
        return announcement

    @staticmethod
    def delete_announcement(db: Session, announcement_id: str) -> bool:
        """Delete an announcement"""
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        
        if not announcement:
            return False
        
        db.delete(announcement)
        db.commit()
        return True

    @staticmethod
    def get_all_departments(db: Session) -> List[Department]:
        """Get all departments"""
        return db.query(Department).filter(Department.is_active == True).all()

    @staticmethod
    def create_department(db: Session, department_data: dict) -> Department:
        """Create a new department"""
        department = Department(
            name=department_data["name"],
            code=department_data["code"],
            description=department_data.get("description"),
            head_of_department=department_data.get("head_of_department"),
            contact_email=department_data.get("contact_email")
        )
        
        db.add(department)
        db.commit()
        db.refresh(department)
        return department

    @staticmethod
    def update_department(
        db: Session,
        department_id: str,
        department_data: dict
    ) -> Optional[Department]:
        """Update a department"""
        department = db.query(Department).filter(Department.id == department_id).first()
        
        if not department:
            return None
        
        for key, value in department_data.items():
            if hasattr(department, key):
                setattr(department, key, value)
        
        db.commit()
        db.refresh(department)
        return department

    @staticmethod
    def delete_department(db: Session, department_id: str) -> bool:
        """Delete a department"""
        department = db.query(Department).filter(Department.id == department_id).first()
        
        if not department:
            return False
        
        db.delete(department)
        db.commit()
        return True

    @staticmethod
    def get_audit_logs(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> Tuple[List[AuditLog], int]:
        """Get audit logs"""
        query = db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        total = query.count()
        logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
        
        return logs, total
