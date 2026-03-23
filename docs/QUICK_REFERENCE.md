# ALIA Platform API - Quick Reference Card

## Base URL
```
http://localhost:8000
```

## Authentication
```
Authorization: Bearer {access_token}
```

---

## 🔐 Authentication

```bash
# Register
POST /api/auth/register
{
  "full_name": "string",
  "email": "string",
  "password": "string",
  "role": "student|lecturer|admin",
  "department": "string"
}

# Login
POST /api/auth/login
{
  "email": "string",
  "password": "string"
}

# Refresh Token
POST /api/auth/refresh
{
  "refresh_token": "string"
}
```

---

## 👤 Users

```bash
# Get Profile
GET /api/users/profile

# Update Profile
PUT /api/users/profile
{
  "full_name": "string",
  "preferences": {...},
  "disability_info": {...}
}

# List Users (Admin)
GET /api/users?page=1&limit=20&role=student
```

---

## 📚 Courses

```bash
# List Courses
GET /api/courses?page=1&limit=20&search=python

# Get Course
GET /api/courses/{course_id}

# Create Course (Lecturer/Admin)
POST /api/courses
{
  "code": "CS101",
  "title": "string",
  "description": "string",
  "department": "string",
  "level": "beginner|intermediate|advanced"
}

# Get Modules
GET /api/courses/{course_id}/modules

# Get Topics
GET /api/courses/{course_id}/modules/{module_id}/topics

# Get Topic Details
GET /api/courses/{course_id}/topics/{topic_id}
```

---

## 📝 Enrollments

```bash
# Get My Enrollments
GET /api/enrollments

# Enroll in Course
POST /api/enrollments
{
  "course_id": "uuid"
}

# Unenroll
DELETE /api/enrollments/{course_id}
```

---

## 📊 Progress

```bash
# Get Course Progress
GET /api/progress/{course_id}

# Update Topic Progress
POST /api/progress/{course_id}/topics/{topic_id}
{
  "status": "in_progress|completed",
  "time_spent": 30,
  "score": 95.0
}
```

---

## 📈 Analytics

```bash
# Performance Analytics
GET /api/analytics/performance?period=month&course_id=uuid

# Accessibility Analytics
GET /api/analytics/accessibility

# Track Feature Usage
POST /api/analytics/accessibility/{feature}
```

---

## 🤖 AI Services

```bash
# Chat with AI
POST /api/ai/chat
{
  "message": "string",
  "context": {
    "course_id": "uuid",
    "topic_id": "uuid",
    "conversation_history": []
  }
}

# Simplify Content
POST /api/ai/simplify
{
  "content": "string",
  "level": "basic|intermediate|advanced",
  "language": "English|Igbo|Hausa|Yoruba"
}

# Start Voice Session
POST /api/voice/session

# Transcribe Voice
POST /api/voice/transcribe
{
  "session_id": "string",
  "audio_data": "base64_string",
  "language": "string"
}
```

---

## 📁 Files

```bash
# Upload File
POST /api/files/upload
Content-Type: multipart/form-data
file: [binary]

# Get File Info
GET /api/files/{file_id}

# Delete File
DELETE /api/files/{file_id}
```

---

## 🔔 Notifications

```bash
# Get Notifications
GET /api/notifications

# Mark as Read
PUT /api/notifications/{notification_id}/read

# Mark All as Read
PUT /api/notifications/read-all
```

---

## 🛡️ Admin

```bash
# Dashboard Stats
GET /api/admin/dashboard

# User Accessibility Report
GET /api/admin/users/{user_id}/accessibility
```

---

## 📋 Response Format

### Success
```json
{
  "success": true,
  "data": {...}
}
```

### Error
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "string",
    "details": null
  }
}
```

---

## 🔢 Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limit |
| 500 | Server Error |

---

## ⚡ Rate Limits

| Type | Limit |
|------|-------|
| Auth | 5/min |
| AI | 30/min |
| Upload | 10/min |
| General | 100/min |

---

## 🔑 Token Expiry

- Access Token: 30 minutes
- Refresh Token: 7 days

---

## 📱 Quick Setup

```javascript
// Axios Setup
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

---

## 🧪 Quick Test

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test","email":"test@test.com","password":"test123","role":"student","department":"CS"}'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# 3. Get Profile
curl -X GET http://localhost:8000/api/users/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

**Full Documentation**: [API_COMPLETE_REFERENCE.md](./API_COMPLETE_REFERENCE.md)