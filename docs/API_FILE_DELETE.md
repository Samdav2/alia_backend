# File Delete Endpoint - Complete Documentation

## Overview

The file delete endpoint allows authenticated users to permanently delete files they have uploaded to the ALIA platform. This endpoint removes both the file record from the database and the physical file from disk storage.

---

## Endpoint Details

### DELETE /api/files/{file_id}

**Description:** Permanently delete an uploaded file

**Authentication:** Required (Bearer Token)

**Authorization:** Users can only delete files they uploaded

---

## Request Specification

### URL Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | UUID | Yes | Unique identifier of the file to delete |

### Headers

```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

### Example Request

```bash
curl -X DELETE \
  'http://localhost:8000/api/files/ff0e8400-e29b-41d4-a716-446655440000' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
```

---

## Response Specification

### Success Response (200 OK)

**Description:** File successfully deleted

```json
{
  "success": true,
  "message": "File deleted successfully"
}
```

### Error Responses

#### 400 Bad Request - Invalid UUID Format

```json
{
  "detail": "Invalid file ID format"
}
```

**Cause:** The provided file_id is not a valid UUID

**Example:**
```bash
# Invalid file_id
DELETE /api/files/invalid-id
```

---

#### 401 Unauthorized - Missing or Invalid Token

```json
{
  "detail": "Not authenticated"
}
```

**Cause:** No authentication token provided or token is invalid/expired

**Solution:** Include valid Bearer token in Authorization header

---

#### 404 Not Found - File Not Found or Access Denied

```json
{
  "detail": "File not found or access denied"
}
```

**Causes:**
1. File with the given ID doesn't exist
2. File exists but was uploaded by a different user
3. File was already deleted

**Note:** For security reasons, the API returns the same error message whether the file doesn't exist or the user doesn't have permission to delete it.

---

## Business Logic

### Deletion Process

1. **Authentication Check**
   - Validates Bearer token
   - Extracts user ID from token

2. **UUID Validation**
   - Validates file_id is a proper UUID format
   - Returns 400 if invalid

3. **Authorization Check**
   - Queries database for file with matching file_id AND uploaded_by = current_user_id
   - Ensures users can only delete their own files

4. **Physical File Deletion**
   - Checks if file exists on disk at the stored file_path
   - Removes physical file using `os.remove()`
   - Continues even if physical file is missing (handles orphaned records)

5. **Database Record Deletion**
   - Removes file record from database
   - Commits transaction

6. **Response**
   - Returns success message

### Security Features

- **User Isolation:** Users can only delete files they uploaded
- **UUID Validation:** Prevents SQL injection and invalid queries
- **Atomic Operation:** Database transaction ensures consistency
- **Graceful Handling:** Handles missing physical files without errors

---

## Code Examples

### JavaScript/TypeScript (Axios)

```typescript
import axios from 'axios';

interface DeleteFileResponse {
  success: boolean;
  message: string;
}

