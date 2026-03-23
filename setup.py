#!/usr/bin/env python3
"""
Complete setup script for ALIA Platform Backend
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print setup header"""
    print("🎓 ALIA Platform Backend - Complete Setup")
    print("=" * 50)
    print("This script will set up the complete ALIA Platform backend")
    print("with UUID-based models, security, and all features.\n")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required system dependencies are available"""
    dependencies = {
        "git": "Git version control",
        "pip": "Python package manager",
    }
    
    missing = []
    for cmd, desc in dependencies.items():
        if shutil.which(cmd) is None:
            missing.append(f"{cmd} ({desc})")
        else:
            print(f"✅ {desc}: Found")
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        return False
    
    return True

def setup_virtual_environment():
    """Set up Python virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("🔄 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def install_requirements():
    """Install Python requirements"""
    print("🔄 Installing Python requirements...")
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = "venv/Scripts/pip"
    else:  # Unix/Linux/macOS
        pip_path = "venv/bin/pip"
    
    try:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def setup_environment_file():
    """Set up environment configuration"""
    env_file = Path(".env")
    example_file = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not example_file.exists():
        print("❌ .env.example file not found")
        return False
    
    print("🔄 Creating .env file from example...")
    shutil.copy(example_file, env_file)
    
    print("✅ .env file created")
    print("⚠️  Please edit .env file with your actual configuration:")
    print("   - DATABASE_URL (PostgreSQL connection string)")
    print("   - SECRET_KEY (generate a secure secret key)")
    print("   - OPENAI_API_KEY (if using AI features)")
    print("   - REDIS_URL (if using Redis)")
    
    return True

def setup_database():
    """Set up database migrations"""
    print("🔄 Setting up database migrations...")
    
    # Check if migrations directory exists
    migrations_dir = Path("migrations")
    if not migrations_dir.exists():
        print("📁 Initializing Alembic...")
        try:
            subprocess.run(["alembic", "init", "migrations"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to initialize Alembic")
            return False
    
    print("✅ Database migration setup complete")
    print("📋 Next steps for database:")
    print("   1. Set up PostgreSQL database")
    print("   2. Update DATABASE_URL in .env file")
    print("   3. Run: alembic revision --autogenerate -m 'Initial migration'")
    print("   4. Run: alembic upgrade head")
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "uploads",
        "logs",
        "static"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")
    
    return True

def run_basic_tests():
    """Run basic tests to verify setup"""
    print("🧪 Running basic tests...")
    
    try:
        # Test import of main modules
        sys.path.append(str(Path.cwd()))
        
        from app.config import get_settings
        from app.database import Base
        from app.models.user import User
        from app.main import app
        
        print("✅ All core modules import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup Complete!")
    print("=" * 30)
    print("Next steps:")
    print("1. 📝 Edit .env file with your configuration")
    print("2. 🗄️  Set up PostgreSQL database")
    print("3. 🔄 Run database migrations:")
    print("   python create_migration.py")
    print("4. 🚀 Start the development server:")
    print("   python start_dev.py")
    print("5. 📖 Visit http://localhost:8000/docs for API documentation")
    print("\n📚 Additional resources:")
    print("- README.md: Complete documentation")
    print("- Docker: Use docker-compose up for containerized setup")
    print("- Production: See deployment section in README.md")

def main():
    """Main setup function"""
    print_header()
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Setting up virtual environment", setup_virtual_environment),
        ("Installing requirements", install_requirements),
        ("Setting up environment file", setup_environment_file),
        ("Creating directories", create_directories),
        ("Setting up database migrations", setup_database),
        ("Running basic tests", run_basic_tests),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            sys.exit(1)
    
    print_next_steps()

if __name__ == "__main__":
    main()