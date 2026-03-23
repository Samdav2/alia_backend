# Files & Notifications API Documentation

## File Management

### 1. Upload File

**Endpoint:** `POST /api/files/upload`

**Description:** Upload a file (images, videos, documents)

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request Body (FormData):**
```
file: [binary file data]
```

**Allowed File Types:**
- Images: .jpg, .jpeg, .png
- Documents: .pdf, .doc, .docx
- Media: .mp4, .mp3

**Max File Size:** 10MB

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "file_id": "ff0e8400-e29b-41d4-a716-446655440000",
    "filename": "ff0e8400-e29b-41d4-a716-446655440000.pdf",
    "url": "/api/files/ff0e8400-e29b-41d4-a716-446655440000",
    "type": ".pdf",
    "size": 2048576
  }
}
```

**Error Response (400):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "File type not allowed",
    "details": null
  }
}
```

---

### 2. Get File Information

**Endpoint:** `GET /api/files/{file_id}`

**Description:** Get file metadata

**Path Parameters:**
- `file_id` (UUID): File ID

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "ff0e8400-e29b-41d4-a716-446655440000",
    "filename": "ff0e8400-e29b-41d4-a716-446655440000.pdf",
    "original_filename": "course-notes.pdf",
    "file_type": ".pdf",
    "file_size": 2048576,
    "mime_type": "application/pdf",
    "alt_text": "Course notes for Python programming",
    "description": "Comprehensive notes covering all topics",
    "is_public": false,
    "created_at": "2024-03-15T10:00:00Z"
  }
}
```

---

### 3. Delete File

**Endpoint:** `DELETE /api/files/{file_id}`

**Description:** Permanently delete an uploaded file (removes both database record and physical file)

**Path Parameters:**
- `file_id` (UUID): File ID

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Authorization:** Users can only delete files they uploaded

**Success Response (200):**
```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

**Error Responses:**

400 Bad Request - Invalid UUID:
```json
{
  "detail": "Invalid file ID format"
}
```

404 Not Found - File not found or access denied:
```json
{
  "detail": "File not found or access denied"
}
```

**Note:** For complete documentation including code examples, testing, and best practices, see [API_FILE_DELETE.md](./API_FILE_DELETE.md)

---

## Notifications

### 1. Get Notifications

**Endpoint:** `GET /api/notifications`

**Description:** Get user's notifications

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": "aa0e8400-e29b-41d4-a716-446655440000",
        "type": "course_update",
        "title": "New Module Added",
        "message": "A new module 'Advanced Topics' has been added to Python Programming",
        "action_url": "/courses/770e8400-e29b-41d4-a716-446655440000",
        "is_read": false,
        "created_at": "2024-03-15T14:30:00Z"
      },
      {
        "id": "bb0e8400-e29b-41d4-a716-446655440000",
        "type": "assignment_due",
        "title": "Assignment Due Soon",
        "message": "Your assignment for Data Structures is due in 2 days",
        "action_url": "/courses/880e8400-e29b-41d4-a716-446655440000/assignments/1",
        "is_read": false,
        "created_at": "2024-03-15T10:00:00Z"
      },
      {
        "id": "cc0e8400-e29b-41d4-a716-446655440000",
        "type": "achievement",
        "title": "Achievement Unlocked!",
        "message": "You've completed 5 courses! Keep up the great work!",
        "action_url": "/profile/achievements",
        "is_read": true,
        "created_at": "2024-03-14T16:00:00Z"
      }
    ],
    "unread_count": 2
  }
}
```

**Notification Types:**
- `course_update`: Course content updated
- `assignment_due`: Assignment deadline approaching
- `achievement`: Achievement unlocked
- `system`: System announcements

---

### 2. Mark Notification as Read

**Endpoint:** `PUT /api/notifications/{notification_id}/read`

**Description:** Mark a notification as read

**Path Parameters:**
- `notification_id` (UUID): Notification ID

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

---

### 3. Mark All Notifications as Read

**Endpoint:** `PUT /api/notifications/read-all`

**Description:** Mark all notifications as read

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "All notifications marked as read"
}
```

