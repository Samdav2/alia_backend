# Backend File Storage & Course Status Management Fix

## Issues Fixed

### 1. File URL Issue
**Problem**: Frontend was receiving "No file URL available" because backend wasn't returning proper file URLs.

**Solution**: 
- Added `BASE_URL` configuration to `app/config.py`
- Created `/api/files/download/{file_id}` endpoint to serve files
- Updated file upload response to return full download URLs
- Updated file list endpoints to include proper URLs

### 2. Course Status Management
**Problem**: No admin endpoint to change course status from draft to published.

**Solution**:
- Added `/api/admin/courses/{course_id}/status` endpoint for admins
- Added `AdminService.change_course_status()` method
- Maps "published" status to `is_active = True` and "draft" to `is_active = False`

### 3. UUID Validation Fix
**Problem**: Course endpoints were throwing "Invalid course ID or topic ID format" errors.

**Solution**:
- Added UUID validation to all course-related endpoints
- Added proper error handling with descriptive messages
- Applied to both admin and lecturer endpoints

## New Endpoints Added

### Admin Course Status Management
```
PUT /api/admin/courses/{course_id}/status
Body: {"status": "published" | "draft"}
```

### File Download/Serve
```
GET /api/files/download/{file_id}
Returns: File with proper headers and content-type
```

## Configuration Changes

### app/config.py
- Added `base_url` setting for file URL generation
- Defaults to `http://localhost:8000`

### .env.example
- Added `BASE_URL=http://localhost:8000` configuration

## File Service Updates

### File Upload Response
Now returns:
```json
{
  "success": true,
  "data": {
    "file_id": "uuid",
    "filename": "stored_filename",
    "original_filename": "user_filename",
    "url": "http://localhost:8000/api/files/download/{file_id}",
    "type": "file_extension",
    "size": 12345,
    "context": "course|module|topic|general",
    "course_id": "uuid",
    "uploaded_at": "timestamp",
    "uploaded_by": "user_id"
  }
}
```

### File List Response
Each file now includes a proper `url` field pointing to the download endpoint.

## Usage Examples

### Change Course Status (Admin)
```bash
curl -X PUT "http://localhost:8000/api/admin/courses/{course_id}/status" \
  -H "Authorization: Bearer {admin_token}" \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}'
```

### Download File
```bash
curl "http://localhost:8000/api/files/download/{file_id}" \
  -H "Authorization: Bearer {token}" \
  -o downloaded_file.pdf
```

## Frontend Integration

The frontend file viewing system is now ready to work with proper file URLs. Files uploaded will return valid download URLs that can be used directly in the frontend for:

- Document previews
- Image displays
- Video playback
- File downloads

## Status Mapping

| Frontend Status | Backend Field | Value |
|----------------|---------------|-------|
| "draft" | `is_active` | `false` |
| "published" | `is_active` | `true` |

## Security Notes

- All endpoints require proper authentication
- Admin endpoints require admin role
- Lecturer endpoints verify course ownership
- File downloads respect access permissions
- UUID validation prevents injection attacks

The backend is now fully configured for file storage and course status management!