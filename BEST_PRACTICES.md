# Best Practices & Troubleshooting Guide

## ✅ Best Practices for Async PostgreSQL

### 1. Database URL Management
```python
# ✅ GOOD: Use environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./alia.db")

# ❌ BAD: Hardcode credentials
DATABASE_URL = "postgresql://root:password123@localhost/db"
```

### 2. Connection Pooling
```python
# ✅ GOOD: Configure appropriate pool sizes
pool_size=20,           # Adjust based on concurrent requests
max_overflow=40,        # Additional connections when needed
pool_pre_ping=True,     # Validate connections
pool_recycle=300        # Recycle stale connections
```

### 3. Using Database Sessions
```python
# ✅ GOOD: Use async context manager
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# ❌ BAD: Synchronous yield (blocking)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4. Query Execution
```python
# ✅ GOOD: Await all async operations
user = await db.query(User).filter(User.id == user_id).first()
await db.commit()

# ❌ BAD: Missing await (will fail)
user = db.query(User).filter(User.id == user_id).first()  # Error!
```

### 5. Transaction Management
```python
# ✅ GOOD: Explicit transaction handling
try:
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
except Exception as e:
    await db.rollback()
    raise

# ❌ BAD: No error handling
db.add(new_user)
await db.commit()
```

## 🐛 Common Issues & Solutions

### Issue 1: "MissingGreenlet" Error
```
Error: sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called

Cause: Synchronous operation in async context
Solution: ✅ FIXED - No sync create_all() in startup

Verification:
  - app/main.py lifespan doesn't call Base.metadata.create_all()
  - Alembic handles schema creation
  - All DB operations use await
```

### Issue 2: "RuntimeError: Event loop is closed"
```
Error: RuntimeError: Event loop is closed

Cause: Improper async session cleanup
Solution:
  1. Use async with AsyncSessionLocal():
  2. Ensure await session.close() called
  3. Check for background tasks still running

Fix:
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()  # Explicit close
```

### Issue 3: "Connection timeout" with Live Database
```
Error: asyncpg.exceptions.ClientError: timeout

Causes:
  1. Firewall blocking connection
  2. Database server offline
  3. Invalid credentials
  4. Pool exhausted

Solutions:
  - Check DATABASE_URL format
  - Test: python verify_db.py
  - Verify firewall: telnet host port
  - Check pool settings in database.py
  - Monitor connection count: SELECT count(*) FROM pg_stat_activity;
```

### Issue 4: "SSL certificate verify failed"
```
Error: SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]

Cause: SSL/TLS verification with self-signed cert
Solutions:
  1. Use proper certificates
  2. Disable SSL:
     DATABASE_URL="postgresql+asyncpg://...?sslmode=disable"
  3. Set SSL mode:
     DATABASE_URL="postgresql+asyncpg://...?sslmode=require"
```

### Issue 5: "Max connections exceeded"
```
Error: FATAL: too many connections

Cause: Connection pool leaks or too small
Solution:
  1. Increase pool size:
     pool_size=50  # Increase if many concurrent requests
  2. Check for leaked connections:
     # In postgres:
     SELECT * FROM pg_stat_activity;
  3. Verify session cleanup in routes
```

### Issue 6: "No module named 'asyncpg'"
```
Error: ModuleNotFoundError: No module named 'asyncpg'

Solution:
  pip install -r requirements.txt
  # or
  pip install asyncpg==0.29.0
```

## 🔍 Debugging Tips

### 1. Enable SQL Logging
```python
# In app/config.py or .env
DEBUG=true  # Enables echo=True in create_async_engine
```

### 2. Monitor Connections
```bash
# PostgreSQL
psql -h host -d dbname -c "SELECT count(*) FROM pg_stat_activity;"

# Watch connections
watch "psql -h host -d dbname -c \"SELECT count(*) FROM pg_stat_activity;\""
```

### 3. Test Async Connection
```python
# verify_db.py script does this:
async with engine.connect() as conn:
    await conn.connection.ping()
    print("✓ Connection OK")
```

### 4. Check Environment Variables
```bash
echo $DATABASE_URL
echo $REDIS_URL
echo $SECRET_KEY
```

### 5. View Application Logs
```bash
# Development
python run_app.py 2>&1 | grep -E "ERROR|WARNING|Connection"

# Production (via systemd)
journalctl -u alia_platform -f
```

## 📊 Performance Optimization

### 1. Connection Pool Tuning
```python
# For high traffic (1000+ req/s):
pool_size=50
max_overflow=100

# For moderate traffic (100-1000 req/s):
pool_size=20
max_overflow=40

# For low traffic (dev/test):
pool_size=5
max_overflow=10
```

### 2. Query Optimization
```python
# ✅ GOOD: Batch operations
users = await db.query(User).filter(User.role == "student").all()

# ❌ BAD: N+1 queries
for user_id in user_ids:
    user = await db.query(User).filter(User.id == user_id).first()  # Loop!
```

### 3. Caching with Redis
```python
# ✅ GOOD: Cache frequently accessed data
async def get_user(user_id: str):
    # Check cache first
    cached = await redis_client.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)

    # Query DB
    user = await db.query(User).filter(User.id == user_id).first()

    # Cache result
    await redis_client.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

### 4. Connection Recycling
```python
# Already configured:
pool_recycle=300  # Recycle every 5 minutes

# For Render.com with connection timeout:
pool_recycle=120  # More frequent recycling
```

## 🚀 Production Checklist

- [ ] DATABASE_URL configured with proper PostgreSQL async format
- [ ] SECRET_KEY set to strong random value
- [ ] DEBUG=false in production
- [ ] Redis configured for caching
- [ ] SSL/TLS enabled for database connection
- [ ] Alembic migrations up to date: `alembic upgrade head`
- [ ] Connection pool sizes tuned for expected load
- [ ] Run `verify_db.py` before deployment
- [ ] Monitor application logs for errors
- [ ] Setup database backups
- [ ] Configure monitoring/alerting

## 📝 Migration Examples

### Create New Table
```bash
alembic revision --autogenerate -m "Add courses table"
alembic upgrade head
```

### Add Column
```bash
alembic revision --autogenerate -m "Add status column to courses"
alembic upgrade head
```

### Rollback Changes
```bash
# See history
alembic history

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade ae1027a6acf
```

## 🔐 Security Best Practices

1. **Environment Variables**
   - Never commit .env file
   - Use .env.example as template
   - Rotate secrets regularly

2. **Database Credentials**
   - Use strong passwords (16+ chars, mixed case, numbers, symbols)
   - Use separate DB user for app (least privilege)
   - Enable SSL/TLS for all connections

3. **Connection Pooling**
   - Don't exceed necessary pool size
   - Monitor for connection leaks
   - Use pre-ping for stale connection detection

4. **Alembic Migrations**
   - Review migrations before applying
   - Test migrations in staging first
   - Keep backups before migrations

## 📞 Getting Help

1. Check `ASYNC_DB_SETUP.md` for detailed setup
2. Run `verify_db.py` to diagnose issues
3. Review application logs
4. Check PostgreSQL logs if database issue
5. Test with simple query via psql:
   ```bash
   psql postgresql://user:pass@host:5432/dbname -c "SELECT 1;"
   ```

## 🎯 Summary

✅ Use async/await for all database operations
✅ Configure connection pooling appropriately
✅ Use environment variables for secrets
✅ Monitor connections and pool usage
✅ Test changes in staging before production
✅ Keep Alembic migrations updated
✅ Enable SSL/TLS for live databases
✅ Use Redis for caching when possible
