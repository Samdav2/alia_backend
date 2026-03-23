# ALIA Platform Backend

Adaptive Learning Intelligence Assistant (ALIA) - A comprehensive, secure, and high-performance backend API for educational platforms with advanced accessibility features.

## 🚀 Features

### Core Functionality
- **User Management**: Registration, authentication, profile management
- **Course Management**: Create, manage, and deliver educational content
- **Progress Tracking**: Real-time learning progress and analytics
- **AI Integration**: Intelligent chat assistant and content simplification
- **Accessibility**: Comprehensive accessibility features and tracking
- **File Management**: Secure file upload and management
- **Notifications**: Real-time notification system

### Security & Performance
- **JWT Authentication**: Secure token-based authentication
- **Role-based Access Control**: Student, Lecturer, Admin roles
- **Rate Limiting**: Configurable rate limits per endpoint
- **Input Validation**: Comprehensive request validation
- **SQL Injection Protection**: Parameterized queries
- **CORS Protection**: Configurable CORS policies
- **Security Headers**: Comprehensive security headers

### Architecture
- **Clean Architecture**: Separation of concerns with services, models, schemas
- **Async/Await**: High-performance asynchronous operations
- **Database Migrations**: Alembic for database version control
- **Caching**: Redis for performance optimization
- **Containerization**: Docker and Docker Compose support
- **Load Balancing**: Nginx reverse proxy configuration

## 🏗️ Project Structure

```
app/
├── api/                    # API route handlers
│   ├── auth.py            # Authentication endpoints
│   ├── users.py           # User management
│   ├── courses.py         # Course management
│   ├── enrollments.py     # Enrollment management
│   ├── progress.py        # Progress tracking
│   ├── analytics.py       # Analytics endpoints
│   ├── notifications.py   # Notification management
│   ├── files.py           # File management
│   ├── ai.py              # AI services
│   └── admin.py           # Admin endpoints
├── core/                  # Core utilities
│   ├── security.py        # Security utilities
│   └── exceptions.py      # Custom exceptions
├── models/                # Database models
│   ├── user.py           # User model
│   ├── course.py         # Course models
│   ├── progress.py       # Progress models
│   ├── analytics.py      # Analytics models
│   ├── notification.py   # Notification model
│   └── file.py           # File model
├── schemas/               # Pydantic schemas
│   ├── auth.py           # Authentication schemas
│   ├── user.py           # User schemas
│   ├── course.py         # Course schemas
│   ├── progress.py       # Progress schemas
│   ├── analytics.py      # Analytics schemas
│   ├── notification.py   # Notification schemas
│   ├── file.py           # File schemas
│   └── ai.py             # AI service schemas
├── services/              # Business logic
│   ├── auth_service.py   # Authentication service
│   ├── user_service.py   # User management service
│   ├── course_service.py # Course management service
│   ├── progress_service.py # Progress tracking service
│   ├── analytics_service.py # Analytics service
│   ├── notification_service.py # Notification service
│   ├── file_service.py   # File management service
│   └── ai_service.py     # AI services
├── config.py             # Configuration settings
├── database.py           # Database configuration
└── main.py               # FastAPI application
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- SQLite (included with Python) or PostgreSQL 13+ (optional)
- Redis 6+ (optional, for caching)
- Docker (optional)

### Instant Start with SQLite (Recommended for Development)

1. **Clone the repository**
```bash
git clone <repository-url>
cd alia-platform-backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Quick start (creates database and starts server)**
```bash
python quickstart.py
```

That's it! The API will be running at `http://localhost:8000`

### Manual Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd alia-platform-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env if needed (SQLite is configured by default)
```

5. **Create database tables**
```bash
python -c "from app.database import Base, engine; from app.models import *; Base.metadata.create_all(bind=engine)"
```

6. **Run the application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Switching to PostgreSQL

When you're ready to use PostgreSQL:

1. **Install PostgreSQL** and create a database

2. **Update .env file**
```bash
# Comment out SQLite
# DATABASE_URL=sqlite:///./alia.db

