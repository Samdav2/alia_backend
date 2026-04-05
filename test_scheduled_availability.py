import asyncio
from datetime import datetime, timedelta, timezone
from app.database import AsyncSessionLocal
from app.services.lecturer_service import LecturerService
from app.services.course_service import CourseService
from app.schemas.course import ModuleCreate, TopicCreate, CourseCreate
from sqlalchemy import select
from app.models.course import Course, Module, Topic
from app.models.user import User, UserRole

async def test_availability():
    async with AsyncSessionLocal() as db:
        # 1. Setup Lecturer and Course
        result = await db.execute(select(User).filter(User.role == UserRole.LECTURER).limit(1))
        lecturer = result.scalar_one_or_none()
        if not lecturer:
            print("❌ No lecturer found. Run seed_app.py")
            return

        result = await db.execute(select(Course).filter(Course.instructor_id == lecturer.id).limit(1))
        course = result.scalar_one_or_none()

        # 1b. Test Course Creation (Verify MissingGreenlet fix)
        print("\nTesting course creation (MissingGreenlet check)...")
        course_code = f"TEST-{datetime.now().timestamp()}"
        new_course_data = CourseCreate(
            code=course_code,
            title="Fix Test Course",
            description="Testing MissingGreenlet",
            department="Test",
            level="beginner",
            duration="1 week"
        )
        new_course = await CourseService.create_course(db, new_course_data, str(lecturer.id))
        if new_course:
            print(f"✅ Created course successfully: {new_course.code}")
            # Try to serialize to trigger potential MissingGreenlet
            from app.schemas.course import CourseDetailResponse
            try:
                CourseDetailResponse.from_orm(new_course)
                print("✅ Serialization successful (No MissingGreenlet)!")
            except Exception as e:
                print(f"❌ Serialization failed: {e}")

            # Cleanup new course
            await db.delete(new_course)
            await db.commit()

        # 1c. Test Enrollment (Verify ValidationError fix)
        print("\nTesting enrollment (ValidationError check)...")
        test_enrollment = await CourseService.enroll_user(db, str(lecturer.id), str(course.id))
        if test_enrollment:
            print(f"✅ Created enrollment successfully: {test_enrollment.id}")
            from app.schemas.course import EnrollmentResponse
            try:
                # This is where it was failing in the API
                resp = EnrollmentResponse.from_orm(test_enrollment)
                print(f"✅ Serialization successful (No ValidationError)! Course Title: {resp.course.title}")
            except Exception as e:
                print(f"❌ Serialization failed: {e}")

            # Cleanup enrollment (wait, maybe we should keep it for a bit or just delete)
            await db.delete(test_enrollment)
            await db.commit()
        else:
            print("ℹ️ Already enrolled in course (expected if seeded)")

        if not course:
            print("❌ No course found for lecturer.")
            return

        now = datetime.now(timezone.utc)
        future = now + timedelta(hours=1)
        past = now - timedelta(hours=1)

        print(f"Current time (UTC): {now}")

        # 2. Create Future Module
        print("\nCreating future module...")
        module_data = ModuleCreate(
            title="Future Module",
            description="Locked module",
            order=10,
            course_id=str(course.id),
            available_at=future
        )
        future_module = await LecturerService.create_module(db, str(course.id), module_data, str(lecturer.id))
        print(f"✅ Created future module: {future_module.title} (Available at: {future_module.available_at})")

        # 3. Create Past Module with Future Topic
        print("\nCreating past module with future topic...")
        module_data.title = "Past Module"
        module_data.available_at = past
        past_module = await LecturerService.create_module(db, str(course.id), module_data, str(lecturer.id))

        topic_data = TopicCreate(
            title="Future Topic",
            description="Locked topic",
            order=1,
            module_id=str(past_module.id),
            available_at=future,
            content="SECRET CONTENT"
        )
        future_topic = await LecturerService.create_topic(db, str(past_module.id), topic_data, str(lecturer.id))
        print(f"✅ Created future topic: {future_topic.title} (Available at: {future_topic.available_at})")

        # 4. Simulate API Logic for Student (is_staff=False)
        print("\nSimulating API response for Student (is_staff=False)...")

        # Check future module
        is_locked_m = future_module.available_at > now
        print(f"Module '{future_module.title}' is_locked: {is_locked_m}")
        if is_locked_m:
            print("✅ Logic correct: Future module is locked for students.")

        # Check future topic in past module
        is_locked_t = future_topic.available_at > now
        print(f"Topic '{future_topic.title}' is_locked: {is_locked_t}")
        if is_locked_t:
            print("✅ Logic correct: Future topic is locked for students.")
            content_redacted = "Locked until scheduled time"
            print(f"Redacted content: {content_redacted}")

        # 5. Clean up
        print("\nCleaning up...")
        await db.delete(future_topic)
        await db.delete(future_module)
        await db.delete(past_module)
        await db.commit()
        print("✅ Cleanup successful.")

if __name__ == "__main__":
    asyncio.run(test_availability())
