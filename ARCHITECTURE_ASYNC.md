# Architecture Diagram - Async PostgreSQL Implementation

## Before (Broken)
```
┌─────────────────────────────────────────┐
│        FastAPI Application              │
├─────────────────────────────────────────┤
│                                         │
│  Startup (async context manager)        │
│  ├─ Sync engine created ✓              │
│  ├─ Try: Base.metadata.create_all()    │
│  │   ├─ Calls sync operations          │
│  │   ├─ Inside async context with      │
│  │   │   asyncpg driver                │
│  │   └─ ❌ GREENLET ERROR!             │
│  └─ Application crashes                │
│                                         │
└─────────────────────────────────────────┘

Error: sqlalchemy.exc.MissingGreenlet
Reason: Sync operations in async context with async driver
```

## After (Fixed)
```
┌──────────────────────────────────────────────────────────┐
│            FastAPI Application                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  app/database.py                                         │
│  ├─ Create async_engine (asyncpg://...)                 │
│  ├─ Create AsyncSessionLocal factory                    │
│  ├─ init_redis() → async Redis                          │
│  └─ dispose_engine() → cleanup                          │
│                                                          │
│  app/main.py - Lifespan                                 │
│  ├─ @asynccontextmanager lifespan()                     │
│  ├─ await init_redis()                                  │
│  ├─ engine.connect() → ping DB (async)                  │
│  ├─ yield (app running)                                 │
│  ├─ await close_redis()                                 │
│  └─ await dispose_engine()                              │
│                                                          │
│  Alembic (separate process)                             │
│  ├─ run_app.py executes: alembic upgrade head           │
│  ├─ Creates/updates schema                              │
│  └─ Independent of app startup                          │
│                                                          │
└──────────────────────────────────────────────────────────┘

Result: ✅ App starts successfully, handles async operations
```

## Request Flow - Async Database Operations

```
┌─────────────────────────────────────────────────────────┐
│                 HTTP Request                            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Route Handler                       │
│   async def create_user(..., db = Depends(get_db)):    │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│           get_db() Dependency                           │
│   async with AsyncSessionLocal() as session:           │
│       yield session                                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│        AsyncSession (asyncpg connection)               │
│                                                         │
│  Query Flow:                                            │
│  ├─ db.query(User).filter(...) → creates query        │
│  ├─ await session.execute(query)  → sends to DB       │
│  ├─ await session.commit()        → commits changes   │
│  └─ await session.close()         → releases conn     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│    PostgreSQL (via asyncpg driver)                      │
│                                                         │
│  Connection Pool:                                       │
│  ├─ 20 base connections                                │
│  ├─ 40 max overflow                                    │
│  └─ Pre-ping validation enabled                        │
└──────────────────────────────────────────────────────────┘
```

## Connection Pool Architecture

```
┌────────────────────────────────────────────────────────┐
│         Async Engine Connection Pool                    │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Base Pool (20 connections)                            │
│  ┌─────┐ ┌─────┐ ┌─────┐  ...  ┌─────┐              │
│  │ 🔌  │ │ 🔌  │ │ 🔌  │       │ 🔌  │              │
│  └─────┘ └─────┘ └─────┘       └─────┘              │
│                                                        │
│  Overflow (up to 40 additional)                        │
│  ┌─────┐ ┌─────┐ ┌─────┐  ...  ┌─────┐              │
│  │ ⚡  │ │ ⚡  │ │ ⚡  │       │ ⚡  │              │
│  └─────┘ └─────┘ └─────┘       └─────┘              │
│                                                        │
│  Pre-ping: Validates connections before use            │
│  Recycle: Every 300 seconds (5 minutes)                │
│  Timeout: 30 seconds per connection                    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Startup Sequence

```
1. python run_app.py
   │
   ├─ Alembic Upgrade
   │  ├─ Check schema version
   │  ├─ Apply pending migrations
   │  └─ ✓ Schema ready
   │
   ├─ uvicorn starts
   │  │
   │  └─ FastAPI app.__init__()
   │     │
   │     └─ lifespan startup:
   │        ├─ await init_redis()
   │        │  └─ ✓ Redis connected
   │        │
   │        ├─ engine.connect()
   │        │  ├─ Validate asyncpg available
   │        │  ├─ Connect to PostgreSQL
   │        │  ├─ await ping()
   │        │  └─ ✓ Database connected
   │        │
   │        └─ yield (app ready)
   │
   └─ ✅ Server listening on 0.0.0.0:8000
```

## Shutdown Sequence

```
Server Shutdown Signal (SIGTERM/SIGINT)
│
└─ lifespan shutdown:
   ├─ await close_redis()
   │  └─ ✓ Redis closed
   │
   ├─ await dispose_engine()
   │  └─ ✓ All connections returned to pool
   │
   └─ ✓ Graceful shutdown complete
```

## Database URL Transformation

```
Input:  postgresql://user:pass@localhost:5432/db
         │
         └─ app/database.py:
            if database_url.startswith("postgresql://"):
                database_url = database_url.replace(
                    "postgresql://",
                    "postgresql+asyncpg://",
                    1
                )
         │
         ▼
Output: postgresql+asyncpg://user:pass@localhost:5432/db
         │
         └─ create_async_engine(database_url)
            └─ Uses asyncpg driver ✓
```

## Service Layer Integration (Future)

```
Current:                           Future:
┌──────────┐                      ┌──────────┐
│ API Route│                      │ API Route│
└────┬─────┘                      └────┬─────┘
     │                                 │
     ▼                                 ▼
┌──────────────┐                 ┌──────────────┐
│ Service      │                 │ Service      │
│ (sync logic) │                 │ (async logic)│
└────┬─────────┘                 └────┬─────────┘
     │                                 │
     ▼                                 ▼
┌──────────────┐                 ┌──────────────┐
│ DB Session   │                 │ DB Session   │
│ (sync ops)   │                 │ (async ops)  │
└────┬─────────┘                 └────┬─────────┘
     │                                 │
     ▼                                 ▼
PostgreSQL  <──────────────────>  PostgreSQL
```

## Summary

✅ **Async Operations**: No blocking calls in startup
✅ **Connection Pooling**: Efficient resource management
✅ **Error Handling**: Greenlet error eliminated
✅ **Production Ready**: Proper SSL, timeouts, recycling
✅ **Scalable**: Handles high concurrency