---

## Frontend Implementation Examples

### React File Upload Component

```typescript
// components/FileUpload.tsx
import React, { useState } from 'react';
import axios from 'axios';

export const FileUpload: React.FC<{ token: string; onUploadComplete: (fileData: any) => void }> = ({
  token,
  onUploadComplete
}) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    // Validate file type
    const allowedTypes = ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx', '.mp4', '.mp3'];
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!allowedTypes.includes(fileExt)) {
      setError('File type not allowed');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setError(null);

    try {
      const response = await axios.post(
        'http://localhost:8000/api/files/upload',
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / (progressEvent.total || 1)
            );
            setProgress(percentCompleted);
          }
        }
      );

      onUploadComplete(response.data.data);
      setProgress(0);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="file-upload">
      <input
        type="file"
        onChange={handleFileSelect}
        disabled={uploading}
        accept=".jpg,.jpeg,.png,.pdf,.doc,.docx,.mp4,.mp3"
      />
      
      {uploading && (
        <div className="progress-bar">
          <div className="progress" style={{ width: `${progress}%` }}>
            {progress}%
          </div>
        </div>
      )}
      
      {error && <div className="error">{error}</div>}
    </div>
  );
};
```

### Vue.js Notifications Component

```vue
<template>
  <div class="notifications">
    <div class="header">
      <h3>Notifications</h3>
      <span class="badge" v-if="unreadCount > 0">{{ unreadCount }}</span>
      <button @click="markAllAsRead" v-if="unreadCount > 0">
        Mark all as read
      </button>
    </div>

    <div class="notification-list">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="['notification-item', { unread: !notification.is_read }]"
        @click="handleNotificationClick(notification)"
      >
        <div class="icon" :class="notification.type">
          <i :class="getIcon(notification.type)"></i>
        </div>
        
        <div class="content">
          <h4>{{ notification.title }}</h4>
          <p>{{ notification.message }}</p>
          <span class="time">{{ formatTime(notification.created_at) }}</span>
        </div>
        
        <button
          v-if="!notification.is_read"
          @click.stop="markAsRead(notification.id)"
          class="mark-read"
        >
          ✓
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const props = defineProps(['token']);
const router = useRouter();

const notifications = ref([]);
const unreadCount = ref(0);

const fetchNotifications = async () => {
  try {
    const response = await axios.get('/api/notifications', {
      headers: { 'Authorization': `Bearer ${props.token}` }
    });
    notifications.value = response.data.data.notifications;
    unreadCount.value = response.data.data.unread_count;
  } catch (error) {
    console.error('Failed to fetch notifications:', error);
  }
};

const markAsRead = async (notificationId) => {
  try {
    await axios.put(
      `/api/notifications/${notificationId}/read`,
      {},
      {
        headers: { 'Authorization': `Bearer ${props.token}` }
      }
    );
    await fetchNotifications();
  } catch (error) {
    console.error('Failed to mark as read:', error);
  }
};

const markAllAsRead = async () => {
  try {
    await axios.put(
      '/api/notifications/read-all',
      {},
      {
        headers: { 'Authorization': `Bearer ${props.token}` }
      }
    );
    await fetchNotifications();
  } catch (error) {
    console.error('Failed to mark all as read:', error);
  }
};

const handleNotificationClick = async (notification) => {
  if (!notification.is_read) {
    await markAsRead(notification.id);
  }
  if (notification.action_url) {
    router.push(notification.action_url);
  }
};

const getIcon = (type) => {
  const icons = {
    course_update: 'fas fa-book',
    assignment_due: 'fas fa-clock',
    achievement: 'fas fa-trophy',
    system: 'fas fa-info-circle'
  };
  return icons[type] || 'fas fa-bell';
};

const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now - date;
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
};

onMounted(() => {
  fetchNotifications();
  // Poll for new notifications every 30 seconds
  setInterval(fetchNotifications, 30000);
});
</script>
```