async function deleteFile(
  fileId: string,
  token: string
): Promise<DeleteFileResponse> {
  try {
    const response = await axios.delete<DeleteFileResponse>(
      `http://localhost:8000/api/files/${fileId}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    return response.data;
  } catch (error: any) {
    if (error.response) {
      // Server responded with error
      throw new Error(error.response.data.detail || 'Failed to delete file');
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server');
    } else {
      // Error setting up request
      throw new Error('Failed to make request');
    }
  }
}

// Usage
const token = 'your-access-token';
const fileId = 'ff0e8400-e29b-41d4-a716-446655440000';

deleteFile(fileId, token)
  .then(result => {
    console.log('Success:', result.message);
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

---

### React Component with Confirmation

```typescript
import React, { useState } from 'react';
import axios from 'axios';

interface FileItemProps {
  file: {
    id: string;
    original_filename: string;
    file_size: number;
    created_at: string;
  };
  token: string;
  onDelete: (fileId: string) => void;
}

export const FileItem: React.FC<FileItemProps> = ({ file, token, onDelete }) => {
  const [deleting, setDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDelete = async () => {
    setDeleting(true);
    setError(null);

    try {
      const response = await axios.delete(
        `http://localhost:8000/api/files/${file.id}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data.success) {
        onDelete(file.id);
        setShowConfirm(false);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete file';
      setError(errorMessage);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="file-item">
      <div className="file-info">
        <span className="filename">{file.original_filename}</span>
        <span className="filesize">{(file.file_size / 1024).toFixed(2)} KB</span>
        <span className="date">{new Date(file.created_at).toLocaleDateString()}</span>
      </div>

      <button
        onClick={() => setShowConfirm(true)}
        className="delete-btn"
        disabled={deleting}
      >
        Delete
      </button>

      {showConfirm && (
        <div className="confirm-dialog">
          <p>Are you sure you want to delete "{file.original_filename}"?</p>
          <p className="warning">This action cannot be undone.</p>
          
          <div className="actions">
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="confirm-btn"
            >
              {deleting ? 'Deleting...' : 'Yes, Delete'}
            </button>
            <button
              onClick={() => setShowConfirm(false)}
              disabled={deleting}
              className="cancel-btn"
            >
              Cancel
            </button>
          </div>

          {error && <div className="error">{error}</div>}
        </div>
      )}
    </div>
  );
};
```

---

### Python (Requests)

```python
import requests
from typing import Dict, Optional

def delete_file(file_id: str, token: str, base_url: str = "http://localhost:8000") -> Dict:
    """
    Delete a file from the ALIA platform
    
    Args:
        file_id: UUID of the file to delete
        token: JWT access token
        base_url: Base URL of the API
        
    Returns:
        Response dictionary with success status and message
        
    Raises:
        requests.HTTPError: If the request fails
    """
    url = f"{base_url}/api/files/{file_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

# Usage example
if __name__ == "__main__":
    token = "your-access-token"
    file_id = "ff0e8400-e29b-41d4-a716-446655440000"
    
    try:
        result = delete_file(file_id, token)
        print(f"✓ {result['message']}")
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            print("✗ File not found or you don't have permission to delete it")
        elif e.response.status_code == 400:
            print("✗ Invalid file ID format")
        elif e.response.status_code == 401:
            print("✗ Authentication failed")
        else:
            print(f"✗ Error: {e.response.text}")
```

---

### Vue.js Composition API

```vue
<template>
  <div class="file-manager">
    <div v-for="file in files" :key="file.id" class="file-card">
      <div class="file-details">
        <h4>{{ file.original_filename }}</h4>
        <p>{{ formatFileSize(file.file_size) }}</p>
        <p>{{ formatDate(file.created_at) }}</p>
      </div>

      <button
        @click="confirmDelete(file)"
        :disabled="deletingFileId === file.id"
        class="delete-button"
      >
        {{ deletingFileId === file.id ? 'Deleting...' : 'Delete' }}
      </button>
    </div>

    <!-- Confirmation Modal -->
    <div v-if="fileToDelete" class="modal-overlay" @click="cancelDelete">
      <div class="modal" @click.stop>
        <h3>Confirm Deletion</h3>
        <p>Are you sure you want to delete "{{ fileToDelete.original_filename }}"?</p>
        <p class="warning">This action cannot be undone.</p>

        <div class="modal-actions">
          <button @click="deleteFile" class="confirm-btn">Delete</button>
          <button @click="cancelDelete" class="cancel-btn">Cancel</button>
        </div>

        <div v-if="deleteError" class="error">{{ deleteError }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';

interface File {
  id: string;
  original_filename: string;
  file_size: number;
  created_at: string;
}

const props = defineProps<{
  files: File[];
  token: string;
}>();

const emit = defineEmits<{
  fileDeleted: [fileId: string];
}>();

const fileToDelete = ref<File | null>(null);
const deletingFileId = ref<string | null>(null);
const deleteError = ref<string | null>(null);

const confirmDelete = (file: File) => {
  fileToDelete.value = file;
  deleteError.value = null;
};

const cancelDelete = () => {
  fileToDelete.value = null;
  deleteError.value = null;
};

const deleteFile = async () => {
  if (!fileToDelete.value) return;

  const fileId = fileToDelete.value.id;
  deletingFileId.value = fileId;
  deleteError.value = null;

  try {
    const response = await axios.delete(
      `http://localhost:8000/api/files/${fileId}`,
      {
        headers: {
          'Authorization': `Bearer ${props.token}`
        }
      }
    );

    if (response.data.success) {
      emit('fileDeleted', fileId);
      fileToDelete.value = null;
    }
  } catch (error: any) {
    deleteError.value = error.response?.data?.detail || 'Failed to delete file';
  } finally {
    deletingFileId.value = null;
  }
};

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};
</script>

<style scoped>
.file-manager {
  display: grid;
  gap: 1rem;
}

.file-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.delete-button {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.delete-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 400px;
}

.warning {
  color: #dc3545;
  font-weight: bold;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.confirm-btn {
  background-color: #dc3545;
  color: white;
}

.cancel-btn {
  background-color: #6c757d;
  color: white;
}

.error {
  color: #dc3545;
  margin-top: 1rem;
}
</style>
```

---

### Angular Service

```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

interface DeleteFileResponse {
  success: boolean;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class FileService {
  private baseUrl = 'http://localhost:8000/api/files';

  constructor(private http: HttpClient) {}

  deleteFile(fileId: string, token: string): Observable<string> {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    return this.http.delete<DeleteFileResponse>(
      `${this.baseUrl}/${fileId}`,
      { headers }
    ).pipe(
      map(response => {
        if (response.success) {
          return response.message;
        }
        throw new Error('Delete operation failed');
      }),
      catchError(error => {
        let errorMessage = 'Failed to delete file';
        
        if (error.status === 404) {
          errorMessage = 'File not found or access denied';
        } else if (error.status === 400) {
          errorMessage = 'Invalid file ID';
        } else if (error.status === 401) {
          errorMessage = 'Authentication required';
        } else if (error.error?.detail) {
          errorMessage = error.error.detail;
        }
        
        return throwError(() => new Error(errorMessage));
      })
    );
  }
}

// Component usage
import { Component } from '@angular/core';
import { FileService } from './file.service';

@Component({
  selector: 'app-file-list',
  template: `
    <div *ngFor="let file of files" class="file-item">
      <span>{{ file.original_filename }}</span>
      <button 
        (click)="deleteFile(file.id)"
        [disabled]="deleting"
      >
        {{ deleting ? 'Deleting...' : 'Delete' }}
      </button>
    </div>
    <div *ngIf="error" class="error">{{ error }}</div>
  `
})
export class FileListComponent {
  files: any[] = [];
  deleting = false;
  error: string | null = null;

  constructor(private fileService: FileService) {}

  deleteFile(fileId: string): void {
    if (!confirm('Are you sure you want to delete this file?')) {
      return;
    }

    this.deleting = true;
    this.error = null;

    const token = localStorage.getItem('access_token') || '';

    this.fileService.deleteFile(fileId, token).subscribe({
      next: (message) => {
        console.log(message);
        this.files = this.files.filter(f => f.id !== fileId);
        this.deleting = false;
      },
      error: (error) => {
        this.error = error.message;
        this.deleting = false;
      }
    });
  }
}
```

---

## Testing

### Manual Testing with cURL

```bash
# 1. Login to get token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student@alia.edu.ng&password=student123"

# Response: { "access_token": "eyJhbGc...", ... }

# 2. Upload a test file
curl -X POST http://localhost:8000/api/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf"

# Response: { "success": true, "data": { "file_id": "abc-123-...", ... } }

# 3. Delete the file
curl -X DELETE http://localhost:8000/api/files/abc-123-... \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response: { "success": true, "message": "File deleted successfully" }

# 4. Verify deletion (should return 404)
curl -X GET http://localhost:8000/api/files/abc-123-... \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response: { "detail": "File not found" }
```

### Automated Testing (Python/Pytest)

```python
import pytest
import requests
from uuid import uuid4

BASE_URL = "http://localhost:8000"

@pytest.fixture
def auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": "student@alia.edu.ng",
            "password": "student123"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def uploaded_file(auth_token):
    """Upload a test file"""
    with open("test_file.pdf", "rb") as f:
        response = requests.post(
            f"{BASE_URL}/api/files/upload",
            headers={"Authorization": f"Bearer {auth_token}"},
            files={"file": f}
        )
    return response.json()["data"]["file_id"]

def test_delete_file_success(auth_token, uploaded_file):
    """Test successful file deletion"""
    response = requests.delete(
        f"{BASE_URL}/api/files/{uploaded_file}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "deleted successfully" in response.json()["message"]

def test_delete_file_not_found(auth_token):
    """Test deleting non-existent file"""
    fake_id = str(uuid4())
    response = requests.delete(
        f"{BASE_URL}/api/files/{fake_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_delete_file_invalid_uuid(auth_token):
    """Test deleting with invalid UUID"""
    response = requests.delete(
        f"{BASE_URL}/api/files/invalid-uuid",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 400
    assert "invalid" in response.json()["detail"].lower()

def test_delete_file_unauthorized():
    """Test deleting without authentication"""
    fake_id = str(uuid4())
    response = requests.delete(f"{BASE_URL}/api/files/{fake_id}")
    
    assert response.status_code == 401

def test_delete_file_wrong_user(auth_token, uploaded_file):
    """Test deleting another user's file"""
    # Login as different user
    other_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": "lecturer@alia.edu.ng",
            "password": "lecturer123"
        }
    )
    other_token = other_response.json()["access_token"]
    
    # Try to delete first user's file
    response = requests.delete(
        f"{BASE_URL}/api/files/{uploaded_file}",
        headers={"Authorization": f"Bearer {other_token}"}
    )
    
    assert response.status_code == 404  # Returns 404 for security
```

---

## Best Practices

### 1. Always Confirm Before Deletion

```typescript
// Good: Show confirmation dialog
const handleDelete = async (fileId: string) => {
  const confirmed = window.confirm(
    'Are you sure you want to delete this file? This action cannot be undone.'
  );
  
  if (confirmed) {
    await deleteFile(fileId);
  }
};

// Better: Use custom modal with detailed information
const handleDelete = async (file: File) => {
  const confirmed = await showConfirmationModal({
    title: 'Delete File',
    message: `Are you sure you want to delete "${file.original_filename}"?`,
    details: `Size: ${formatSize(file.file_size)}, Uploaded: ${formatDate(file.created_at)}`,
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
  });
  
  if (confirmed) {
    await deleteFile(file.id);
  }
};
```

### 2. Handle Errors Gracefully

```typescript
const deleteFile = async (fileId: string) => {
  try {
    await api.delete(`/files/${fileId}`);
    showSuccessToast('File deleted successfully');
    refreshFileList();
  } catch (error) {
    if (error.response?.status === 404) {
      showErrorToast('File not found or already deleted');
    } else if (error.response?.status === 401) {
      showErrorToast('Please log in again');
      redirectToLogin();
    } else {
      showErrorToast('Failed to delete file. Please try again.');
    }
  }
};
```

### 3. Update UI Optimistically

```typescript
const deleteFile = async (fileId: string) => {
  // Optimistically remove from UI
  const previousFiles = [...files];
  setFiles(files.filter(f => f.id !== fileId));
  
  try {
    await api.delete(`/files/${fileId}`);
    showSuccessToast('File deleted');
  } catch (error) {
    // Restore on error
    setFiles(previousFiles);
    showErrorToast('Failed to delete file');
  }
};
```

### 4. Implement Undo Functionality

```typescript
const deleteFile = async (fileId: string) => {
  const file = files.find(f => f.id === fileId);
  
  // Soft delete with undo option
  setFiles(files.filter(f => f.id !== fileId));
  
  const undoTimeout = setTimeout(async () => {
    try {
      await api.delete(`/files/${fileId}`);
    } catch (error) {
      // Restore if actual deletion fails
      setFiles([...files, file]);
    }
  }, 5000);
  
  showUndoToast('File deleted', () => {
    clearTimeout(undoTimeout);
    setFiles([...files, file]);
  });
};
```

---

## Common Issues and Solutions

### Issue 1: "Invalid file ID format"

**Cause:** File ID is not a valid UUID

**Solution:**
```typescript
// Validate UUID before making request
const isValidUUID = (id: string): boolean => {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(id);
};

if (!isValidUUID(fileId)) {
  console.error('Invalid file ID');
  return;
}
```

### Issue 2: "File not found or access denied"

**Causes:**
- File doesn't exist
- User doesn't own the file
- File was already deleted

**Solution:**
```typescript
// Check file ownership before attempting deletion
const canDeleteFile = (file: File, currentUserId: string): boolean => {
  return file.uploaded_by === currentUserId;
};

if (!canDeleteFile(file, user.id)) {
  showError('You can only delete files you uploaded');
  return;
}
```

### Issue 3: Token Expired During Deletion

**Solution:**
```typescript
const deleteFileWithRetry = async (fileId: string) => {
  try {
    await api.delete(`/files/${fileId}`);
  } catch (error) {
    if (error.response?.status === 401) {
      // Refresh token and retry
      await refreshAuthToken();
      await api.delete(`/files/${fileId}`);
    } else {
      throw error;
    }
  }
};
```

---

## Security Considerations

1. **User Isolation:** Users can only delete their own files
2. **UUID Validation:** Prevents injection attacks
3. **Authentication Required:** All requests must include valid token
4. **No Information Leakage:** Same error for "not found" and "access denied"
5. **Atomic Operations:** Database transactions ensure consistency

---

## Related Endpoints

- `POST /api/files/upload` - Upload new file
- `GET /api/files/{file_id}` - Get file information
- `GET /api/files/download/{file_id}` - Download file
- `GET /api/files` - List user's files
- `PUT /api/files/{file_id}` - Update file metadata

---

## Support

For issues or questions:
- Check the main API documentation
- Review error messages carefully
- Ensure file_id is a valid UUID
- Verify authentication token is valid
- Confirm you own the file you're trying to delete
