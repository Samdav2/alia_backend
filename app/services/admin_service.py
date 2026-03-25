"""
Admin service for system management - Async compatible
"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, or_, select, text
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
    async def get_all_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        role: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """Async: Get all users with filters"""
        query = select(User)
        
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
        
        count_result = await db.execute(select(func.count(User.id)))
        total = count_result.scalar() or 0
        
        result = await db.execute(query.offset(skip).limit(limit))
        users = result.scalars().all()
        
        return users, total

    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict) -> User:
        """Async: Create a new user"""
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
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update_user(db: AsyncSession, user_id: str, user_data: dict) -> Optional[User]:
        """Async: Update a user"""
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        for key, value in user_data.items():
            if key == "password":
                user.hashed_password = AuthService.get_password_hash(value)
            elif hasattr(user, key):
                setattr(user, key, value)
        
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: str) -> bool:
        """Async: Delete a user"""
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        await db.delete(user)
        await db.commit()
        return True

    @staticmethod
    async def bulk_user_action(
        db: AsyncSession,
        user_ids: List[str],
        action: str,
        data: Optional[dict] = None
    ) -> bool:
        """Async: Perform bulk action on users"""
        result = await db.execute(select(User).filter(User.id.in_(user_ids)))
        users = result.scalars().all()
        
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
                await db.delete(user)
        elif action == "update_role" and data:
            for user in users:
                user.role = data.get("role")
        
        await db.commit()
        return True

    @staticmethod
    async def get_all_courses_admin(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        department: Optional[str] = None
    ) -> Tuple[List[dict], int]:
        """Async: Get all courses with admin view"""
        query = select(Course)
        
        if status == "active":
            query = query.filter(Course.is_active == True)
        elif status == "inactive":
            query = query.filter(Course.is_active == False)
        
        if department:
            query = query.filter(Course.department == department)
        
        count_result = await db.execute(select(func.count(Course.id)))
        total = count_result.scalar() or 0
        
        result = await db.execute(query.offset(skip).limit(limit))
        courses = result.scalars().all()
        
        result_list = []
        for course in courses:
            instructor_result = await db.execute(select(User).filter(User.id == course.instructor_id))
            instructor = instructor_result.scalar_one_or_none()
            
            enrollment_count_result = await db.execute(select(func.count(Enrollment.id)).filter(
                Enrollment.course_id == course.id
            ))
            enrollment_count = enrollment_count_result.scalar() or 0
            
            result_list.append({
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
        
        return result_list, total

    @staticmethod
    async def approve_course(db: AsyncSession, course_id: str) -> bool:
        """Async: Approve a course"""
        result = await db.execute(select(Course).filter(Course.id == course_id))
        course = result.scalar_one_or_none()
        
        if not course:
            return False
        
        course.is_active = True
        await db.commit()
        return True

    @staticmethod
    async def reject_course(db: AsyncSession, course_id: str) -> bool:
        """Async: Reject a course"""
        result = await db.execute(select(Course).filter(Course.id == course_id))
        course = result.scalar_one_or_none()
        
        if not course:
            return False
        
        course.is_active = False
        await db.commit()
        return True

    @staticmethod
    async def change_course_status(db: AsyncSession, course_id: str, status: str) -> bool:
        """Async: Change course status (draft/published)"""
        result = await db.execute(select(Course).filter(Course.id == course_id))
        course = result.scalar_one_or_none()
        
        if not course:
            return False
        
        # Map status to is_active field
        if status == "published":
            course.is_active = True
        elif status == "draft":
            course.is_active = False
        else:
            return False  # Invalid status
        
        await db.commit()
        return True

    @staticmethod
    async def feature_course(db: AsyncSession, course_id: str, featured: bool) -> bool:
        """Async: Feature or unfeature a course"""
        result = await db.execute(select(Course).filter(Course.id == course_id))
        course = result.scalar_one_or_none()
        
        if not course:
            return False
        
        # Add featured flag to course tags
        tags = course.tags or []
        if featured and "featured" not in tags:
            tags.append("featured")
        elif not featured and "featured" in tags:
            tags.remove("featured")
        
        course.tags = tags
        await db.commit()
        return True

    @staticmethod
    async def get_system_statistics(db: AsyncSession) -> Dict[str, Any]:
        """Async: Get system-wide statistics"""
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar() or 0
        
        total_students_result = await db.execute(select(func.count(User.id)).filter(User.role == "student"))
        total_students = total_students_result.scalar() or 0
        
        total_lecturers_result = await db.execute(select(func.count(User.id)).filter(User.role == "lecturer"))
        total_lecturers = total_lecturers_result.scalar() or 0
        
        total_courses_result = await db.execute(select(func.count(Course.id)))
        total_courses = total_courses_result.scalar() or 0
        
        active_courses_result = await db.execute(select(func.count(Course.id)).filter(Course.is_active == True))
        active_courses = active_courses_result.scalar() or 0
        
        total_enrollments_result = await db.execute(select(func.count(Enrollment.id)))
        total_enrollments = total_enrollments_result.scalar() or 0
        
        # Active users (logged in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users_result = await db.execute(select(func.count(User.id)).filter(
            User.last_login >= thirty_days_ago
        ))
        active_users = active_users_result.scalar() or 0
        
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
    async def get_accessibility_report(db: AsyncSession) -> Dict[str, Any]:
        """Async: Get system-wide accessibility report"""
        # Users with disabilities
        result = await db.execute(select(User))
        all_users = result.scalars().all()
        
        disability_count = sum(
            1 for u in all_users 
            if u.disability_info and u.disability_info.get("hasDisability")
        )
        
        total_users_result = await db.execute(select(func.count(User.id)))
        total_users = total_users_result.scalar() or 0
        
        return {
            "users_with_disabilities": disability_count,
            "total_users": total_users,
            "feature_usage": []  # Placeholder
        }

    @staticmethod
    async def get_performance_metrics(db: AsyncSession) -> Dict[str, Any]:
        """Async: Get system performance metrics"""
        # Average course completion rate
        total_enrollments_result = await db.execute(select(func.count(Enrollment.id)))
        total_enrollments = total_enrollments_result.scalar() or 0
        
        completed_enrollments_result = await db.execute(select(func.count(Enrollment.id)).filter(
            Enrollment.status == "completed"
        ))
        completed_enrollments = completed_enrollments_result.scalar() or 0
        
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
    async def get_system_health(db: AsyncSession) -> Dict[str, Any]:
        """Async: Get system health status"""
        try:
            # Test database connection
            await db.execute(text("SELECT 1"))
            db_status = "healthy"
        except:
            db_status = "unhealthy"
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "database": db_status,
            "timestamp": datetime.utcnow()
        }

    @staticmethod
    async def create_announcement(db: AsyncSession, announcement_data: dict, author_id: str) -> Announcement:
        """Async: Create a new announcement"""
        announcement = Announcement(
            title=announcement_data["title"],
            content=announcement_data["content"],
            author_id=author_id,
            target_audience=announcement_data.get("target_audience", "all"),
            priority=announcement_data.get("priority", "normal"),
            expires_at=announcement_data.get("expires_at")
        )
        
        db.add(announcement)
        await db.commit()
        await db.refresh(announcement)
        return announcement

    @staticmethod
    async def get_all_announcements(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Announcement], int]:
        """Async: Get all announcements"""
        query = select(Announcement)
        
        if is_active is not None:
            query = query.filter(Announcement.is_active == is_active)
        
        count_result = await db.execute(select(func.count(Announcement.id)))
        total = count_result.scalar() or 0
        
        result = await db.execute(query.order_by(Announcement.created_at.desc()).offset(skip).limit(limit))
        announcements = result.scalars().all()
        
        return announcements, total

    @staticmethod
    async def update_announcement(
        db: AsyncSession,
        announcement_id: str,
        announcement_data: dict
    ) -> Optional[Announcement]:
        """Async: Update an announcement"""
        result = await db.execute(select(Announcement).filter(Announcement.id == announcement_id))
        announcement = result.scalar_one_or_none()
        
        if not announcement:
            return None
        
        for key, value in announcement_data.items():
            if hasattr(announcement, key):
                setattr(announcement, key, value)
        
        await db.commit()
        await db.refresh(announcement)
        return announcement

    @staticmethod
    async def delete_announcement(db: AsyncSession, announcement_id: str) -> bool:
        """Async: Delete an announcement"""
        result = await db.execute(select(Announcement).filter(Announcement.id == announcement_id))
        announcement = result.scalar_one_or_none()
        
        if not announcement:
            return False
        
        await db.delete(announcement)
        await db.commit()
        return True

    @staticmethod
    async def get_all_departments(db: AsyncSession) -> List[Department]:
        """Async: Get all departments"""
        result = await db.execute(select(Department).filter(Department.is_active == True))
        return result.scalars().all()

    @staticmethod
    async def create_department(db: AsyncSession, department_data: dict) -> Department:
        """Async: Create a new department"""
        department = Department(
            name=department_data["name"],
            code=department_data["code"],
            description=department_data.get("description"),
            head_of_department=department_data.get("head_of_department"),
            contact_email=department_data.get("contact_email")
        )
        
        db.add(department)
        await db.commit()
        await db.refresh(department)
        return department

    @staticmethod
    async def update_department(
        db: AsyncSession,
        department_id: str,
        department_data: dict
    ) -> Optional[Department]:
        """Async: Update a department"""
        result = await db.execute(select(Department).filter(Department.id == department_id))
        department = result.scalar_one_or_none()
        
        if not department:
            return None
        
        for key, value in department_data.items():
            if hasattr(department, key):
                setattr(department, key, value)
        
        await db.commit()
        await db.refresh(department)
        return department

    @staticmethod
    async def delete_department(db: AsyncSession, department_id: str) -> bool:
        """Async: Delete a department"""
        result = await db.execute(select(Department).filter(Department.id == department_id))
        department = result.scalar_one_or_none()
        
        if not department:
            return False
        
        await db.delete(department)
        await db.commit()
        return True

    @staticmethod
    async def get_audit_logs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> Tuple[List[AuditLog], int]:
        """Async: Get audit logs"""
        query = select(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        count_result = await db.execute(select(func.count(AuditLog.id)))
        total = count_result.scalar() or 0
        
        result = await db.execute(query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit))
        logs = result.scalars().all()
        
        return logs, total
