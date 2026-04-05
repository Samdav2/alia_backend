# Course Management API Documentation

---

## 1. Get All Courses

**Endpoint:** `GET /api/courses`

**Description:** Get paginated list of courses

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20)
- `department` (string, optional): Filter by department
- `level` (string, optional): Filter by level ("beginner", "intermediate", "advanced")
- `search` (string, optional): Search in title, description, code

**Example Request:**
```
GET /api/courses?page=1&limit=10&department=Computer%20Science&level=beginner&search=python
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "id": "770e8400-e29b-41d4-a716-446655440000",
        "code": "CS101",
        "title": "Introduction to Python Programming",
        "description": "Learn Python from scratch",
        "instructor": "Dr. Jane Smith",
        "department": "Computer Science",
        "level": "beginner",
        "duration": "12 weeks",
        "enrollment_count": 150,
        "rating": 4.5,
        "tags": ["python", "programming", "beginner"],
        "thumbnail": "https://example.com/thumbnails/cs101.jpg",
        "is_active": true,
        "created_at": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 45,
      "total_pages": 5
    }
  }
}
```

---

## 2. Get Course Details

**Endpoint:** `GET /api/courses/{course_id}`

**Description:** Get detailed course information including modules and topics

**Path Parameters:**
- `course_id` (UUID): Course ID

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "code": "CS101",
    "title": "Introduction to Python Programming",
    "description": "Comprehensive Python course for beginners",
    "instructor_id": "550e8400-e29b-41d4-a716-446655440000",
    "department": "Computer Science",
    "level": "beginner",
    "duration": "12 weeks",
    "tags": ["python", "programming", "beginner"],
    "thumbnail": "https://example.com/thumbnails/cs101.jpg",
    "modules": [
      {
        "id": "880e8400-e29b-41d4-a716-446655440000",
        "title": "Getting Started with Python",
        "description": "Introduction to Python basics",
        "order": 1,
        "course_id": "770e8400-e29b-41d4-a716-446655440000",
        "topics": [
          {
            "id": "990e8400-e29b-41d4-a716-446655440000",
            "title": "Installing Python",
            "description": "How to install Python on your system",
            "duration": "30 minutes",
            "order": 1,
            "content_type": "video",
            "content": "Video content or text content here...",
            "media_files": [
              {
                "type": "video",
                "url": "https://example.com/videos/install-python.mp4",
                "title": "Python Installation Guide",
                "description": "Step by step installation",
                "alt_text": "Python installation video"
              }
            ],
            "prerequisites": [],
            "learning_objectives": [
              "Install Python on Windows, Mac, or Linux",
              "Verify Python installation",
              "Set up development environment"
            ],
            "assessments": [
              {
                "id": "aa0e8400-e29b-41d4-a716-446655440000",
                "type": "quiz",
                "title": "Installation Quiz",
                "questions": [
                  {
                    "id": "bb0e8400-e29b-41d4-a716-446655440000",
                    "question": "What command checks Python version?",
                    "type": "multiple_choice",
                    "options": [
                      "python --version",
                      "python -v",
                      "check python",
                      "python version"
                    ],
                    "correct_answer": "python --version",
                    "explanation": "The --version flag displays the installed Python version"
                  }
                ]
              }
            ],
            "module_id": "880e8400-e29b-41d4-a716-446655440000",
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z"
          }
        ],
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z"
      }
    ],
    "enrollment_count": 150,
    "rating": 4.5,
        "is_active": true,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-02-01T14:30:00Z"
      }
    ],
    "enrollment_count": 150,
    "rating": 4.5,
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-02-01T14:30:00Z"
  }
}
```

### Scheduled Content (Locked Example)
If a module or topic is scheduled for the future, the response will include `is_locked: true` and redacted content for students:

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440000",
  "title": "Advanced Topics",
  "available_at": "2026-12-01T10:00:00Z",
  "is_locked": true,
  "availability_message": "Available on 2026-12-01 10:00:00",
  "topics": [] // Topics are hidden if module is locked
}
```

---

## 3. Create Course (Lecturer/Admin Only)

**Endpoint:** `POST /api/courses`

