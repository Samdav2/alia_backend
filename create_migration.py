#!/usr/bin/env python3
"""
Create initial database migration for ALIA Platform
"""
import subprocess
import sys
import os

def create_initial_migration():
    """Create the initial database migration"""
    print("🔄 Creating initial database migration...")
    
    try:
        # Initialize alembic if not already done
        if not os.path.exists("migrations/versions"):
            print("📁 Initializing Alembic...")
            subprocess.run(["alembic", "init", "migrations"], check=True)
        
        # Create initial migration
        print("📝 Creating initial migration...")
        result = subprocess.run([
            "alembic", "revision", "--autogenerate", 
            "-m", "Initial migration with UUID primary keys"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration created successfully!")
            print("📄 Migration file:", result.stdout.strip())
        else:
            print("❌ Error creating migration:")
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Please install it with: pip install alembic")
        return False
    
    return True

def apply_migration():
    """Apply the migration to the database"""
    print("🚀 Applying migration to database...")
    
    try:
        result = subprocess.run(["alembic", "upgrade", "head"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Migration applied successfully!")
            return True
        else:
            print("❌ Error applying migration:")
            print(result.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🎓 ALIA Platform - Database Migration Setup")
    print("=" * 45)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Please create it from .env.example")
        print("   Make sure to set the correct DATABASE_URL")
        return
    
    # Create migration
    if not create_initial_migration():
        sys.exit(1)
    
    # Ask user if they want to apply the migration
    apply = input("\n🤔 Do you want to apply the migration now? (y/N): ").lower().strip()
    
    if apply in ['y', 'yes']:
        if apply_migration():
            print("\n🎉 Database setup complete!")
            print("   You can now start the application with: python start_dev.py")
        else:
            print("\n⚠️  Migration created but not applied.")
            print("   Run 'alembic upgrade head' manually when ready.")
    else:
        print("\n📋 Migration created but not applied.")
        print("   Run 'alembic upgrade head' when you're ready to apply it.")

if __name__ == "__main__":
    main()