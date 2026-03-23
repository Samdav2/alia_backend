# User Management API Documentation

All endpoints require authentication.

---

## 1. Get User Profile

**Endpoint:** `GET /api/users/profile`

**Description:** Get current authenticated user's profile

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "role": "student",
    "department": "Computer Science",
    "student_id": "CS2024001",
    "is_active": true,
    "preferences": {
      "language": "English",
      "accessibility": {
        "bionic_reading": false,
        "dyslexia_font": false,
        "high_contrast": "none",
        "voice_navigation": false
      }
    },
    "disability_info": {
      "has_disability": false,
      "disability_type": [],
      "assistive_technology": [],
      "accommodations_needed": []
    },
    "created_at": "2024-03-15T10:30:00Z",
    "updated_at": "2024-03-15T10:30:00Z",
    "last_login": "2024-03-15T12:00:00Z"
  }
}
```

---

## 2. Update User Profile

**Endpoint:** `PUT /api/users/profile`

**Description:** Update current user's profile

**Request Body:**
```json
{
  "full_name": "John Michael Doe",
  "department": "Software Engineering",
  "preferences": {
    "language": "English",
    "accessibility": {
      "bionic_reading": true,
      "dyslexia_font": true,
      "high_contrast": "dark",
      "voice_navigation": true
    }
  },
  "disability_info": {
    "has_disability": true,
    "disability_type": ["visual", "dyslexia"],
    "assistive_technology": ["screen_reader", "text_to_speech"],
    "accommodations_needed": ["extended_time", "audio_content"]
  }
}
```

**Field Descriptions:**
- `full_name` (string, optional): Updated full name
- `department` (string, optional): Updated department
- `preferences` (object, optional): User preferences
  - `language`: "English", "Igbo", "Hausa", "Yoruba"
  - `accessibility`: Accessibility settings
- `disability_info` (object, optional): Disability information

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Michael Doe",
    "email": "john.doe@example.com",
    "role": "student",
    "department": "Software Engineering",
    "student_id": "CS2024001",
    "is_active": true,
    "preferences": {
      "language": "English",
      "accessibility": {
        "bionic_reading": true,
        "dyslexia_font": true,
        "high_contrast": "dark",
        "voice_navigation": true
      }
    },
    "disability_info": {
      "has_disability": true,
      "disability_type": ["visual", "dyslexia"],
      "assistive_technology": ["screen_reader", "text_to_speech"],
      "accommodations_needed": ["extended_time", "audio_content"]
    },
    "created_at": "2024-03-15T10:30:00Z",
    "updated_at": "2024-03-15T14:30:00Z",
    "last_login": "2024-03-15T12:00:00Z"
  }
}
```

---

## 3. Get All Users (Admin Only)

**Endpoint:** `GET /api/users`

**Description:** Get paginated list of all users

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `limit` (integer, optional): Items per page (default: 20, max: 100)
- `role` (string, optional): Filter by role ("student", "lecturer", "admin")
- `department` (string, optional): Filter by department

**Example Request:**
```
GET /api/users?page=1&limit=20&role=student&department=Computer%20Science
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "role": "student",
        "department": "Computer Science",
        "is_active": true,
        "created_at": "2024-03-15T10:30:00Z"
      },
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "full_name": "Jane Smith",
        "email": "jane.smith@example.com",
        "role": "student",
        "department": "Computer Science",
        "is_active": true,
        "created_at": "2024-03-14T09:20:00Z"
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

## 4. Deactivate User (Admin Only)

**Endpoint:** `PUT /api/users/{user_id}/deactivate`

**Description:** Deactivate a user account

**Path Parameters:**
- `user_id` (UUID): User ID to deactivate

**Success Response (200):**
```json
{
  "success": true,
  "message": "User deactivated successfully"
}
```

---

## 5. Activate User (Admin Only)

**Endpoint:** `PUT /api/users/{user_id}/activate`

**Description:** Activate a user account

**Path Parameters:**
- `user_id` (UUID): User ID to activate

**Success Response (200):**
```json
{
  "success": true,
  "message": "User activated successfully"
}
```

---

## Error Responses

**401 Unauthorized:**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Could not validate credentials",
    "details": null
  }
}
```

**403 Forbidden:**
```json
{
  "success": false,
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions",
    "details": null
  }
}
```

**404 Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found",
    "details": null
  }
}
```