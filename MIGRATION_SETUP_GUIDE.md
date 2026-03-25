# Database Migration Setup Guide

## Problem
The production PostgreSQL database on Render.com doesn't have the required tables. The error `relation "users" does not exist` indicates that the Alembic migrations haven't been applied.

## Solution
The application now automatically runs database migrations on startup via `app/main.py`.

## How It Works

### 1. Automatic Migration on Startup (RECOMMENDED)
The application will automatically:
- Connect to the PostgreSQL database
- Check if migrations have been applied
- Run `alembic upgrade head` to create all tables
- Continue with the app startup

**No additional setup required** - Just deploy the updated code!

### 2. Manual Migration (If Needed)

If you need to run migrations manually:

```bash
# Navigate to project directory
cd /home/rehack/Agentic_lms_backend

# Run all pending migrations
alembic upgrade head

# Check migration history
alembic current

# See available migrations
alembic branches
```

## Environment Setup

Ensure your `.env` file has the correct database URL:

```env
# For Render.com PostgreSQL (example)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database_name

# The migration system will automatically convert this to sync URL for Alembic
```

## Generated Migrations

The following migration has been automatically created:
- `migrations/versions/3ddc33d673e0_initial_schema_creation.py`

This migration creates all tables including:
- users
- courses
- modules
- topics
- files
- progress
- enrollments
- quizzes
- assessments
- notifications
- announcements
- departments
- audit_logs

## Troubleshooting

### Migration Already Applied
If you see warnings about migrations already being applied, that's normal:
```
INFO:root:Running database migrations...
⚠ Migration warning (may be normal): ...
```
The app continues normally - migrations only apply once.

### Connection Issues
If migrations fail due to connection issues:
1. Verify your `DATABASE_URL` environment variable is correct
2. Check that PostgreSQL is accessible from your environment
3. Ensure the database user has permissions to create tables

### Rollback (If Needed)
To rollback to a previous migration state:
```bash
# Rollback one step
alembic downgrade -1

# Rollback all migrations
alembic downgrade base
```

## Deployment Instructions

### For Render.com:
1. Update your repository with the new code
2. Push changes:
   ```bash
   git add .
   git commit -m "Enable automatic database migrations on startup"
   git push
   ```
3. Render.com will automatically redeploy
4. Migrations will run automatically on first startup
5. Monitor logs to confirm successful migration

### For Other Cloud Platforms:
The migration system works the same way - just deploy the updated code and migrations will run automatically on startup.

## Technical Details

### Migration System Architecture
- **Alembic**: Database schema migration tool
- **Async Support**: Migrations run with SQLAlchemy async engine
- **Auto-startup**: Migrations execute during app lifespan startup
- **Error Handling**: Warnings don't block app startup (migrations may already be applied)

### URL Conversion
The migration system handles async/sync URL conversion:
- App uses: `postgresql+asyncpg://...` (async)
- Alembic uses: `postgresql://...` (sync)
- Automatic conversion in `migrations/env.py`

## Files Modified

1. **app/main.py**: Added automatic migration execution in lifespan startup
2. **migrations/env.py**: Added async URL conversion for Alembic
3. **migrations/versions/**: Created initial schema migration

## Next Steps

After migrations are applied:
1. ✅ App will start successfully
2. ✅ Database tables will be created
3. ✅ User registration will work
4. ✅ All API endpoints will function normally

For any issues, check the application logs for detailed error messages.
