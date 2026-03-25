# Async PostgreSQL Database Configuration

## Overview
The ALIA Platform has been updated to use **async SQLAlchemy** with **asyncpg** driver for PostgreSQL. This provides:
- ✅ True async/await support throughout the application
- ✅ Better performance and concurrency
- ✅ Production-ready connection pooling
- ✅ Fallback to SQLite for development

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Required new packages:
- `asyncpg==0.29.0` - Async PostgreSQL driver
- `redis[asyncio]` (via redis==5.0.1) - Async Redis support

### 2. Setup Environment Variables

For **PostgreSQL** (Production/Live):
```bash
export DATABASE_URL="postgresql://user:password@host:port/dbname"
export REDIS_URL="redis://localhost:6379"
export PORT=8000
```

For **SQLite** (Development):
```bash
export DATABASE_URL="sqlite:///./alia.db"
export REDIS_URL="redis://localhost:6379"
export PORT=8000
```

## Running the Application

### Option 1: With Migrations (Recommended)
```bash
python run_app.py
```

This will:
1. Run Alembic migrations to create/update database schema
2. Start uvicorn server

### Option 2: Direct Start
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Verification

### Test Database Connection
```bash
python verify_db.py
```

This will:
- ✅ Test async PostgreSQL/SQLite connection
- ✅ Test Redis connection
- ✅ Display configuration summary

### Health Check
```bash
curl http://localhost:8000/health
```

## Database Configuration Details

### Async Engine Settings
```python
engine = create_async_engine(
    database_url,
    echo=debug,                    # SQL logging
    pool_pre_ping=True,           # Verify connections before use
    pool_recycle=300,             # Recycle connections every 5 min
    pool_size=20,                 # Base pool size
    max_overflow=40,              # Extra connections allowed
    connect_args={
        "ssl": "prefer",          # SSL support
        "timeout": 30,            # Connection timeout
        "command_timeout": 30,    # Query timeout
    }
)
```

### Connection Pool Info
- **Pool Size**: 20 connections
- **Max Overflow**: 40 additional connections
- **Pre-ping**: Enabled (validates connections)
- **Recycle**: 300 seconds
- **SSL**: Preferred (auto-negotiated)

## Migration Management

### Create New Migration
```bash
alembic revision --autogenerate -m "your message"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Last Migration
```bash
alembic downgrade -1
```

## Troubleshooting

### Issue: "MissingGreenlet" Error
**Solution**: Already fixed! Removed synchronous `create_all()` from startup.

### Issue: Redis Connection Failed
**Solution**: Redis is optional. App works with Redis disabled for caching.

### Issue: "Connection timeout"
**Solution**:
- Check database connectivity: `verify_db.py`
- Verify DATABASE_URL format
- Check firewall rules for port access

### Issue: SSL Certificate Error
**Solution**: Set `ssl=False` in database URL or use proper certificates

## Database URL Formats

### PostgreSQL (Async)
```
postgresql+asyncpg://user:password@localhost:5432/dbname
```

### PostgreSQL (with SSL)
```
postgresql+asyncpg://user:password@localhost:5432/dbname?sslmode=require
```

### SQLite (Development)
```
sqlite:///./alia.db
```

### Render.com PostgreSQL
```
postgresql+asyncpg://user:password@host.render.com:5432/dbname
```

## Important Notes

1. **Async Operations**: All database operations are now truly async. Services need to use `async with` for sessions.

2. **Backward Compatibility**: SQLite support maintained for development.

3. **Production Checklist**:
   - ✅ Set strong `SECRET_KEY`
   - ✅ Use HTTPS (DATABASE_URL with SSL)
   - ✅ Configure proper pool sizes for your workload
   - ✅ Enable Redis for production performance
   - ✅ Run migrations before deployment
   - ✅ Monitor connection pool usage

4. **Performance Tips**:
   - Increase `pool_size` if you have many concurrent requests
   - Set `max_overflow` appropriately
   - Use Alembic migrations instead of `create_all()`
   - Enable connection pooling on database side

## Deployment on Render.com

Create `.render/start.sh`:
```bash
#!/bin/bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
```

Make executable:
```bash
chmod +x .render/start.sh
```

Set environment variables in Render dashboard:
- `DATABASE_URL`: Your PostgreSQL connection string
- `REDIS_URL`: Redis connection URL
- `SECRET_KEY`: Strong secret key

## Related Files
- `app/database.py` - Async database configuration
- `app/main.py` - Application lifespan with async setup
- `app/config.py` - Settings and configuration
- `alembic/` - Database migrations
- `verify_db.py` - Database verification script
- `run_app.py` - Application startup script
