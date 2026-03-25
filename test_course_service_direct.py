import asyncio
from app.database import AsyncSessionLocal
from app.services.course_service import CourseService
from app.schemas.course import CourseDetailResponse
from sqlalchemy import select
from app.models.course import Course

async def test_direct():
    async with AsyncSessionLocal() as db:
        # 1. Get a course ID
        result = await db.execute(select(Course).limit(1))
        course = result.scalar_one_or_none()

        if not course:
            print("No course found in DB. Please run seed_app.py first.")
            return

        course_id = str(course.id)
        print(f"Testing direct fetch for course ID: {course_id}")

        # 2. Call the service with eager loading
        # This was the problematic call
        course_loaded = await CourseService.get_course_by_id(db, course_id)

        if not course_loaded:
            print("Failed to fetch course via service.")
            return

        print(f"Course title: {course_loaded.title}")

        # 3. Simulate Pydantic from_orm (this triggers the MissingGreenlet)
        print("Testing Pydantic conversion...")
        try:
            course_data = CourseDetailResponse.from_orm(course_loaded)
            print("✅ Pydantic conversion successful!")
            print(f"Modules: {len(course_data.modules)}")
            if course_data.modules:
                print(f"Topics in module 1: {len(course_data.modules[0].topics)}")
                if course_data.modules[0].topics:
                     print(f"Assessments in topic 1: {len(course_data.modules[0].topics[0].assessments)}")
        except Exception as e:
            print(f"❌ Pydantic conversion failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct())