**Description:** Create a new course

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "code": "CS102",
  "title": "Advanced Python Programming",
  "description": "Deep dive into Python advanced concepts",
  "department": "Computer Science",
  "level": "intermediate",
  "duration": "10 weeks",
  "tags": ["python", "advanced", "oop"],
  "thumbnail": "https://example.com/thumbnails/cs102.jpg"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "cc0e8400-e29b-41d4-a716-446655440000",
    "code": "CS102",
    "title": "Advanced Python Programming",
    "description": "Deep dive into Python advanced concepts",
    "instructor_id": "550e8400-e29b-41d4-a716-446655440000",
    "department": "Computer Science",
    "level": "intermediate",
    "duration": "10 weeks",
    "tags": ["python", "advanced", "oop"],
    "thumbnail": "https://example.com/thumbnails/cs102.jpg",
    "modules": [],
    "enrollment_count": 0,
    "rating": 0.0,
    "is_active": true,
    "created_at": "2024-03-15T14:30:00Z",
    "updated_at": "2024-03-15T14:30:00Z"
  }
}
```

---

## 4. Update Course (Lecturer/Admin Only)

**Endpoint:** `PUT /api/courses/{course_id}`

**Description:** Update course information

**Request Body:**
```json
{
  "title": "Advanced Python Programming - Updated",
  "description": "Updated description",
  "level": "advanced",
  "duration": "12 weeks",
  "tags": ["python", "advanced", "oop", "design-patterns"],
  "thumbnail": "https://example.com/thumbnails/cs102-new.jpg"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "cc0e8400-e29b-41d4-a716-446655440000",
    "code": "CS102",
    "title": "Advanced Python Programming - Updated",
    "description": "Updated description",
    "instructor_id": "550e8400-e29b-41d4-a716-446655440000",
    "department": "Computer Science",
    "level": "advanced",
    "duration": "12 weeks",
    "tags": ["python", "advanced", "oop", "design-patterns"],
    "thumbnail": "https://example.com/thumbnails/cs102-new.jpg",
    "modules": [],
    "enrollment_count": 0,
    "rating": 0.0,
    "is_active": true,
    "created_at": "2024-03-15T14:30:00Z",
    "updated_at": "2024-03-15T15:00:00Z"
  }
}
```

---

## 5. Delete Course (Admin Only)

**Endpoint:** `DELETE /api/courses/{course_id}`

**Description:** Soft delete a course (sets is_active to false)

**Success Response (200):**
```json
{
  "success": true,
  "message": "Course deleted successfully"
}
```

---

## 6. Get Course Modules

**Endpoint:** `GET /api/courses/{course_id}/modules`

**Description:** Get all modules for a course

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "modules": [
      {
        "id": "880e8400-e29b-41d4-a716-446655440000",
        "title": "Getting Started",
        "description": "Introduction module",
        "order": 1,
        "available_at": "2024-01-15T10:00:00Z",
        "is_locked": false,
        "course_id": "770e8400-e29b-41d4-a716-446655440000",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z"
      }
    ]
  }
}
```

---

## 7. Get Module Topics

**Endpoint:** `GET /api/courses/{course_id}/modules/{module_id}/topics`

**Description:** Get all topics in a module

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "topics": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440000",
        "title": "Installing Python",
        "description": "Installation guide",
        "duration": "30 minutes",
        "order": 1,
        "available_at": "2024-01-15T10:00:00Z",
        "is_locked": false,
        "content_type": "video",
        "module_id": "880e8400-e29b-41d4-a716-446655440000"
      }
    ]
  }
}
```

---

## 8. Get Topic Details

**Endpoint:** `GET /api/courses/{course_id}/topics/{topic_id}`

**Description:** Get detailed topic content

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "990e8400-e29b-41d4-a716-446655440000",
    "title": "Installing Python",
    "description": "Complete installation guide",
    "duration": "30 minutes",
    "available_at": "2024-01-15T10:00:00Z",
    "is_locked": false,
    "availability_message": "Available on 2024-01-15 10:00:00",
    "content": "Detailed content here...",
    "media_files": [],
    "assessments": [],
    "prerequisites": [],
    "learning_objectives": []
  }
}
```

---

## 9. Content Availability Rules

1. **Scheduled Release**: Both `Modules` and `Topics` can have an `available_at` timestamp.
2. **Locking**: If the current time is before `available_at`, the content is considered "locked" for students.
3. **Redaction**:
   - Locked Modules: No topics are returned in the list.
   - Locked Topics: Content is replaced with a "Locked" message, and media files are empty.
4. **Staff Access**: Lecturers and Admins always bypass locking logic and see full content.
