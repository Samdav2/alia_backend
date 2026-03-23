# ALIA Platform - Quick Start Guide

## 🚀 Get Started in 3 Minutes

### Option 1: Automatic Setup (Recommended)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run quick start
python quickstart.py
```

The server will start automatically at `http://localhost:8000`

### Option 2: Manual Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment file
cp .env.example .env

# 3. Create database
python test_setup.py

# 4. Start server
uvicorn app.main:app --reload
```

## 📖 Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🗄️ Database Configuration

### SQLite (Default - No Setup Required)

The application uses SQLite by default. The database file `alia.db` is created automatically.

**Advantages:**
- ✅ Zero configuration
- ✅ No external dependencies
- ✅ Perfect for development
- ✅ Easy to reset (just delete alia.db)

### PostgreSQL (Production Ready)

When you're ready for production:

1. **Install PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql

# macOS
brew install postgresql
```

2. **Create database**
```bash
createdb alia_db
```

3. **Update .env**
```bash
# Change this line in .env:
DATABASE_URL=postgresql://username:password@localhost:5432/alia_db
```

4. **Recreate tables**
```bash
python test_setup.py
```

The application automatically detects the database type!

## 🔑 First Steps

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "role": "student",
    "department": "Computer Science"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

Save the `token` from the response!

### 3. Get Your Profile

```bash
curl -X GET "http://localhost:8000/api/users/profile" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🎯 Key Features

### UUID Primary Keys
- All tables use UUID for security
- Works with both SQLite and PostgreSQL
- Prevents enumeration attacks

### Security
- JWT authentication
- Role-based access control
- Password hashing with bcrypt
- Rate limiting (when Redis is available)

### Performance
- Async/await throughout
- Database connection pooling
- Optional Redis caching
- Optimized queries

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```bash
# Application
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (choose one)
DATABASE_URL=sqlite:///./alia.db
# DATABASE_URL=postgresql://user:pass@localhost/alia_db

# Redis (optional)
REDIS_URL=redis://localhost:6379

# AI Services (optional)
OPENAI_API_KEY=your-key-here
```

## 📊 Database Schema

All tables use UUID primary keys:

- `users` - User accounts and profiles
- `courses` - Course information
- `modules` - Course modules
- `topics` - Module topics
- `enrollments` - User course enrollments
- `progress` - Learning progress tracking
- `topic_progress` - Individual topic progress
- `analytics` - Performance analytics
- `accessibility_usage` - Accessibility feature tracking
- `notifications` - User notifications
- `files` - File uploads

## 🧪 Testing

```bash
# Test database setup
python test_setup.py

# Run API tests
pytest

# Test specific endpoint
pytest tests/test_auth.py
```

## 🐳 Docker (Optional)

```bash
# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

## 🔄 Switching Databases

### From SQLite to PostgreSQL

1. Export data (if needed):
```bash
sqlite3 alia.db .dump > backup.sql
```

2. Update `.env`:
```bash
DATABASE_URL=postgresql://user:pass@localhost/alia_db
```

3. Recreate tables:
```bash
python test_setup.py
```

### From PostgreSQL to SQLite

1. Update `.env`:
```bash
DATABASE_URL=sqlite:///./alia.db
```

2. Recreate tables:
```bash
python test_setup.py
```

## 🆘 Troubleshooting

### Database Connection Error

**SQLite:**
- Check file permissions
- Ensure directory is writable

**PostgreSQL:**
- Verify PostgreSQL is running: `pg_isready`
- Check credentials in `.env`
- Ensure database exists: `psql -l`

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use

```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

## 📚 Next Steps

1. ✅ Read the [full README](README.md)
2. ✅ Explore the [API documentation](http://localhost:8000/docs)
3. ✅ Check out the [API specification](API_DOCUMENTATION.md)
4. ✅ Review the [architecture](README.md#architecture)

## 💡 Tips

- Use SQLite for development
- Switch to PostgreSQL for production
- Enable Redis for better performance
- Set `DEBUG=False` in production
- Change `SECRET_KEY` to a secure random value
- Use environment variables for sensitive data

## 🎓 Learn More

- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://www.sqlalchemy.org
- Pydantic: https://pydantic-docs.helpmanual.io

---

**Need help?** Open an issue or contact support@alia.edu.ng