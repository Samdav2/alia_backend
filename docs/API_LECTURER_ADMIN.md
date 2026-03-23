# ALIA Platform - Lecturer & Admin API Documentation

Complete API reference for lecturer and administrator endpoints.

## Table of Contents

### Lecturer Endpoints
1. [Course Management](#lecturer-course-management)
2. [Module Management](#lecturer-module-management)
3. [Topic Management](#lecturer-topic-management)
4. [Quiz Management](#lecturer-quiz-management)
5. [Student Analytics](#lecturer-student-analytics)
6. [Alerts & Notifications](#lecturer-alerts-notifications)

### Admin Endpoints
1. [User Management](#admin-user-management)
2. [Course Management](#admin-course-management)
3. [System Analytics](#admin-system-analytics)
4. [System Health](#admin-system-health)
5. [Announcements](#admin-announcements)
6. [Departments](#admin-departments)
7. [Audit Logs](#admin-audit-logs)

---

## Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

**Role Requirements:**
- Lecturer endpoints: `lecturer` or `admin` role
- Admin endpoints: `admin` role only

---

# LECTURER ENDPOINTS

## Lecturer Course Management

### 1. Get My Courses

Get all courses created by the authenticated lecturer.

**Endpoint:** `GET /api/lecturer/courses/my`

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20, max: 100)
- `status` (string, optional): Filter by status (`active`, `draft`)

**Response:**
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "id": "uuid",
        "code": "CS101",
        "title": "Introduction to Programming",
        "department": "Computer Science",
        "level": "beginner",
        "is_active": true,
        "enrollment_count": 45,
        "created_at": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 5,
      "total_pages": 1
    }
  }
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/api/lecturer/courses/my?page=1&limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. Publish Course

Publish a course to make it visible to students.

**Endpoint:** `PUT /api/lecturer/courses/{course_id}/publish`

**Response:**
```json
{
  "success": true,
  "message": "Course published successfully"
}
```

**cURL Example:**
```bash
curl -X PUT "http://localhost:8000/api/lecturer/courses/{course_id}/publish" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. Unpublish Course

Unpublish a course to hide it from students.

**Endpoint:** `PUT /api/lecturer/courses/{course_id}/unpublish`

**Response:**
```json
{
  "success": true,
  "message": "Course unpublished successfully"
}
```

---

## Lecturer Module Management

### 4. Create Module

Create a new module in a course.

**Endpoint:** `POST /api/lecturer/courses/{course_id}/modules`

**Request Body:**
```json
{
  "title": "Introduction to Variables",
  "description": "Learn about variables and data types",
  "order": 1,
  "course_id": "course-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "module-uuid",
    "title": "Introduction to Variables",
    "description": "Learn about variables and data types",
    "order": 1,
    "course_id": "course-uuid",
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

---

### 5. Update Module

Update an existing module.

**Endpoint:** `PUT /api/lecturer/courses/modules/{module_id}`

**Request Body:**
```json
{
  "title": "Updated Module Title",
  "description": "Updated description",
  "order": 2
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "module-uuid",
    "title": "Updated Module Title",
    "description": "Updated description",
    "order": 2,
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

---

### 6. Delete Module

Delete a module from a course.

**Endpoint:** `DELETE /api/lecturer/courses/modules/{module_id}`

**Response:**
```json
{
  "success": true,
  "message": "Module deleted successfully"
}
```

---

### 7. Reorder Modules

Reorder modules within a course.

**Endpoint:** `PUT /api/lecturer/courses/{course_id}/modules/reorder`

**Request Body:**
```json
{
  "module_orders": [
    {"module_id": "uuid-1", "order": 1},
    {"module_id": "uuid-2", "order": 2},
    {"module_id": "uuid-3", "order": 3}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Modules reordered successfully"
}
```

---

## Lecturer Topic Management

### 8. Create Topic

Create a new topic in a module.

**Endpoint:** `POST /api/lecturer/courses/modules/{module_id}/topics`

**Request Body:**
```json
{
  "title": "What are Variables?",
  "description": "Introduction to variables",
  "duration": "30 minutes",
  "order": 1,
  "content_type": "text",
  "content": "Variables are containers for storing data...",
  "media_files": [],
  "prerequisites": [],
  "learning_objectives": ["Understand variables", "Declare variables"],
  "module_id": "module-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "topic-uuid",
    "title": "What are Variables?",
    "order": 1,
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

---

### 9. Update Topic

Update an existing topic.

**Endpoint:** `PUT /api/lecturer/courses/topics/{topic_id}`

**Request Body:**
```json
{
  "title": "Updated Topic Title",
  "content": "Updated content..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "topic-uuid",
    "title": "Updated Topic Title",
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

---

### 10. Delete Topic

Delete a topic from a module.

**Endpoint:** `DELETE /api/lecturer/courses/topics/{topic_id}`

**Response:**
```json
{
  "success": true,
  "message": "Topic deleted successfully"
}
```

---

### 11. Reorder Topics

Reorder topics within a module.

**Endpoint:** `PUT /api/lecturer/courses/modules/{module_id}/topics/reorder`

**Request Body:**
```json
{
  "topic_orders": [
    {"topic_id": "uuid-1", "order": 1},
    {"topic_id": "uuid-2", "order": 2}
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Topics reordered successfully"
}
```

---

## Lecturer Quiz Management

### 12. Create Quiz

Create a new quiz for a topic.

**Endpoint:** `POST /api/lecturer/quizzes`

**Request Body:**
```json
{
  "title": "Variables Quiz",
  "description": "Test your knowledge of variables",
  "topic_id": "topic-uuid",
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
        {"id": "b", "text": "A function"},
        {"id": "c", "text": "A loop"}
      ],
      "correct_answer": "a",
      "explanation": "Variables store data values",
      "points": 1.0
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "quiz-uuid",
    "title": "Variables Quiz",
    "topic_id": "topic-uuid",
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

---

### 13. Update Quiz

Update an existing quiz.

**Endpoint:** `PUT /api/lecturer/quizzes/{quiz_id}`

**Request Body:**
```json
{
  "title": "Updated Quiz Title",
  "passing_score": 75.0,
  "is_active": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "quiz-uuid",
    "title": "Updated Quiz Title",
    "passing_score": 75.0,
    "updated_at": "2024-01-15T11:00:00Z"
  }
}
```

---

### 14. Delete Quiz

Delete a quiz.

**Endpoint:** `DELETE /api/lecturer/quizzes/{quiz_id}`

**Response:**
```json
{
  "success": true,
  "message": "Quiz deleted successfully"
}
```

---

## Lecturer Student Analytics

### 15. Get Course Enrollments

Get all students enrolled in a course.

**Endpoint:** `GET /api/lecturer/courses/{course_id}/enrollments`

**Query Parameters:**
- `page` (integer, optional): Page number
- `limit` (integer, optional): Items per page
- `status` (string, optional): Filter by status

**Response:**
```json
{
  "success": true,
  "data": {
    "enrollments": [
      {
        "id": "enrollment-uuid",
        "user": {
          "id": "user-uuid",
          "full_name": "John Doe",
          "email": "john@example.com"
        },
        "enrolled_at": "2024-01-10T10:00:00Z",
        "progress_percentage": 45.5,
        "status": "active"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45,
      "total_pages": 3
    }
  }
}
```

---

### 16. Get Course Analytics

Get detailed analytics for a course.

**Endpoint:** `GET /api/lecturer/courses/{course_id}/analytics`

**Response:**
```json
{
  "success": true,
  "data": {
    "total_enrollments": 45,
    "active_students": 40,
    "completion_rate": 22.5,
    "average_progress": 55.3,
    "average_quiz_score": 78.0,
    "struggling_students": [
      {
        "user_id": "uuid",
        "full_name": "Jane Smith",
        "progress": 15.0,
        "average_score": 45.0
      }
    ]
  }
}
```

---

### 17. Get Student Progress

Get specific student's progress in a course.

**Endpoint:** `GET /api/lecturer/courses/{course_id}/students/{student_id}/progress`

**Response:**
```json
{
  "success": true,
  "data": {
    "student": {
      "id": "user-uuid",
      "full_name": "John Doe",
      "email": "john@example.com"
    },
    "enrollment": {
      "enrolled_at": "2024-01-10T10:00:00Z",
      "status": "active"
    },
    "topic_progress": [
      {
        "topic_id": "topic-uuid",
        "status": "completed",
        "time_spent": 1800,
        "completed_at": "2024-01-12T15:30:00Z"
      }
    ]
  }
}
```

---

### 18. Get Class Demographics

Get demographics of all students in lecturer's courses.

**Endpoint:** `GET /api/lecturer/class-demographics`

**Response:**
```json
{
  "success": true,
  "data": {
    "total_students": 120,
    "by_department": [
      {"department": "Computer Science", "count": 45},
      {"department": "Engineering", "count": 35}
    ],
    "by_disability": [
      {"type": "visual", "count": 8},
      {"type": "hearing", "count": 5}
    ]
  }
}
```

---

## Lecturer Alerts & Notifications

### 19. Get Lecturer Alerts

Get alerts about students needing attention.

**Endpoint:** `GET /api/lecturer/alerts`

**Response:**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "id": "alert-uuid",
        "type": "struggling_student",
        "severity": "high",
        "student": {
          "id": "user-uuid",
          "full_name": "Jane Smith"
        },
        "course": {
          "id": "course-uuid",
          "title": "Introduction to Programming"
        },
        "message": "Student has not accessed course in 7 days",
        "created_at": "2024-01-15T10:00:00Z"
      }
    ]
  }
}
```

---

### 20. Send Notification to Students

Send notification to students in a course.

**Endpoint:** `POST /api/lecturer/notifications`

**Request Body:**
```json
{
  "course_id": "course-uuid",
  "recipient_type": "all",
  "student_ids": [],
  "title": "Assignment Reminder",
  "message": "Don't forget to submit your assignment by Friday",
  "type": "announcement"
}
```

**Recipient Types:**
- `all`: All enrolled students
- `specific`: Specific students (provide student_ids)
- `struggling`: Students with progress < 30%

**Response:**
```json
{
  "success": true,
  "message": "Notifications sent successfully"
}
```

---

# ADMIN ENDPOINTS

## Admin User Management

### 21. Get All Users

Get all users with filters.

**Endpoint:** `GET /api/admin/users`

**Query Parameters:**
- `page` (integer, optional): Page number
- `limit` (integer, optional): Items per page
- `role` (string, optional): Filter by role (`student`, `lecturer`, `admin`)
- `search` (string, optional): Search by name, email, or student ID
- `is_active` (boolean, optional): Filter by active status

**Response:**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": "user-uuid",
        "full_name": "John Doe",
        "email": "john@example.com",
        "role": "student",
        "department": "Computer Science",
        "is_active": true,
        "created_at": "2024-01-10T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 500,
      "total_pages": 25
    }
  }
}
```

---

### 22. Create User

Create a new user.

**Endpoint:** `POST /api/admin/users`

**Request Body:**
```json
{
  "full_name": "Jane Smith",
  "email": "jane@example.com",
  "password": "SecurePass123!",
  "role": "student",
  "department": "Computer Science",
  "student_id": "CS2024001",
  "is_active": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user-uuid",
    "full_name": "Jane Smith",
    "email": "jane@example.com",
    "role": "student"
  },
  "message": "User created successfully"
}
```

---

### 23. Update User

Update an existing user.

**Endpoint:** `PUT /api/admin/users/{user_id}`

**Request Body:**
```json
{
  "full_name": "Jane Smith Updated",
  "department": "Engineering",
  "is_active": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user-uuid",
    "full_name": "Jane Smith Updated",
    "department": "Engineering"
  },
  "message": "User updated successfully"
}
```

---

### 24. Delete User

Delete a user.

**Endpoint:** `DELETE /api/admin/users/{user_id}`

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

### 25. Bulk User Action

Perform bulk action on multiple users.

**Endpoint:** `POST /api/admin/users/bulk-action`

**Request Body:**
```json
{
  "user_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "action": "activate",
  "data": {}
}
```

**Actions:**
- `activate`: Activate users
- `deactivate`: Deactivate users
- `delete`: Delete users
- `update_role`: Update role (provide `data: {"role": "lecturer"}`)

**Response:**
```json
{
  "success": true,
  "message": "Bulk action 'activate' completed successfully"
}
```

---

## Admin Course Management

### 26. Get All Courses (Admin View)

Get all courses with admin view.

**Endpoint:** `GET /api/admin/courses`

**Query Parameters:**
- `page`, `limit`: Pagination
- `status` (string, optional): Filter by status (`active`, `inactive`)
- `department` (string, optional): Filter by department

**Response:**
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "id": "course-uuid",
        "code": "CS101",
        "title": "Introduction to Programming",
        "department": "Computer Science",
        "instructor": {
          "id": "user-uuid",
          "full_name": "Dr. Smith"
        },
        "enrollment_count": 45,
        "is_active": true,
        "created_at": "2024-01-10T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "total_pages": 8
    }
  }
}
```

---

### 27. Approve Course

Approve a course for publication.

**Endpoint:** `PUT /api/admin/courses/{course_id}/approve`

**Response:**
```json
{
  "success": true,
  "message": "Course approved successfully"
}
```

---

### 28. Reject Course

Reject a course.

**Endpoint:** `PUT /api/admin/courses/{course_id}/reject`

**Response:**
```json
{
  "success": true,
  "message": "Course rejected successfully"
}
```

---

### 29. Feature Course

Feature or unfeature a course.

**Endpoint:** `PUT /api/admin/courses/{course_id}/feature`

**Request Body:**
```json
{
  "featured": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Course featured status updated successfully"
}
```

---

## Admin System Analytics

### 30. Get System Statistics

Get system-wide statistics.

**Endpoint:** `GET /api/admin/statistics`

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

### 31. Get Accessibility Report

Get system-wide accessibility report.

**Endpoint:** `GET /api/admin/accessibility-report`

**Response:**
```json
{
  "success": true,
  "data": {
    "users_with_disabilities": 120,
    "total_users": 1500,
    "feature_usage": [
      {"feature": "bionic_reading", "count": 450},
      {"feature": "high_contrast", "count": 320}
    ]
  }
}
```

---

### 32. Get Performance Metrics

Get system performance metrics.

**Endpoint:** `GET /api/admin/performance-metrics`

**Response:**
```json
{
  "success": true,
  "data": {
    "completion_rate": 68.5,
    "average_completion_time": "8 weeks",
    "total_enrollments": 5000,
    "completed_enrollments": 3425
  }
}
```

---

## Admin System Health

### 33. Get System Health

Get system health status.

**Endpoint:** `GET /api/admin/system-health`

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "healthy",
    "timestamp": "2024-01-15T10:00:00Z"
  }
}
```

---

## Admin Announcements

### 34. Create Announcement

Create a new system announcement.

**Endpoint:** `POST /api/admin/announcements`

**Request Body:**
```json
{
  "title": "System Maintenance",
  "content": "The system will be down for maintenance on Saturday",
  "target_audience": "all",
  "priority": "high",
  "expires_at": "2024-01-20T00:00:00Z"
}
```

**Target Audiences:**
- `all`: All users
- `students`: Students only
- `lecturers`: Lecturers only
- `department`: Specific department

**Priorities:**
- `low`, `normal`, `high`, `urgent`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "announcement-uuid",
    "title": "System Maintenance",
    "priority": "high",
    "created_at": "2024-01-15T10:00:00Z"
  },
  "message": "Announcement created successfully"
}
```

---

### 35. Get All Announcements

Get all announcements.

**Endpoint:** `GET /api/admin/announcements`

**Query Parameters:**
- `page`, `limit`: Pagination
- `is_active` (boolean, optional): Filter by active status

**Response:**
```json
{
  "success": true,
  "data": {
    "announcements": [
      {
        "id": "announcement-uuid",
        "title": "System Maintenance",
        "content": "The system will be down...",
        "priority": "high",
        "is_active": true,
        "created_at": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 10,
      "total_pages": 1
    }
  }
}
```

---

### 36. Update Announcement

Update an announcement.

**Endpoint:** `PUT /api/admin/announcements/{announcement_id}`

**Request Body:**
```json
{
  "title": "Updated Title",
  "is_active": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "announcement-uuid",
    "title": "Updated Title",
    "updated_at": "2024-01-15T11:00:00Z"
  },
  "message": "Announcement updated successfully"
}
```

---

### 37. Delete Announcement

Delete an announcement.

**Endpoint:** `DELETE /api/admin/announcements/{announcement_id}`

**Response:**
```json
{
  "success": true,
  "message": "Announcement deleted successfully"
}
```

---

## Admin Departments

### 38. Get All Departments

Get all departments.

**Endpoint:** `GET /api/admin/departments`

**Response:**
```json
{
  "success": true,
  "data": {
    "departments": [
      {
        "id": "dept-uuid",
        "name": "Computer Science",
        "code": "CS",
        "head_of_department": "Dr. John Smith",
        "contact_email": "cs@university.edu",
        "student_count": 450,
        "course_count": 25,
        "is_active": true
      }
    ]
  }
}
```

---

### 39. Create Department

Create a new department.

**Endpoint:** `POST /api/admin/departments`

**Request Body:**
```json
{
  "name": "Data Science",
  "code": "DS",
  "description": "Department of Data Science",
  "head_of_department": "Dr. Jane Doe",
  "contact_email": "ds@university.edu"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "dept-uuid",
    "name": "Data Science",
    "code": "DS"
  },
  "message": "Department created successfully"
}
```

---

### 40. Update Department

Update a department.

**Endpoint:** `PUT /api/admin/departments/{department_id}`

**Request Body:**
```json
{
  "head_of_department": "Dr. New Head",
  "contact_email": "newemail@university.edu"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "dept-uuid",
    "head_of_department": "Dr. New Head"
  },
  "message": "Department updated successfully"
}
```

---

### 41. Delete Department

Delete a department.

**Endpoint:** `DELETE /api/admin/departments/{department_id}`

**Response:**
```json
{
  "success": true,
  "message": "Department deleted successfully"
}
```

---

## Admin Audit Logs

### 42. Get Audit Logs

Get system audit logs.

**Endpoint:** `GET /api/admin/audit-logs`

**Query Parameters:**
- `page`, `limit`: Pagination
- `user_id` (string, optional): Filter by user
- `action` (string, optional): Filter by action (`create`, `update`, `delete`, `login`)
- `resource_type` (string, optional): Filter by resource type (`user`, `course`, `enrollment`)

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": "log-uuid",
        "user_id": "user-uuid",
        "action": "create",
        "resource_type": "course",
        "resource_id": "course-uuid",
        "details": {"title": "New Course"},
        "ip_address": "192.168.1.1",
        "created_at": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 1000,
      "total_pages": 20
    }
  }
}
```

---

## Error Responses

All endpoints may return the following error responses:

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden:**
```json
{
  "detail": "Insufficient permissions"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Frontend Integration Examples

### React/TypeScript Hook for Lecturer

```typescript
// hooks/useLecturerCourses.ts
import { useState, useEffect } from 'react';
import axios from 'axios';

export const useLecturerCourses = (token: string) => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const response = await axios.get(
          'http://localhost:8000/api/lecturer/courses/my',
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
        setCourses(response.data.data.courses);
      } catch (error) {
        console.error('Error fetching courses:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [token]);

  return { courses, loading };
};
```

### Vue.js Composable for Admin

```javascript
// composables/useAdminUsers.js
import { ref } from 'vue';
import axios from 'axios';

export function useAdminUsers() {
  const users = ref([]);
  const loading = ref(false);

  const fetchUsers = async (token, filters = {}) => {
    loading.value = true;
    try {
      const response = await axios.get(
        'http://localhost:8000/api/admin/users',
        {
          headers: { Authorization: `Bearer ${token}` },
          params: filters
        }
      );
      users.value = response.data.data.users;
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      loading.value = false;
    }
  };

  return { users, loading, fetchUsers };
}
```

---

## Rate Limiting

All endpoints are subject to rate limiting:
- 100 requests per minute per user
- 429 Too Many Requests response when exceeded

---

## Best Practices

1. **Always handle errors gracefully** in your frontend
2. **Cache responses** when appropriate to reduce API calls
3. **Use pagination** for large datasets
4. **Implement retry logic** for failed requests
5. **Validate data** on the frontend before sending to API
6. **Use optimistic updates** for better UX
7. **Monitor API performance** and adjust as needed

---

## Support

For API support, contact: support@alia.edu.ng

Documentation Version: 1.0.0
Last Updated: January 2024
