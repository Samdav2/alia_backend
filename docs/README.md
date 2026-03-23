# ALIA Platform API Documentation

Complete API documentation for frontend developers.

## 📚 Documentation Files

### Quick Start
- **[API_COMPLETE_REFERENCE.md](./API_COMPLETE_REFERENCE.md)** - Complete API overview and integration guide

### Detailed Endpoint Documentation
1. **[API_AUTHENTICATION.md](./API_AUTHENTICATION.md)** - Authentication & Authorization
2. **[API_USERS.md](./API_USERS.md)** - User Management
3. **[API_COURSES.md](./API_COURSES.md)** - Course Management
4. **[API_ENROLLMENTS.md](./API_ENROLLMENTS.md)** - Enrollment Management
5. **[API_PROGRESS.md](./API_PROGRESS.md)** - Progress Tracking
6. **[API_ANALYTICS.md](./API_ANALYTICS.md)** - Analytics & Reporting
7. **[API_AI_SERVICES.md](./API_AI_SERVICES.md)** - AI Chat & Voice Services
8. **[API_FILES_NOTIFICATIONS.md](./API_FILES_NOTIFICATIONS.md)** - Files & Notifications

## 🚀 Quick Start

### 1. Start the Backend
```bash
python quickstart.py
```

### 2. Access API Documentation
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### 3. Test Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"test123","role":"student","department":"CS"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 📖 What's Included

### For Each Endpoint:
- ✅ HTTP Method and URL
- ✅ Request headers
- ✅ Request body with field descriptions
- ✅ Success response examples
- ✅ Error response examples
- ✅ Frontend implementation examples (React, Vue, Angular)

### Code Examples:
- TypeScript/React hooks
- Vue.js composables
- Angular services
- Axios configuration
- Error handling
- Token management

## 🎯 Common Use Cases

### User Registration & Login
See [API_AUTHENTICATION.md](./API_AUTHENTICATION.md)

### Enrolling in Courses
See [API_ENROLLMENTS.md](./API_ENROLLMENTS.md)

### Tracking Progress
See [API_PROGRESS.md](./API_PROGRESS.md)

### Using AI Features
See [API_AI_SERVICES.md](./API_AI_SERVICES.md)

## 🔑 Authentication Flow

```
1. Register/Login → Get access_token & refresh_token
2. Store tokens in localStorage
3. Include access_token in all requests:
   Authorization: Bearer {access_token}
4. When access_token expires (30 min):
   - Use refresh_token to get new access_token
   - Update stored tokens
   - Retry failed request
```

## 📊 Response Format

All responses follow this structure:

**Success:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": null
  }
}
```

## 🛠️ Frontend Setup

### React/TypeScript
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### Vue.js
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

## 🔒 Security

### Best Practices:
1. Store tokens in localStorage (or httpOnly cookies for better security)
2. Always use HTTPS in production
3. Implement token refresh logic
4. Handle 401 errors by redirecting to login
5. Clear tokens on logout
6. Validate user input before sending to API

## 📱 Mobile Apps

The API works with mobile apps (React Native, Flutter, etc.):
- Use the same authentication flow
- Store tokens securely (AsyncStorage, SecureStore)
- Handle network errors gracefully
- Implement offline support where needed

## 🧪 Testing

### Postman Collection
Import the Postman collection for easy testing:
1. Create new collection
2. Add environment variables:
   - `base_url`: http://localhost:8000
   - `token`: (set after login)
3. Use `{{base_url}}` and `{{token}}` in requests

### Automated Testing
```typescript
// Example Jest test
import api from './api';

describe('Authentication', () => {
  it('should login successfully', async () => {
    const response = await api.post('/api/auth/login', {
      email: 'test@example.com',
      password: 'test123'
    });
    
    expect(response.data.success).toBe(true);
    expect(response.data.data.token).toBeDefined();
  });
});
```

## 🆘 Troubleshooting

### CORS Errors
If you get CORS errors:
1. Backend is configured to allow all origins in development
2. In production, update `allowed_origins` in `app/config.py`

### 401 Unauthorized
- Check if token is included in request
- Verify token hasn't expired
- Try refreshing the token

### 404 Not Found
- Verify the endpoint URL is correct
- Check if backend is running
- Ensure you're using the correct HTTP method

### Rate Limiting
- Authentication: 5 requests/minute
- AI Chat: 30 requests/minute
- General API: 100 requests/minute

## 📞 Support

- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Email**: api-support@alia.edu.ng

## 🔄 Updates

This documentation is for API version 1.0. Check the changelog for updates.

---

**Happy Coding! 🚀**