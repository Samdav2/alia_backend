#!/usr/bin/env python3
"""
Quick start script for ALIA Platform with SQLite
"""
import os
import sys
import shutil
from pathlib import Path

def print_header():
    print("🎓 ALIA Platform - Quick Start with SQLite")
    print("=" * 50)

def setup_env():
    """Set up environment file"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        shutil.copy(".env.example", ".env")
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    for directory in ["uploads", "logs", "static"]:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def create_database():
    """Create database tables"""
    print("🗄️  Creating database tables...")
    try:
        from app.database import Base, engine
        import app.models.user
        import app.models.course
        import app.models.progress
        import app.models.analytics
        import app.models.notification
        import app.models.file
        
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()
        return False

def start_server():
    """Start the development server"""
    print("\n🎉 Setup complete!")
    print("\n🚀 Starting development server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    import subprocess
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")

def main():
    print_header()
    
    setup_env()
    create_directories()
    
    if not create_database():
        print("\n❌ Failed to create database")
        print("Please check your Python environment and try again")
        sys.exit(1)
    
    start_server()

if __name__ == "__main__":
    main()