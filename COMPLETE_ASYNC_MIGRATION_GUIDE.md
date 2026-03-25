# Complete AsyncSession Migration Guide

## Current Status

### ✅ Complete (Ready to Use)
- `auth_service.py` - All async ✅
- `user_service.py` - All async ✅
- `auth.py` - All async ✅

### ❌ Incomplete (Still Using .query())
- `course_service.py`
- `analytics_service.py`
- `file_service.py`
- `lecturer_service.py`
- `notification_service.py`
- `admin_service.py`
- `progress_service.py`

## Quick Fix Template

Use this template to fix each remaining service:

```python
# OLD (Sync) - ❌ WRONG
from sqlalchemy.orm import Session
from sqlalchemy import func

def get_records(db: Session):
    result = db.query(Model).filter(...).all()
    count = db.query(Model).count()
    db.add(obj)
    db.commit()
    return result

# NEW (Async) - ✅ CORRECT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

async def get_records(db: AsyncSession):
    result = await db.execute(select(Model).filter(...))
    records = result.scalars().all()

    count_result = await db.execute(select(func.count(Model.id)))
    count = count_result.scalar() or 0

    db.add(obj)
    await db.commit()
    return records
```

## Conversion Checklist for Each Service

### Step 1: Update Imports
```python
# Remove
from sqlalchemy.orm import Session

# Add
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
```

### Step 2: Convert Method Signatures
```python
# Change all methods from:
def method_name(db: Session, ...):

# To:
async def method_name(db: AsyncSession, ...):
```

### Step 3: Replace .query() with select()
```python
# Search for patterns like:
db.query(Model)
db.query(Model).filter(...)
db.query(Model).filter(...).first()
db.query(Model).filter(...).all()

# Replace with:
select(Model)
select(Model).filter(...)
# Then wrap with: await db.execute(...)
```

### Step 4: Add await to DB Operations
```python
# Add await to:
await db.execute(...)
await db.commit()
await db.refresh(obj)
await db.flush()
```

### Step 5: Update Result Extraction
```python
# For single result:
result = await db.execute(select(Model).filter(...))
obj = result.scalar_one_or_none()

# For multiple results:
result = await db.execute(select(Model).filter(...))
objs = result.scalars().all()
```

### Step 6: Handle API Endpoint Changes
```python
# In the route/endpoint:
from sqlalchemy.ext.asyncio import AsyncSession

@router.get("/path")
async def endpoint(db: AsyncSession = Depends(get_db)):
    result = await service_method(db, ...)  # Add await!
    return result
```

## Service-by-Service Conversion Order

### Priority 1: Course Service
**File**: `app/services/course_service.py`
**Used by**: `app/api/courses.py`
**Difficulty**: Medium

Key methods to convert:
- `get_course()` - Single query
- `get_courses()` - Multiple with pagination
- `create_course()` - Insert
- `update_course()` - Update
- `delete_course()` - Delete

### Priority 2: Progress Service
**File**: `app/services/progress_service.py`
**Used by**: `app/api/progress.py`
**Difficulty**: Medium

Key methods to convert:
- `get_progress()` - Single query
- `create_progress()` - Insert
- `update_progress()` - Update

### Priority 3: File Service
**File**: `app/services/file_service.py`
**Used by**: `app/api/files.py`
**Difficulty**: Medium

Key methods to convert:
- `save_file_metadata()` - Insert
- `get_file()` - Single query
- `delete_file()` - Delete

### Priority 4: Remaining Services
- `analytics_service.py` - Statistics queries
- `lecturer_service.py` - Lecturer operations
- `notification_service.py` - Notifications
- `admin_service.py` - Admin operations

## Common Patterns to Convert

### Pattern: Single Record Retrieval
```python
# Before
user = db.query(User).filter(User.id == user_id).first()

# After
result = await db.execute(select(User).filter(User.id == user_id))
user = result.scalar_one_or_none()
```

### Pattern: List with Pagination
```python
# Before
total = db.query(Course).count()
courses = db.query(Course).offset(skip).limit(limit).all()

# After
count_result = await db.execute(select(func.count(Course.id)))
total = count_result.scalar() or 0

result = await db.execute(select(Course).offset(skip).limit(limit))
courses = result.scalars().all()
```

### Pattern: Insert New Record
```python
# Before
new_obj = Model(...)
db.add(new_obj)
db.commit()
db.refresh(new_obj)

# After
new_obj = Model(...)
db.add(new_obj)
await db.commit()
await db.refresh(new_obj)
```

### Pattern: Update Record
```python
# Before
obj = db.query(Model).filter(Model.id == id).first()
obj.field = new_value
db.commit()

# After
result = await db.execute(select(Model).filter(Model.id == id))
obj = result.scalar_one_or_none()
obj.field = new_value
await db.commit()
```

### Pattern: Delete Record
```python
# Before
obj = db.query(Model).filter(Model.id == id).first()
if obj:
    db.delete(obj)
    db.commit()

# After
result = await db.execute(select(Model).filter(Model.id == id))
obj = result.scalar_one_or_none()
if obj:
    await db.delete(obj)
    await db.commit()
```

### Pattern: Filter with Multiple Conditions
```python
# Before
results = db.query(Model).filter(
    Model.status == "active",
    Model.type == "course"
).all()

# After
result = await db.execute(select(Model).filter(
    Model.status == "active",
    Model.type == "course"
))
results = result.scalars().all()
```

### Pattern: Join Tables
```python
# Before
results = db.query(Course).join(Enrollment).filter(
    Enrollment.user_id == user_id
).all()

# After
from sqlalchemy import join
result = await db.execute(select(Course).join(Enrollment).filter(
    Enrollment.user_id == user_id
))
results = result.scalars().all()
```

## Testing After Update

For each service:

1. **Unit Test** - Test service method directly
2. **Integration Test** - Test via API endpoint
3. **Error Test** - Test error handling
4. **Database Test** - Verify DB changes

Example test:
```bash
# After updating auth_service, this works:
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "securepass123",
    "role": "student",
    "department": "Engineering"
  }'
```

## Debugging Tips

### Error: "Session is closed"
- Likely forgot an `await`
- Check all `db.execute()`, `db.commit()`, `db.refresh()` calls

### Error: ".query() not found"
- AsyncSession doesn't have `.query()`
- Use `select()` instead

### Error: "Coroutine was never awaited"
- Forgot to `await` an async call
- Add `await` before service method calls

### Error: "No results"
- Check if using `.scalar_one_or_none()` (returns None if not found)
- Or use `.scalars().all()` for lists

## Verification Commands

```bash
# Check if all services are async
grep -r "def " app/services/ | grep -v async | grep -v "__"
# Should return only non-database methods

# Check for remaining .query() usage
grep -r "\.query(" app/services/
# Should return nothing

# Check for missing awaits
grep -r "\.commit()" app/services/
grep -r "\.refresh(" app/services/
# Should all be "await .commit()" and "await .refresh()"
```

## Summary

**Total work**: ~7 more services to convert
**Time per service**: ~15-30 minutes
**Total estimated time**: 2-3 hours
**Complexity**: Low (pattern-based, repetitive)

**Start with**: `course_service.py` (most used)

Good luck! Follow the patterns and you'll have it done quickly. 🚀
