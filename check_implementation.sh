#!/bin/bash
# Implementation Verification Checklist
# Run this to verify the async PostgreSQL setup is complete

echo "========================================"
echo "Async PostgreSQL Implementation Checker"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_count=0
pass_count=0

# Function to check if file exists
check_file() {
    local file=$1
    local description=$2
    check_count=$((check_count + 1))

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗${NC} $description"
    fi
}

# Function to check if dependency is installed
check_package() {
    local package=$1
    local description=$2
    check_count=$((check_count + 1))

    if python -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        pass_count=$((pass_count + 1))
    else
        echo -e "${RED}✗${NC} $description (run: pip install -r requirements.txt)"
    fi
}

echo "📋 Checking Implementation Files..."
echo ""

# Check modified files
check_file "app/database.py" "app/database.py - Async engine configured"
check_file "app/main.py" "app/main.py - Lifespan updated"
check_file "requirements.txt" "requirements.txt - Updated with asyncpg"
check_file ".env.example" ".env.example - Database URL examples"
check_file "Dockerfile" "Dockerfile - Startup scripts added"

echo ""
echo "🔧 Checking Helper Scripts..."
echo ""

# Check new scripts
check_file "verify_db.py" "verify_db.py - Database verification script"
check_file "run_app.py" "run_app.py - Application launcher"
check_file "run.sh" "run.sh - Docker startup script"
check_file "quick_setup.sh" "quick_setup.sh - Automatic setup script"

echo ""
echo "📚 Checking Documentation..."
echo ""

# Check documentation
check_file "DOCUMENTATION_INDEX.md" "DOCUMENTATION_INDEX.md - Documentation index"
check_file "ASYNC_QUICK_REFERENCE.md" "ASYNC_QUICK_REFERENCE.md - Quick reference"
check_file "ASYNC_DB_SETUP.md" "ASYNC_DB_SETUP.md - Setup guide"
check_file "ASYNC_COMPLETE_GUIDE.md" "ASYNC_COMPLETE_GUIDE.md - Complete guide"
check_file "ARCHITECTURE_ASYNC.md" "ARCHITECTURE_ASYNC.md - Architecture diagrams"
check_file "BEST_PRACTICES.md" "BEST_PRACTICES.md - Best practices"
check_file "BEFORE_AFTER_COMPARISON.md" "BEFORE_AFTER_COMPARISON.md - Code comparison"
check_file "ASYNC_DB_MIGRATION_SUMMARY.md" "ASYNC_DB_MIGRATION_SUMMARY.md - Migration summary"
check_file "ASYNC_IMPLEMENTATION_COMPLETE.md" "ASYNC_IMPLEMENTATION_COMPLETE.md - Implementation summary"

echo ""
echo "📦 Checking Python Dependencies..."
echo ""

# Check required packages
check_package "fastapi" "FastAPI installed"
check_package "sqlalchemy" "SQLAlchemy installed"
check_package "asyncpg" "asyncpg installed (async PostgreSQL driver)"
check_package "redis" "redis installed"
check_package "pydantic" "pydantic installed"

echo ""
echo "========================================"
echo "Summary"
echo "========================================"
echo "Checks Passed: $pass_count / $check_count"
echo ""

if [ $pass_count -eq $check_count ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Set DATABASE_URL environment variable"
    echo "2. Run: python run_app.py"
    echo "3. Test: curl http://localhost:8000/health"
    echo ""
    exit 0
else
    failed=$((check_count - pass_count))
    echo -e "${YELLOW}⚠️  $failed check(s) failed${NC}"
    echo ""
    echo "To fix:"
    echo "1. Install dependencies: pip install -r requirements.txt"
    echo "2. Read: DOCUMENTATION_INDEX.md"
    echo "3. See: ASYNC_QUICK_REFERENCE.md"
    echo ""
    exit 1
fi