# Uncomment and configure PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/alia_db
```

3. **Recreate tables**
```bash
python -c "from app.database import Base, engine; from app.models import *; Base.metadata.create_all(bind=engine)"
```

The application automatically detects the database type and uses the appropriate UUID implementation!

### Docker Development

1. **Start services**
```bash
docker-compose up -d
```

2. **Run migrations**
```bash
docker-compose exec api alembic upgrade head
```

## 📚 API Documentation

### Base URL
- Development: `http://localhost:8000`
- Production: `https://api.alia.edu.ng`

### Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - User logout

#### User Management
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users` - Get all users (Admin)

#### Course Management
- `GET /api/courses` - Get all courses
- `GET /api/courses/{id}` - Get course details
- `POST /api/courses` - Create course (Lecturer/Admin)
- `PUT /api/courses/{id}` - Update course
- `DELETE /api/courses/{id}` - Delete course (Admin)

#### Progress Tracking
- `GET /api/progress/{course_id}` - Get course progress
- `POST /api/progress/{course_id}/topics/{topic_id}` - Update topic progress

#### AI Services
- `POST /api/ai/chat` - Chat with AI assistant
- `POST /api/ai/simplify` - Simplify content
- `POST /api/voice/session` - Start voice session
- `POST /api/voice/transcribe` - Transcribe voice

### Interactive Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔧 Configuration

### Environment Variables

```bash
# Application
SECRET_KEY=your-super-secret-key
DEBUG=False
APP_NAME=ALIA Platform API

# Database
DATABASE_URL=postgresql://user:password@localhost/alia_db

# Redis
REDIS_URL=redis://localhost:6379

# AI Services
OPENAI_API_KEY=your-openai-api-key

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
AUTH_RATE_LIMIT_PER_MINUTE=5
```

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (Student, Lecturer, Admin)
- Password hashing with bcrypt
- Token expiration and refresh mechanism

### API Security
- Rate limiting per endpoint and user
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection
- Secure headers (HSTS, CSP, etc.)

### Data Protection
- Encrypted sensitive data
- Secure file upload with type validation
- Access logging and monitoring
- Environment-based configuration

## 📊 Performance Features

### Optimization
- Async/await for non-blocking operations
- Database connection pooling
- Redis caching for frequently accessed data
- Gzip compression for responses
- Efficient database queries with proper indexing

### Monitoring
- Request/response time tracking
- Health check endpoints
- Performance metrics logging
- Error tracking and reporting

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Test Structure
```
tests/
├── test_auth.py          # Authentication tests
├── test_users.py         # User management tests
├── test_courses.py       # Course management tests
├── test_progress.py      # Progress tracking tests
└── conftest.py           # Test configuration
```

## 🚀 Deployment

### Production Deployment

1. **Set up production environment**
```bash
# Set production environment variables
export DEBUG=False
export DATABASE_URL=postgresql://user:password@prod-db/alia_db
```

2. **Deploy with Docker**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Run migrations**
```bash
docker-compose exec api alembic upgrade head
```

### Performance Tuning
- Use multiple worker processes
- Configure database connection pooling
- Set up Redis clustering for high availability
- Use CDN for static file serving
- Configure proper caching strategies

## 📈 Monitoring & Logging

### Application Monitoring
- Health check endpoints
- Performance metrics
- Error tracking
- User activity monitoring

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Request/response logging
- Security event logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Add type hints where appropriate
- Write comprehensive docstrings

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: api-support@alia.edu.ng
- Documentation: https://docs.alia.edu.ng
- Status Page: https://status.alia.edu.ng

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added AI services and voice features
- **v1.2.0** - Enhanced accessibility features
- **v1.3.0** - Performance optimizations and security improvements# alia_backend
