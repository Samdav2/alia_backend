# Enrollment Management API Documentation

---

## 1. Get User Enrollments

**Endpoint:** `GET /api/enrollments`

**Description:** Get all courses the current user is enrolled in

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "enrollments": [
      {
        "id": "dd0e8400-e29b-41d4-a716-446655440000",
        "course_id": "770e8400-e29b-41d4-a716-446655440000",
        "course": {
          "id": "770e8400-e29b-41d4-a716-446655440000",
          "code": "CS101",
          "title": "Introduction to Python Programming",
          "instructor": "Dr. Jane Smith",
          "department": "Computer Science",
          "level": "beginner",
          "duration": "12 weeks",
          "enrollment_count": 150,
          "rating": 4.5,
          "tags": ["python", "programming"],
          "thumbnail": "https://example.com/thumbnails/cs101.jpg",
          "is_active": true,
          "created_at": "2024-01-15T10:00:00Z"
        },
        "enrollment_date": "2024-03-01T09:00:00Z",
        "status": "active",
        "completion_date": null,
        "progress": {
          "completed_topics": 5,
          "total_topics": 20,
          "completion_percentage": 25.0,
          "time_spent": 180,
          "last_accessed_at": "2024-03-15T14:30:00Z"
        }
      },
      {
        "id": "ee0e8400-e29b-41d4-a716-446655440000",
        "course_id": "880e8400-e29b-41d4-a716-446655440000",
        "course": {
          "id": "880e8400-e29b-41d4-a716-446655440000",
          "code": "CS201",
          "title": "Data Structures and Algorithms",
          "instructor": "Prof. John Smith",
          "department": "Computer Science",
          "level": "intermediate",
          "duration": "14 weeks",
          "enrollment_count": 120,
          "rating": 4.7,
          "tags": ["algorithms", "data-structures"],
          "thumbnail": "https://example.com/thumbnails/cs201.jpg",
          "is_active": true,
          "created_at": "2024-01-20T10:00:00Z"
        },
        "enrollment_date": "2024-02-15T10:00:00Z",
        "status": "completed",
        "completion_date": "2024-03-10T16:00:00Z",
        "progress": {
          "completed_topics": 30,
          "total_topics": 30,
          "completion_percentage": 100.0,
          "time_spent": 420,
          "last_accessed_at": "2024-03-10T16:00:00Z"
        }
      }
    ]
  }
}
```

**Enrollment Status Values:**
- `active`: Currently enrolled and in progress
- `completed`: Course completed
- `dropped`: User dropped the course

---

## 2. Enroll in Course

**Endpoint:** `POST /api/enrollments`

**Description:** Enroll current user in a course

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "course_id": "770e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "ff0e8400-e29b-41d4-a716-446655440000",
    "course_id": "770e8400-e29b-41d4-a716-446655440000",
    "course": {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "code": "CS101",
      "title": "Introduction to Python Programming",
      "instructor": "Dr. Jane Smith",
      "department": "Computer Science",
      "level": "beginner",
      "duration": "12 weeks",
      "enrollment_count": 151,
      "rating": 4.5,
      "tags": ["python", "programming"],
      "thumbnail": "https://example.com/thumbnails/cs101.jpg",
      "is_active": true,
      "created_at": "2024-01-15T10:00:00Z"
    },
    "enrollment_date": "2024-03-15T15:00:00Z",
    "status": "active",
    "completion_date": null
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Already enrolled in this course",
    "details": null
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Course not found",
    "details": null
  }
}
```

---

## 3. Unenroll from Course

**Endpoint:** `DELETE /api/enrollments/{course_id}`

**Description:** Unenroll current user from a course

**Path Parameters:**
- `course_id` (UUID): Course ID to unenroll from

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Successfully unenrolled from course"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Enrollment not found",
    "details": null
  }
}
```

---

## Frontend Implementation Examples

### React/TypeScript Example

```typescript
// Enrollment Service
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

interface EnrollmentData {
  course_id: string;
}

export const enrollmentService = {
  // Get user enrollments
  getEnrollments: async (token: string) => {
    const response = await axios.get(`${API_BASE_URL}/api/enrollments`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  },

  // Enroll in course
  enrollInCourse: async (token: string, courseId: string) => {
    const response = await axios.post(
      `${API_BASE_URL}/api/enrollments`,
      { course_id: courseId },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    return response.data;
  },

  // Unenroll from course
  unenrollFromCourse: async (token: string, courseId: string) => {
    const response = await axios.delete(
      `${API_BASE_URL}/api/enrollments/${courseId}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    return response.data;
  }
};
```

### Vue.js Example

```javascript
// composables/useEnrollments.js
import { ref } from 'vue';
import axios from 'axios';

export function useEnrollments() {
  const enrollments = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const fetchEnrollments = async (token) => {
    loading.value = true;
    try {
      const response = await axios.get('/api/enrollments', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      enrollments.value = response.data.data.enrollments;
    } catch (err) {
      error.value = err.response?.data?.error?.message || 'Failed to fetch enrollments';
    } finally {
      loading.value = false;
    }
  };

  const enrollInCourse = async (token, courseId) => {
    loading.value = true;
    try {
      const response = await axios.post(
        '/api/enrollments',
        { course_id: courseId },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      return response.data;
    } catch (err) {
      error.value = err.response?.data?.error?.message || 'Failed to enroll';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    enrollments,
    loading,
    error,
    fetchEnrollments,
    enrollInCourse
  };
}
```