# Progress Tracking API Documentation

---

## 1. Get Course Progress

**Endpoint:** `GET /api/progress/{course_id}`

**Description:** Get user's progress for a specific course

**Path Parameters:**
- `course_id` (UUID): Course ID

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "course_id": "770e8400-e29b-41d4-a716-446655440000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "completed_topics": 5,
    "total_topics": 20,
    "completion_percentage": 25.0,
    "time_spent": 180,
    "current_topic": "990e8400-e29b-41d4-a716-446655440005",
    "last_accessed_at": "2024-03-15T14:30:00Z",
    "topic_progress": [
      {
        "topic_id": "990e8400-e29b-41d4-a716-446655440000",
        "status": "completed",
        "time_spent": 30,
        "score": 95.0,
        "completed_at": "2024-03-10T10:00:00Z"
      },
      {
        "topic_id": "990e8400-e29b-41d4-a716-446655440001",
        "status": "completed",
        "time_spent": 45,
        "score": 88.0,
        "completed_at": "2024-03-11T11:30:00Z"
      },
      {
        "topic_id": "990e8400-e29b-41d4-a716-446655440002",
        "status": "in_progress",
        "time_spent": 20,
        "score": 0.0,
        "completed_at": null
      },
      {
        "topic_id": "990e8400-e29b-41d4-a716-446655440003",
        "status": "not_started",
        "time_spent": 0,
        "score": 0.0,
        "completed_at": null
      }
    ]
  }
}
```

**Progress Status Values:**
- `not_started`: Topic not yet accessed
- `in_progress`: Topic started but not completed
- `completed`: Topic completed

---

## 2. Update Topic Progress

**Endpoint:** `POST /api/progress/{course_id}/topics/{topic_id}`

**Description:** Update progress for a specific topic

**Path Parameters:**
- `course_id` (UUID): Course ID
- `topic_id` (UUID): Topic ID

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "status": "completed",
  "time_spent": 30,
  "score": 95.0
}
```

**Field Descriptions:**
- `status` (string, required): Progress status
  - `"in_progress"`: Topic started
  - `"completed"`: Topic finished
- `time_spent` (integer, optional): Time spent in minutes
- `score` (float, optional): Assessment score (0-100)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "topic_id": "990e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "time_spent": 30,
    "score": 95.0,
    "completed_at": "2024-03-15T15:30:00Z"
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Topic not found",
    "details": null
  }
}
```

---

## Frontend Implementation Examples

### React Hook Example

```typescript
// hooks/useProgress.ts
import { useState, useEffect } from 'react';
import axios from 'axios';

interface TopicProgress {
  topic_id: string;
  status: 'not_started' | 'in_progress' | 'completed';
  time_spent: number;
  score: number;
  completed_at: string | null;
}

interface CourseProgress {
  course_id: string;
  user_id: string;
  completed_topics: number;
  total_topics: number;
  completion_percentage: number;
  time_spent: number;
  current_topic: string | null;
  last_accessed_at: string;
  topic_progress: TopicProgress[];
}

export const useProgress = (courseId: string, token: string) => {
  const [progress, setProgress] = useState<CourseProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchProgress();
  }, [courseId]);

  const fetchProgress = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `http://localhost:8000/api/progress/${courseId}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      setProgress(response.data.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to fetch progress');
    } finally {
      setLoading(false);
    }
  };

  const updateTopicProgress = async (
    topicId: string,
    status: string,
    timeSpent: number,
    score?: number
  ) => {
    try {
      const response = await axios.post(
        `http://localhost:8000/api/progress/${courseId}/topics/${topicId}`,
        {
          status,
          time_spent: timeSpent,
          score: score || 0
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Refresh progress after update
      await fetchProgress();
      
      return response.data;
    } catch (err: any) {
      throw new Error(err.response?.data?.error?.message || 'Failed to update progress');
    }
  };

  return {
    progress,
    loading,
    error,
    updateTopicProgress,
    refreshProgress: fetchProgress
  };
};
```

### Vue.js Composable Example

```javascript
// composables/useProgress.js
import { ref, computed } from 'vue';
import axios from 'axios';

export function useProgress(courseId, token) {
  const progress = ref(null);
  const loading = ref(false);
  const error = ref(null);

  const completionPercentage = computed(() => {
    return progress.value?.completion_percentage || 0;
  });

  const isCompleted = computed(() => {
    return completionPercentage.value === 100;
  });

  const fetchProgress = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await axios.get(
        `/api/progress/${courseId}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      progress.value = response.data.data;
    } catch (err) {
      error.value = err.response?.data?.error?.message || 'Failed to fetch progress';
    } finally {
      loading.value = false;
    }
  };

  const updateTopicProgress = async (topicId, status, timeSpent, score = 0) => {
    loading.value = true;
    error.value = null;
    
    try {
      await axios.post(
        `/api/progress/${courseId}/topics/${topicId}`,
        {
          status,
          time_spent: timeSpent,
          score
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // Refresh progress
      await fetchProgress();
    } catch (err) {
      error.value = err.response?.data?.error?.message || 'Failed to update progress';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const markTopicComplete = async (topicId, timeSpent, score) => {
    return updateTopicProgress(topicId, 'completed', timeSpent, score);
  };

  const startTopic = async (topicId) => {
    return updateTopicProgress(topicId, 'in_progress', 0);
  };

  return {
    progress,
    loading,
    error,
    completionPercentage,
    isCompleted,
    fetchProgress,
    updateTopicProgress,
    markTopicComplete,
    startTopic
  };
}
```

### Angular Service Example

```typescript
// services/progress.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';

interface ProgressUpdate {
  status: 'in_progress' | 'completed';
  time_spent: number;
  score?: number;
}

@Injectable({
  providedIn: 'root'
})
export class ProgressService {
  private apiUrl = 'http://localhost:8000/api/progress';
  private progressSubject = new BehaviorSubject<any>(null);
  public progress$ = this.progressSubject.asObservable();

  constructor(private http: HttpClient) {}

  private getHeaders(token: string): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });
  }

  getCourseProgress(courseId: string, token: string): Observable<any> {
    return this.http.get(
      `${this.apiUrl}/${courseId}`,
      { headers: this.getHeaders(token) }
    ).pipe(
      tap(response => this.progressSubject.next(response.data))
    );
  }

  updateTopicProgress(
    courseId: string,
    topicId: string,
    update: ProgressUpdate,
    token: string
  ): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/${courseId}/topics/${topicId}`,
      update,
      { headers: this.getHeaders(token) }
    ).pipe(
      tap(() => {
        // Refresh progress after update
        this.getCourseProgress(courseId, token).subscribe();
      })
    );
  }

  markTopicComplete(
    courseId: string,
    topicId: string,
    timeSpent: number,
    score: number,
    token: string
  ): Observable<any> {
    return this.updateTopicProgress(
      courseId,
      topicId,
      { status: 'completed', time_spent: timeSpent, score },
      token
    );
  }
}
```