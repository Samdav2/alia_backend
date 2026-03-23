from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

def seed():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create a Lecturer
    lecturer = models.User(
        username="dr_smith",
        email="smith@university.edu",
        hashed_password="password123",
        role=models.UserRole.LECTURER
    )
    db.add(lecturer)
    db.commit()
    db.refresh(lecturer)

    # Create a Student
    student = models.User(
        username="john_doe",
        email="john@student.edu",
        hashed_password="password123",
        role=models.UserRole.STUDENT,
        preferences={
            "dyslexia_mode": True,
            "high_contrast": False,
            "audio_speed": 1.2,
            "voice_nav_active": True
        }
    )
    db.add(student)

    # Create a Course
    course = models.Course(
        title="Introduction to Agentic AI",
        raw_content="Agentic AI systems are designed to perceive their environment, reason about goals, and take actions to achieve them. Unlike static models, agentic AI can use tools and interact with external systems to complete complex tasks.",
        lecturer_id=lecturer.id
    )
    db.add(course)

    db.commit()
    print("Database seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed()
