#!/bin/bash
# Quick Setup Script for Async PostgreSQL
# Run this to get started quickly

set -e

echo "=========================================="
echo "ALIA Platform - Async Setup"
echo "=========================================="

# Step 1: Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Step 2: Show current configuration
echo ""
echo "📋 Current Configuration:"
if [ -z "$DATABASE_URL" ]; then
    echo "  ⚠️  DATABASE_URL not set"
    echo "  Set it with: export DATABASE_URL='postgresql+asyncpg://...'"
else
    echo "  ✅ DATABASE_URL: ${DATABASE_URL:0:50}..."
fi

if [ -z "$REDIS_URL" ]; then
    echo "  ⚠️  REDIS_URL not set (optional)"
else
    echo "  ✅ REDIS_URL: $REDIS_URL"
fi

# Step 3: Verify database connection
echo ""
echo "🔌 Verifying database connection..."
python verify_db.py

# Step 4: Show next steps
echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the application:"
echo "   python run_app.py"
echo ""
echo "2. In another terminal, test the API:"
echo "   curl http://localhost:8000/health"
echo ""
echo "3. Access API documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "=========================================="
