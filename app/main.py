"""
ALIA Platform - Main FastAPI Application
High-performance, secure, and concurrent backend
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

# Import models to ensure tables are created
from app.models import *
from app.database import Base, engine, init_redis, close_redis, dispose_engine
from app.config import get_settings
from app.core.exceptions import (
    ALIAException, alia_exception_handler,
    http_exception_handler, validation_exception_handler
)

# Import API routes
from app.api import (
    auth, users, courses, enrollments, progress,
    analytics, notifications, files, ai, admin, lecturer
)

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting ALIA Platform API...")

    # Initialize Redis for caching
    await init_redis()
    logger.info("Redis initialized for caching and rate limiting")

    # Verify async database connection
    try:
        async with engine.connect() as conn:
            await conn.connection.ping()
            logger.info("✓ Async database connection verified")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down ALIA Platform API...")

    # Close Redis connection
    await close_redis()

    # Dispose async engine
    await dispose_engine()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Adaptive Learning Intelligence Assistant Platform API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Security Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["alia.edu.ng", "api.alia.edu.ng"]
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"]
)

# Compression Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Performance Monitoring Middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    # Log slow requests
    if process_time > 1.0:
        logger.warning(f"Slow request: {request.method} {request.url} took {process_time:.2f}s")

    return response


# Security Headers Middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response


# Exception Handlers
app.add_exception_handler(ALIAException, alia_exception_handler)
app.add_exception_handler(Exception, http_exception_handler)
app.add_exception_handler(422, validation_exception_handler)


# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": time.time()
    }


# Root Endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ALIA Platform API",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Contact administrator for API documentation"
    }


# Include API Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(progress.router)
app.include_router(analytics.router)
app.include_router(notifications.router)
app.include_router(files.router)
app.include_router(ai.router)
app.include_router(admin.router)
app.include_router(lecturer.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        workers=1 if settings.debug else 4,
        log_level=settings.log_level.lower()
    )
