"""
Configuration settings for ALIA Platform
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "ALIA Platform API"
    app_version: str = "1.0.0"
    debug: bool = True  # Enable debug mode by default for development

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Database - External PostgreSQL
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://samdav:A0RQspljYlfxHlk9IcWW9rxfA6pauyuw@dpg-d71n9iu3jp1c739eokg0-a.ohio-postgres.render.com/alia"
    )

    # Redis (for caching and rate limiting)
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "https://alia.com.ng",
        "https://www.alia.com.ng",
    ]

    # File Storage
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx", ".mp4", ".mp3"]
    base_url: str = os.getenv("BASE_URL", "http://localhost:8000")

    # AI Services
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Rate Limiting
    rate_limit_per_minute: int = 100
    auth_rate_limit_per_minute: int = 5

    # Logging
    log_level: str = "DEBUG"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()
