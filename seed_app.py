import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.course import Course, Module, Topic, CourseLevel
from app.models.assessment import Quiz
import uuid

async def seed():
    async with AsyncSessionLocal() as db:
        # 1. Create a Lecturer if not exists
        from sqlalchemy import select
        result = await db.execute(select(User).filter(User.email == "smith@university.edu"))
        lecturer = result.scalar_one_or_none()

        if not lecturer:
            lecturer = User(
                full_name="Dr. Smith",
                email="smith@university.edu",
                hashed_password="hashed_password_here", # Should be hashed in real app
                role=UserRole.LECTURER
            )
            db.add(lecturer)
            await db.commit()
            await db.refresh(lecturer)
            print(f"Created lecturer: {lecturer.full_name}")
        else:
            print(f"Lecturer already exists: {lecturer.full_name}")

        # 2. Create a Course
        result = await db.execute(select(Course).filter(Course.code == "AI101"))
        course = result.scalar_one_or_none()

        if not course:
            course = Course(
                code="AI101",
                title="Introduction to Agentic AI",
                description="Learn about autonomous agentic systems.",
                department="Computer Science",
                level=CourseLevel.BEGINNER,
                instructor_id=lecturer.id,
                is_active=True
            )
            db.add(course)
            await db.commit()
            await db.refresh(course)
            print(f"Created course: {course.title}")

            # 3. Create a Module
            module = Module(
                title="Basics of Agents",
                description="Core concepts of agentic AI.",
                order=1,
                course_id=course.id
            )
            db.add(module)
            await db.commit()
            await db.refresh(module)
            print(f"Created module: {module.title}")

            # 4. Create a Topic
            topic = Topic(
                title="What is an Agent?",
                description="Introductory topic.",
                order=1,
                module_id=module.id
            )
            db.add(topic)
            await db.commit()
            await db.refresh(topic)
            print(f"Created topic: {topic.title}")

            # 5. Create a Quiz (Assessment)
            quiz = Quiz(
                title="Agent Basics Quiz",
                description="Test your knowledge of agents.",
                topic_id=topic.id,
                questions=[
                    {
                        "id": str(uuid.uuid4()),
                        "question": "What is an agent?",
                        "type": "multiple_choice",
                        "options": ["A tool", "An autonomous system", "A robot"],
                        "correct_answer": "An autonomous system"
                    }
                ]
            )
            db.add(quiz)
            await db.commit()
            print(f"Created quiz: {quiz.title}")
        else:
            print(f"Course already exists: {course.title}")

    print("Seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
