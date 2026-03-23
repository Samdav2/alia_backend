# 📚 ALIA Platform - API Documentation Index

## Complete Backend API Documentation for Frontend Developers

All API endpoints are fully documented with request/response examples and frontend implementation code.

---

## 🚀 Quick Links

- **[Complete API Reference](./docs/API_COMPLETE_REFERENCE.md)** - Start here!
- **[Interactive API Docs](http://localhost:8000/docs)** - Swagger UI
- **[Alternative Docs](http://localhost:8000/redoc)** - ReDoc UI

---

## 📖 Documentation Structure

### 1. Authentication & Users
- **[Authentication API](./docs/API_AUTHENTICATION.md)**
  - Register, Login, Logout, Token Refresh
  - JWT token management
  - Code examples for React, Vue, Angular

- **[User Management API](./docs/API_USERS.md)**
  - Get/Update profile
  - User preferences
  - Accessibility settings
  - Admin user management

### 2. Courses & Learning
- **[Course Management API](./docs/API_COURSES.md)**
  - List/Get/Create/Update/Delete courses
  - Modules and topics
  - Course content structure
  - Frontend components examples

- **[Enrollment API](./docs/API_ENROLLMENTS.md)**
  - Enroll/Unenroll from courses
  - View enrollments
  - Enrollment status tracking

- **[Progress Tracking API](./docs/API_PROGRESS.md)**
  - Track course progress
  - Update topic completion
  - Time tracking
  - React hooks and Vue composables

### 3. Analytics & AI
- **[Analytics API](./docs/API_ANALYTICS.md)**
  - Performance metrics
  - Accessibility analytics
  - Weekly activity tracking
  - Dashboard components

- **[AI Services API](./docs/API_AI_SERVICES.md)**
  - AI chat assistant
  - Content simplification
  - Voice chat and transcription
  - Multi-language support

### 4. Files & Notifications
- **[Files & Notifications API](./docs/API_FILES_NOTIFICATIONS.md)**
  - File upload/download
  - Notification management
  - Real-time updates
  - File upload components

---

## 🎯 What's Included

### For Every Endpoint:
✅ HTTP method and URL  
✅ Authentication requirements  
✅ Request headers  
✅ Request body with field descriptions  
✅ Success response (200/201)  
✅ Error responses (400/401/403/404)  
✅ Field validation rules  
✅ Example requests (cURL, JavaScript)  

### Frontend Code Examples:
✅ React/TypeScript hooks  
✅ Vue.js composables  
✅ Angular services  
✅ Axios configuration  
✅ Error handling  
✅ Token management  
✅ Form validation  

---

## 🔧 Setup Instructions

### 1. Start Backend
```bash
# Quick start with SQLite
python quickstart.py

# Or manual start
uvicorn app.main:app --reload
```

### 2. Access Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### 3. Test API
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "test123",
    "role": "student",
    "department": "Computer Science"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'
```

---

## 📊 API Overview

### Total Endpoints: 40+

| Category | Endpoints | Auth Required |
|----------|-----------|---------------|
| Authentication | 4 | ❌ |
| User Management | 5 | ✅ |
| Courses | 8 | Mixed |
| Enrollments | 3 | ✅ |
| Progress | 2 | ✅ |
| Analytics | 3 | ✅ |
| AI Services | 4 | ✅ |
| Files | 3 | ✅ |
| Notifications | 3 | ✅ |
| Admin | 2 | ✅ Admin |

---

## 🔑 Authentication Flow

```
┌─────────────┐
│   Register  │
│   or Login  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Get access_token   │
│  & refresh_token    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Store tokens in    │
│  localStorage       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Include token in   │
│  all API requests   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Token expires?     │
│  Use refresh_token  │
└─────────────────────┘
```

---

## 💻 Frontend Integration

### React Example
```typescript
// hooks/useAuth.ts
import { useState } from 'react';
import axios from 'axios';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token'));

  const login = async (email: string, password: string) => {
    const response = await axios.post('/api/auth/login', { email, password });
    const { user, token, refresh_token } = response.data.data;
    
    localStorage.setItem('access_token', token);
    localStorage.setItem('refresh_token', refresh_token);
    setToken(token);
    setUser(user);
  };

  return { user, token, login };
};
```

### Vue Example
```javascript
// composables/useAuth.js
import { ref } from 'vue';
import axios from 'axios';

export function useAuth() {
  const user = ref(null);
  const token = ref(localStorage.getItem('access_token'));

  const login = async (email, password) => {
    const response = await axios.post('/api/auth/login', { email, password });
    const { user: userData, token: accessToken, refresh_token } = response.data.data;
    
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refresh_token);
    token.value = accessToken;
    user.value = userData;
  };

  return { user, token, login };
}
```

---

## 🎨 Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": null
  }
}
```

### Pagination Response
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

---

## 🔒 Security Features

✅ JWT authentication  
✅ Password hashing (bcrypt)  
✅ Role-based access control  
✅ Rate limiting  
✅ Input validation  
✅ SQL injection prevention  
✅ XSS protection  
✅ CSRF protection  

---

## 📱 Supported Platforms

- ✅ Web (React, Vue, Angular, Svelte)
- ✅ Mobile (React Native, Flutter)
- ✅ Desktop (Electron)
- ✅ Any HTTP client

---

## 🧪 Testing Tools

### Postman
1. Import collection from `/docs`
2. Set environment variables
3. Test all endpoints

### cURL
```bash
# All examples in documentation use cURL
# Copy and paste to test
```

### Swagger UI
- Interactive testing at http://localhost:8000/docs
- Try out endpoints directly
- See request/response in real-time

---

## 📈 Rate Limits

| Endpoint Type | Limit |
|--------------|-------|
| Authentication | 5/min |
| AI Chat | 30/min |
| File Upload | 10/min |
| General API | 100/min |

---

## 🆘 Common Issues

### CORS Errors
✅ Backend configured for development  
✅ Update `allowed_origins` for production  

### 401 Unauthorized
✅ Check token is included  
✅ Verify token hasn't expired  
✅ Try refreshing token  

### 404 Not Found
✅ Verify endpoint URL  
✅ Check HTTP method  
✅ Ensure backend is running  

---

## 📞 Support

- **Documentation**: [docs/](./docs/)
- **Interactive API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Email**: api-support@alia.edu.ng

---

## 🎓 Learning Path

1. **Start Here**: [API_COMPLETE_REFERENCE.md](./docs/API_COMPLETE_REFERENCE.md)
2. **Authentication**: [API_AUTHENTICATION.md](./docs/API_AUTHENTICATION.md)
3. **Build Features**: Choose relevant endpoint docs
4. **Test**: Use Swagger UI or Postman
5. **Integrate**: Use provided code examples

---

## ✨ Features

- 🔐 Secure authentication with JWT
- 👥 User management with roles
- 📚 Complete course management
- 📊 Progress tracking
- 📈 Analytics and reporting
- 🤖 AI chat assistant
- 🎤 Voice interaction
- ♿ Accessibility features
- 🔔 Real-time notifications
- 📁 File management

---

**Ready to build? Start with [API_COMPLETE_REFERENCE.md](./docs/API_COMPLETE_REFERENCE.md)!** 🚀