#!/usr/bin/env python3
"""
Development startup script for ALIA Platform
"""
import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ Core dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def setup_environment():
    """Set up environment variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found, copying from .env.example")
        example_file = Path(".env.example")
        if example_file.exists():
            import shutil
            shutil.copy(example_file, env_file)
            print("✅ Created .env file from example")
        else:
            print("❌ .env.example not found")
            return False
    return True

def start_application():
    """Start the FastAPI application"""
    print("🚀 Starting ALIA Platform API...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health check available at: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def main():
    """Main function"""
    print("🎓 ALIA Platform - Development Server")
    print("=" * 40)
    
    if not check_requirements():
        sys.exit(1)
    
    if not setup_environment():
        sys.exit(1)
    
    start_application()

if __name__ == "__main__":
    main()