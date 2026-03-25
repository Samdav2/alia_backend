# Quick Reference - Async PostgreSQL Setup

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Database URL
```bash
# For Local PostgreSQL
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/alia_db"

# For Render.com
export DATABASE_URL="postgresql+asyncpg://user:password@hostname.render.com:5432/alia_db"

# For Development (SQLite)
export DATABASE_URL="sqlite:///./alia.db"
```

### 3. Run Migrations
```bash
alembic upgrade head
```

### 4. Start Application
```bash
# Option A: With auto-migration
python run_app.py

# Option B: Direct
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Option C: Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Verify Setup
```bash
python verify_db.py
```

## 📝 Key Files Modified

| File | Change | Purpose |
|------|--------|---------|
| `app/database.py` | Async engine, asyncpg driver | PostgreSQL async support |
| `app/main.py` | Async lifespan, init_redis | Proper startup/shutdown |
| `requirements.txt` | Added asyncpg==0.29.0 | Async PostgreSQL driver |
| `.env.example` | Added async DB URLs | Configuration reference |

## ✨ New Features

✅ **True Async Support** - All database operations are async-compatible
✅ **Connection Pooling** - 20 base + 40 overflow connections
✅ **Auto URL Conversion** - Converts `postgresql://` to `postgresql+asyncpg://`
✅ **SSL/TLS Support** - `ssl=prefer` configured by default
✅ **Redis Async** - Async Redis support for caching
✅ **SQLite Fallback** - Still works for development

## 🔧 Configuration

### Database URL Formats
```
# SQLite (Dev)
sqlite:///./alia.db

# PostgreSQL (Local)
postgresql+asyncpg://user:pass@localhost:5432/dbname

# PostgreSQL with SSL
postgresql+asyncpg://user:pass@host:5432/dbname?sslmode=require

# Render.com
postgresql+asyncpg://user:pass@host.render.com:5432/dbname
```

### Connection Pool
```python
pool_size=20           # Base connections
max_overflow=40        # Extra connections
pool_pre_ping=True     # Validate connections
pool_recycle=300       # Recycle after 5 min
```

## 🐛 Troubleshooting

| Error | Solution |
|-------|----------|
| `MissingGreenlet` | ✅ Fixed - async operations removed from sync context |
| Connection timeout | Check DB credentials and firewall |
| Redis connection failed | Redis optional - app works without it |
| SSL certificate error | Set `sslmode=prefer` or use proper certs |

## 📚 Documentation

- `ASYNC_DB_SETUP.md` - Complete setup guide
- `ASYNC_DB_MIGRATION_SUMMARY.md` - All changes made
- `.env.example` - Configuration reference

## ✅ Verification Checklist

- [ ] `pip install -r requirements.txt` successful
- [ ] DATABASE_URL configured
- [ ] `python verify_db.py` passes
- [ ] `python run_app.py` starts without errors
- [ ] `/health` endpoint responds
- [ ] Database tables created by Alembic

## 🚢 Render.com Deployment

1. Set environment variables in Render dashboard
2. Create `.render/start.sh`:
```bash
#!/bin/bash
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
```

3. Update Dockerfile or Render config to use start script
4. Deploy!

## 📞 Support

For issues:
1. Check `ASYNC_DB_SETUP.md` troubleshooting section
2. Run `verify_db.py` to diagnose
3. Check environment variables: `printenv | grep DATABASE`
4. Review application logs for SQL errors
