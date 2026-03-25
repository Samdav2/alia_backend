import asyncio
import logging
from sqlmodel import SQLModel
from app.database import engine, Base
# Import all models to ensure they are registered with SQLModel.metadata
from app.models import (
    User, Course, Module, Topic, Enrollment,
    Progress, TopicProgress, Analytics, AccessibilityUsage,
    Notification, File, Quiz, QuizAttempt,
    Department, Announcement, AuditLog
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def recreate_db():
    logger.info("Starting database recreation...")
    try:
        async with engine.begin() as conn:
            logger.info("Dropping all existing tables...")
            await conn.run_sync(SQLModel.metadata.drop_all)
            logger.info("Creating all tables using SQLModel metadata...")
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("✓ Database recreated successfully!")
    except Exception as e:
        logger.error(f"✗ Failed to recreate database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(recreate_db())
