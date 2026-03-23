# Quick Start Guide - Lecturer & Admin Features

## 🚀 Getting Started

### 1. Start the Backend

```bash
# Make sure you're in the project directory
python quickstart.py

# Or manually
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

### 2. Access API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 👨‍🏫 Lecturer Quick Start

### Step 1: Login as Lecturer

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lecturer@example.com",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {...},
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "..."
  }
}
```

Save the `token` for subsequent requests.

---

### Step 2: Get Your Courses

```bash
curl -X GET "http://localhost:8000/api/lecturer/courses/my" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Step 3: Create a Module

```bash
curl -X POST "http://localhost:8000/api/lecturer/courses/{course_id}/modules" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Introduction to Python",
    "description": "Learn Python basics",
    "order": 1,
    "course_id": "your-course-uuid"
  }'
```

---

### Step 4: Create a Topic

```bash
curl -X POST "http://localhost:8000/api/lecturer/courses/modules/{module_id}/topics" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Variables and Data Types",
    "description": "Learn about variables",
    "duration": "30 minutes",
    "order": 1,
    "content_type": "text",
    "content": "Variables are containers...",
    "module_id": "your-module-uuid"
  }'
```

---

### Step 5: Create a Quiz

```bash
curl -X POST "http://localhost:8000/api/lecturer/quizzes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Basics Quiz",
    "description": "Test your knowledge",
    "topic_id": "your-topic-uuid",
    "time_limit": 30,
    "passing_score": 70.0,
    "max_attempts": 3,
    "questions": [
      {
        "id": "q1",
        "question": "What is a variable?",
        "type": "multiple_choice",
        "options": [
          {"id": "a", "text": "A container for data"},
          {"id": "b", "text": "A function"}
        ],
        "correct_answer": "a",
        "explanation": "Variables store data",
        "points": 1.0
      }
    ]
  }'
```

---

### Step 6: View Course Analytics

```bash
curl -X GET "http://localhost:8000/api/lecturer/courses/{course_id}/analytics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_enrollments": 45,
    "active_students": 40,
    "completion_rate": 22.5,
    "average_progress": 55.3,
    "struggling_students": [...]
  }
}
```

---

### Step 7: Send Notification to Students

```bash
curl -X POST "http://localhost:8000/api/lecturer/notifications" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "your-course-uuid",
    "recipient_type": "all",
    "title": "Assignment Reminder",
    "message": "Submit your assignment by Friday",
    "type": "announcement"
  }'
```

---

## 👨‍💼 Admin Quick Start

### Step 1: Login as Admin

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your_password"
  }'
```

---

### Step 2: View All Users

```bash
curl -X GET "http://localhost:8000/api/admin/users?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**With Filters:**
```bash
# Search for users
curl -X GET "http://localhost:8000/api/admin/users?search=john&role=student" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Step 3: Create a User

```bash
curl -X POST "http://localhost:8000/api/admin/users" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Smith",
    "email": "jane@example.com",
    "password": "SecurePass123!",
    "role": "lecturer",
    "department": "Computer Science",
    "is_active": true
  }'
```

---

### Step 4: Bulk User Actions

```bash
# Activate multiple users
curl -X POST "http://localhost:8000/api/admin/users/bulk-action" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": ["uuid-1", "uuid-2", "uuid-3"],
    "action": "activate"
  }'
```

**Available Actions:**
- `activate` - Activate users
- `deactivate` - Deactivate users
- `delete` - Delete users
- `update_role` - Change role (include `data: {"role": "lecturer"}`)

---

### Step 5: View System Statistics

```bash
curl -X GET "http://localhost:8000/api/admin/statistics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 1500,
    "total_students": 1200,
    "total_lecturers": 50,
    "active_users": 800,
    "total_courses": 150,
    "active_courses": 120,
    "total_enrollments": 5000
  }
}
```

---

### Step 6: Approve/Reject Courses

```bash
# Approve a course
curl -X PUT "http://localhost:8000/api/admin/courses/{course_id}/approve" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Reject a course
curl -X PUT "http://localhost:8000/api/admin/courses/{course_id}/reject" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Step 7: Create System Announcement

```bash
curl -X POST "http://localhost:8000/api/admin/announcements" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "System Maintenance",
    "content": "The system will be down for maintenance on Saturday",
    "target_audience": "all",
    "priority": "high",
    "expires_at": "2024-01-20T00:00:00Z"
  }'
