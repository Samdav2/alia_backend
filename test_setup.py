#!/usr/bin/env python3
"""
Test database setup
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧪 Testing ALIA Platform Setup")
print("=" * 40)

try:
    print("1️⃣  Testing imports...")
    from app.database import Base, engine
    import app.models.user
    import app.models.course
    import app.models.progress
    import app.models.analytics
    import app.models.notification
    import app.models.file
    print("✅ All imports successful")
    
    print("\n2️⃣  Testing database connection...")
    from app.database import SessionLocal
    db = SessionLocal()
    db.close()
    print("✅ Database connection successful")
    
    print("\n3️⃣  Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")
    
    print("\n4️⃣  Verifying tables...")
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"✅ Found {len(tables)} tables:")
    for table in tables:
        print(f"   - {table}")
    
    print("\n🎉 Setup test completed successfully!")
    print("\n📋 Next steps:")
    print("   Run: uvicorn app.main:app --reload")
    print("   Visit: http://localhost:8000/docs")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)