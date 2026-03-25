#!/usr/bin/env python
"""
Start the application with database migrations
Works with both async PostgreSQL and SQLite
"""
import subprocess
import sys
import os
import asyncio

async def run_migrations():
    """Run database migrations"""
    print("\n" + "="*60)
    print("Running Database Migrations...")
    print("="*60)

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=os.path.dirname(__file__)
    )

    if result.returncode != 0:
        print("❌ Migration failed!")
        return False

    print("✅ Migrations completed successfully")
    return True

def main():
    # Run migrations first
    try:
        result = asyncio.run(run_migrations())
        if not result:
            sys.exit(1)
    except Exception as e:
        print(f"Migration error: {e}")
        sys.exit(1)

    # Start the application
    print("\n" + "="*60)
    print("Starting ALIA Platform API...")
    print("="*60 + "\n")

    port = os.getenv("PORT", "8000")
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", port,
        "--reload"
    ])

if __name__ == "__main__":
    main()
