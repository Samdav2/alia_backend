# 🔄 AsyncSession Migration - Quick Fix Guide

## Problem
`AttributeError: 'AsyncSession' object has no attribute 'query'`

Sync services using `.query()` won't work with AsyncSession.

## What's Fixed So Far ✅
- ✅ `app/services/auth_service.py` - Converted to async
- ✅ `app/services/user_service.py` - Converted to async
- ✅ `app/api/auth.py` - Updated to use async services

## Services Still Needing Updates

These still use sync `.query()`:
- `course_service.py`
- `analytics_service.py`
- `file_service.py`
- `lecturer_service.py`
- `notification_service.py`
- `admin_service.py`
- `progress_service.py`

## How to Migrate Each Service

### Pattern 1: Get Single Record
**Before (Sync):**
```python
user = db.query(User).filter(User.id == user_id).first()
```

**After (Async):**
```python
from sqlalchemy import select
result = await db.execute(select(User).filter(User.id == user_id))
user = result.scalar_one_or_none()
```

### Pattern 2: Get Multiple Records
**Before (Sync):**
```python
users = db.query(User).filter(User.role == role).all()
```

**After (Async):**
```python
from sqlalchemy import select
result = await db.execute(select(User).filter(User.role == role))
users = result.scalars().all()
```

### Pattern 3: Create Record
**Before (Sync):**
```python
db.add(user)
db.commit()
db.refresh(user)
```

**After (Async):**
```python
db.add(user)
await db.commit()
await db.refresh(user)
```

### Pattern 4: Update Record
**Before (Sync):**
```python
user.name = "new name"
db.commit()
```

**After (Async):**
```python
user.name = "new name"
await db.commit()
```

### Pattern 5: Count Records
**Before (Sync):**
```python
total = db.query(User).count()
```

**After (Async):**
```python
from sqlalchemy import func, select
result = await db.execute(select(func.count(User.id)))
total = result.scalar() or 0
```

## API Changes

### Before (Sync)
```python
from sqlalchemy.orm import Session

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

### After (Async)
```python
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

## Key Changes to Remember

1. Change import:
   ```python
   from sqlalchemy.orm import Session  → from sqlalchemy.ext.asyncio import AsyncSession
   ```

2. Add `await` to all database calls:
   ```python
   db.commit()  → await db.commit()
   db.refresh(obj)  → await db.refresh(obj)
   db.execute(stmt)  → await db.execute(stmt)
   ```

3. Use `select()` with filters:
   ```python
   db.query(User).filter(...)  → select(User).filter(...)
   ```

4. Make methods async:
   ```python
   def method(db: Session):  → async def method(db: AsyncSession):
   ```

5. Await all async method calls:
   ```python
   service.method(db)  → await service.method(db)
   ```

## Migration Priority

1. **Priority 1** (Already done):
   - ✅ auth_service.py
   - ✅ user_service.py

2. **Priority 2** (Fix next):
   - `course_service.py` - Used by course routes
   - `progress_service.py` - Used by progress routes
   - `file_service.py` - Used by file routes

3. **Priority 3** (Can wait):
   - `analytics_service.py`
   - `lecturer_service.py`
   - `notification_service.py`
   - `admin_service.py`

## Testing After Migration

For each service endpoint:
1. Test in isolation first
2. Verify database operations work
3. Check error handling
4. Test with live database

## Status

- Services Updated: 2/9 (22%)
- ✅ auth_service.py
- ✅ user_service.py
- ⏳ Remaining: 7 services

## Next Steps

1. Update remaining Priority 2 services
2. Test each endpoint thoroughly
3. Deploy and monitor
4. Update Priority 3 services

See `ASYNC_SESSION_MIGRATION.md` for detailed migration guide.
