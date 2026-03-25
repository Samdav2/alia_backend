"""
Async Database configuration and session management for PostgreSQL
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
import redis.asyncio as redis
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Determine if using SQLite or PostgreSQL
is_sqlite = settings.database_url.startswith("sqlite")

if is_sqlite:
    # SQLite configuration (synchronous for development)
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.debug
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    async def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def dispose_engine():
        """Dispose the sync engine"""
        engine.dispose()
        logger.info("Database engine disposed")
else:
    # PostgreSQL Async configuration
    # Convert DATABASE_URL to async format if needed
    database_url = settings.database_url
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)

    logger.info(f"Using async database: {database_url[:30]}...")

    # Create async engine
    engine = create_async_engine(
        database_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=20,
        max_overflow=40,
        connect_args={
            "ssl": "prefer",
            "timeout": 30,
            "command_timeout": 30,
            "server_settings": {
                "application_name": "alia_platform",
                "jit": "off"
            }
        }
    )

    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    async def get_db():
        """Async database session dependency"""
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    async def dispose_engine():
        """Dispose the async engine"""
        await engine.dispose()
        logger.info("Database engine disposed")

# Base class for models
Base = declarative_base()

# Redis connection for caching and rate limiting (async)
redis_client = None

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = await redis.from_url(
            settings.redis_url,
            encoding="utf8",
            decode_responses=True,
            socket_connect_timeout=10,
            socket_keepalive=True
        )
        logger.info("✓ Redis connection initialized")
    except Exception as e:
        logger.warning(f"✗ Redis connection failed: {e}. Caching disabled.")
        redis_client = None

async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("✓ Redis connection closed")

# Redis dependency
def get_redis():
    return redis_client
