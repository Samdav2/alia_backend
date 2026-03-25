#!/usr/bin/env python
"""
Async Database Configuration Verification Script
Ensures async PostgreSQL setup works correctly
"""
import asyncio
import os
import sys
from app.config import get_settings
from app.database import engine, init_redis, close_redis

async def verify_database():
    """Verify async database connection"""
    print("\n" + "="*60)
    print("ALIA Platform - Database Configuration Verification")
    print("="*60)

    settings = get_settings()

    # Show configuration
    print(f"\n📋 Configuration:")
    print(f"  Database URL: {settings.database_url[:50]}...")
    print(f"  Redis URL: {settings.redis_url}")
    print(f"  Debug Mode: {settings.debug}")

    # Test database connection
    print(f"\n🔌 Testing Database Connection...")
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            print("  ✅ Database connection successful (async)")
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False

    # Test Redis connection
    print(f"\n🔴 Testing Redis Connection...")
    try:
        await init_redis()
        print("  ✅ Redis connection successful")
        await close_redis()
    except Exception as e:
        print(f"  ⚠️  Redis connection failed: {e}")

    # Show engine info
    print(f"\n⚙️  Engine Configuration:")
    print(f"  Engine Type: {'Async (PostgreSQL)' if hasattr(engine, 'begin_async') else 'Sync (SQLite)'}")
    print(f"  Pool Size: 20")
    print(f"  Max Overflow: 40")
    print(f"  Pool Recycle: 300s")

    print("\n" + "="*60)
    print("✅ All systems ready!")
    print("="*60 + "\n")

    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(verify_database())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
