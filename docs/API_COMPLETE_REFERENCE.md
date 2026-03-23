# ALIA Platform - Complete API Reference

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [Rate Limiting](#rate-limiting)
5. [API Endpoints Overview](#api-endpoints-overview)
6. [Frontend Integration Guide](#frontend-integration-guide)

---

## Getting Started

### Base URL
```
Development: http://localhost:8000
Production: https://api.alia.edu.ng
```

### API Version
Current Version: `v1.0`

### Response Format
All API responses follow this structure:

**Success Response:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": { ... }
  }
}
```

---

## Authentication

### Token-Based Authentication
The API uses JWT (JSON Web Tokens) for authentication.

**Include token in requests:**
```
Authorization: Bearer {your_access_token}
```

**Token Expiration:**
- Access Token: 30 minutes
- Refresh Token: 7 days

**Refresh Flow:**
1. Access token expires
2. Use refresh token to get new access token
3. Continue making requests with new token

See [API_AUTHENTICATION.md](./API_AUTHENTICATION.md) for details.

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Request validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Codes

| Code | Description |
|------|-------------|
| `UNAUTHORIZED` | Invalid or missing authentication |
| `FORBIDDEN` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `VALIDATION_ERROR` | Invalid request data |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

---

## Rate Limiting

### Limits by Endpoint Type

| Endpoint Type | Limit |
|--------------|-------|
| Authentication | 5 requests/minute |
| AI Chat | 30 requests/minute |
| File Upload | 10 requests/minute |
| General API | 100 requests/minute |

### Rate Limit Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1615824000
```

---

## API Endpoints Overview

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | User logout |

[Full Documentation](./API_AUTHENTICATION.md)

---

### User Management Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/profile` | Get user profile | ✅ |
| PUT | `/api/users/profile` | Update profile | ✅ |
| GET | `/api/users` | List all users | ✅ Admin |
| PUT | `/api/users/{id}/deactivate` | Deactivate user | ✅ Admin |
| PUT | `/api/users/{id}/activate` | Activate user | ✅ Admin |

[Full Documentation](./API_USERS.md)

---

### Course Management Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/courses` | List courses | ❌ |
| GET | `/api/courses/{id}` | Get course details | ❌ |
| POST | `/api/courses` | Create course | ✅ Lecturer/Admin |
| PUT | `/api/courses/{id}` | Update course | ✅ Lecturer/Admin |
| DELETE | `/api/courses/{id}` | Delete course | ✅ Admin |
| GET | `/api/courses/{id}/modules` | Get modules | ❌ |
| GET | `/api/courses/{id}/modules/{mid}/topics` | Get topics | ❌ |
| GET | `/api/courses/{id}/topics/{tid}` | Get topic details | ❌ |

[Full Documentation](./API_COURSES.md)

---

### Enrollment Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/enrollments` | Get user enrollments | ✅ |
| POST | `/api/enrollments` | Enroll in course | ✅ |
| DELETE | `/api/enrollments/{id}` | Unenroll from course | ✅ |

[Full Documentation](./API_ENROLLMENTS.md)

---

### Progress Tracking Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/progress/{course_id}` | Get course progress | ✅ |
| POST | `/api/progress/{course_id}/topics/{topic_id}` | Update topic progress | ✅ |

[Full Documentation](./API_PROGRESS.md)

---

### Analytics Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/analytics/performance` | Get performance analytics | ✅ |
| GET | `/api/analytics/accessibility` | Get accessibility analytics | ✅ |
| POST | `/api/analytics/accessibility/{feature}` | Track feature usage | ✅ |

[Full Documentation](./API_ANALYTICS.md)

---

### AI Services Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/ai/chat` | Chat with AI assistant | ✅ |
| POST | `/api/ai/simplify` | Simplify content | ✅ |
| POST | `/api/voice/session` | Start voice session | ✅ |
| POST | `/api/voice/transcribe` | Transcribe voice | ✅ |

[Full Documentation](./API_AI_SERVICES.md)

---

### File Management Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/files/upload` | Upload file | ✅ |
| GET | `/api/files/{id}` | Get file info | ✅ |
| DELETE | `/api/files/{id}` | Delete file | ✅ |

---

### Notification Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/notifications` | Get notifications | ✅ |
| PUT | `/api/notifications/{id}/read` | Mark as read | ✅ |
| PUT | `/api/notifications/read-all` | Mark all as read | ✅ |

[Full Documentation](./API_FILES_NOTIFICATIONS.md)

---

### Admin Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/admin/dashboard` | Get dashboard stats | ✅ Admin |
| GET | `/api/admin/users/{id}/accessibility` | Get user accessibility report | ✅ Admin |

---

## Frontend Integration Guide

### Setup Axios Instance

```typescript
// api/client.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
          refresh_token: refreshToken
        });

        const { token, refresh_token } = response.data.data;
        localStorage.setItem('access_token', token);
        localStorage.setItem('refresh_token', refresh_token);

        originalRequest.headers.Authorization = `Bearer ${token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

### TypeScript Types

```typescript
// types/api.ts
export interface User {
  id: string;
  full_name: string;
  email: string;
  role: 'student' | 'lecturer' | 'admin';
  department: string;
  student_id?: string;
  is_active: boolean;
  preferences: UserPreferences;
  disability_info?: DisabilityInfo;
  created_at: string;
  updated_at?: string;
  last_login?: string;
}

export interface Course {
  id: string;
  code: string;
  title: string;
  description: string;
  instructor: string;
  department: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  duration: string;
  enrollment_count: number;
  rating: number;
  tags: string[];
  thumbnail: string;
  is_active: boolean;
  created_at: string;
}

export interface Progress {
  course_id: string;
  user_id: string;
  completed_topics: number;
  total_topics: number;
  completion_percentage: number;
  time_spent: number;
  current_topic?: string;
  last_accessed_at: string;
  topic_progress: TopicProgress[];
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}
```

### React Context for Auth

```typescript
// context/AuthContext.tsx
import React, { createContext, useState, useContext, useEffect } from 'react';
import { apiClient } from '../api/client';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (userData: RegisterData) => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('access_token')
  );

  useEffect(() => {
    if (token) {
      fetchUserProfile();
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const response = await apiClient.get('/api/users/profile');
      setUser(response.data.data);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      logout();
    }
  };

  const login = async (email: string, password: string) => {
    const response = await apiClient.post('/api/auth/login', { email, password });
    const { user, token, refresh_token } = response.data.data;
    
    localStorage.setItem('access_token', token);
    localStorage.setItem('refresh_token', refresh_token);
    setToken(token);
    setUser(user);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    setUser(null);
  };

  const register = async (userData: RegisterData) => {
    const response = await apiClient.post('/api/auth/register', userData);
    const { user, token, refresh_token } = response.data.data;
    
    localStorage.setItem('access_token', token);
    localStorage.setItem('refresh_token', refresh_token);
    setToken(token);
    setUser(user);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        register,
        isAuthenticated: !!token
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

---

## Testing the API

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"test123","role":"student","department":"CS"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Get Profile (with token)
curl -X GET http://localhost:8000/api/users/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Using Postman

1. Import the API collection
2. Set environment variable `base_url` to `http://localhost:8000`
3. Set environment variable `token` after login
4. Use `{{base_url}}` and `{{token}}` in requests

---

## Support

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

For issues or questions, contact: api-support@alia.edu.ng