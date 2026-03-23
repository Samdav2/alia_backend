# Authentication API Documentation

Base URL: `http://localhost:8000`

## Overview
All authentication endpoints are public and don't require authentication tokens.

---

## 1. Register User

**Endpoint:** `POST /api/auth/register`

**Description:** Create a new user account

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "password": "SecurePassword123!",
  "role": "student",
  "department": "Computer Science",
  "student_id": "CS2024001"
}
```

**Field Descriptions:**
- `full_name` (string, required): User's full name
- `email` (string, required): Valid email address (must be unique)
- `password` (string, required): Password (min 8 characters recommended)
- `role` (string, required): User role - "student", "lecturer", or "admin"
- `department` (string, required): Department name
- `student_id` (string, optional): Student ID (only for students)

**Success Response (201):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "role": "student",
      "department": "Computer Science"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email already registered",
    "details": null
  }
}
```

---

## 2. Login

**Endpoint:** `POST /api/auth/login`

**Description:** Authenticate user and get access tokens

**Request Body:**
```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123!"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "role": "student"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error Response (401):**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Incorrect email or password",
    "details": null
  }
}
```

---

## 3. Refresh Token

**Endpoint:** `POST /api/auth/refresh`

**Description:** Get new access token using refresh token

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

---

## 4. Logout

**Endpoint:** `POST /api/auth/logout`

**Description:** Logout user (invalidate token on client side)

**Success Response (200):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Token Usage

Include the access token in all authenticated requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Expiration:**
- Access Token: 30 minutes
- Refresh Token: 7 days

**Example with cURL:**
```bash
curl -X GET "http://localhost:8000/api/users/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example with JavaScript:**
```javascript
fetch('http://localhost:8000/api/users/profile', {
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
})
```