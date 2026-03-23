#!/bin/bash

echo "🎓 ALIA Platform - Quick Start with SQLite"
echo "=========================================="

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads logs static
echo "✅ Directories created"

# Create database tables
echo "🗄️  Creating database tables..."
python -c "
from app.database import Base, engine
from app.models import *

print('Creating all tables...')
Base.metadata.create_all(bind=engine)
print('✅ Database tables created successfully!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "🚀 Starting development server..."
    echo "📖 API Documentation: http://localhost:8000/docs"
    echo "🔍 Health Check: http://localhost:8000/health"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Start the server
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    echo "❌ Error creating database tables"
    echo "Please check your Python environment and try again"
    exit 1
fi