```

---

### Step 8: Create Department

```bash
curl -X POST "http://localhost:8000/api/admin/departments" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Computer Science",
    "code": "CS",
    "description": "Department of Computer Science",
    "head_of_department": "Dr. John Smith",
    "contact_email": "cs@university.edu"
  }'
```

---

### Step 9: View Audit Logs

```bash
curl -X GET "http://localhost:8000/api/admin/audit-logs?page=1&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**With Filters:**
```bash
# Filter by user and action
curl -X GET "http://localhost:8000/api/admin/audit-logs?user_id=uuid&action=create" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Common Use Cases

### Lecturer: Monitor Struggling Students

```bash
# Get alerts
curl -X GET "http://localhost:8000/api/lecturer/alerts" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Send targeted notification
curl -X POST "http://localhost:8000/api/lecturer/notifications" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": "course-uuid",
    "recipient_type": "struggling",
    "title": "Need Help?",
    "message": "I noticed you might need some assistance...",
    "type": "support"
  }'
```

---

### Admin: Generate Reports

```bash
# System statistics
curl -X GET "http://localhost:8000/api/admin/statistics" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Accessibility report
curl -X GET "http://localhost:8000/api/admin/accessibility-report" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Performance metrics
curl -X GET "http://localhost:8000/api/admin/performance-metrics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔍 Testing with Swagger UI

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_TOKEN`
4. Click "Authorize"
5. Try any endpoint directly in the browser

---

## 📱 Frontend Integration

### React Example - Lecturer Dashboard

```typescript
import { useState, useEffect } from 'react';
import axios from 'axios';

const LecturerDashboard = () => {
  const [courses, setCourses] = useState([]);
  const token = localStorage.getItem('access_token');

  useEffect(() => {
    const fetchCourses = async () => {
      const response = await axios.get(
        'http://localhost:8000/api/lecturer/courses/my',
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      setCourses(response.data.data.courses);
    };
    fetchCourses();
  }, [token]);

  return (
    <div>
      <h1>My Courses</h1>
      {courses.map(course => (
        <div key={course.id}>
          <h2>{course.title}</h2>
          <p>Enrollments: {course.enrollment_count}</p>
        </div>
      ))}
    </div>
  );
};
```

---

### Vue Example - Admin User Management

```vue
<template>
  <div>
    <h1>User Management</h1>
    <input v-model="search" placeholder="Search users..." />
    <table>
      <tr v-for="user in users" :key="user.id">
        <td>{{ user.full_name }}</td>
        <td>{{ user.email }}</td>
        <td>{{ user.role }}</td>
      </tr>
    </table>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import axios from 'axios';

const users = ref([]);
const search = ref('');
const token = localStorage.getItem('access_token');

const fetchUsers = async () => {
  const response = await axios.get(
    'http://localhost:8000/api/admin/users',
    {
      headers: { Authorization: `Bearer ${token}` },
      params: { search: search.value }
    }
  );
  users.value = response.data.data.users;
};

watch(search, fetchUsers);
fetchUsers();
</script>
```

---

## 🎯 Key Endpoints Summary

### Lecturer (20 endpoints)
- Course management (3)
- Module management (4)
- Topic management (4)
- Quiz management (3)
- Student analytics (4)
- Alerts & notifications (2)

### Admin (22 endpoints)
- User management (5)
- Course management (3)
- System analytics (3)
- System health (1)
- Announcements (4)
- Departments (4)
- Audit logs (1)

---

## 📚 Full Documentation

For complete documentation with all request/response examples:

- **Lecturer & Admin:** [docs/API_LECTURER_ADMIN.md](docs/API_LECTURER_ADMIN.md)
- **All Endpoints:** [docs/API_COMPLETE_REFERENCE.md](docs/API_COMPLETE_REFERENCE.md)
- **Quick Reference:** [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)

---

## 🆘 Troubleshooting

### 401 Unauthorized
- Check token is included in Authorization header
- Verify token hasn't expired
- Try logging in again

### 403 Forbidden
- Check user has correct role (lecturer/admin)
- Verify user is active

### 404 Not Found
- Verify endpoint URL is correct
- Check resource ID exists
- Ensure backend is running

---

## 📞 Support

- **Documentation:** [docs/](docs/)
- **API Docs:** http://localhost:8000/docs
- **Email:** support@alia.edu.ng

---

**Ready to build? Start testing with Swagger UI!** 🚀
