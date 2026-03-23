# Analytics API Documentation

---

## 1. Get Performance Analytics

**Endpoint:** `GET /api/analytics/performance`

**Description:** Get user's performance metrics and analytics

**Query Parameters:**
- `period` (string, optional): Time period - "week", "month", "semester" (default: "month")
- `course_id` (UUID, optional): Filter by specific course

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Example Request:**
```
GET /api/analytics/performance?period=month&course_id=770e8400-e29b-41d4-a716-446655440000
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_time_spent": 1200,
      "courses_completed": 3,
      "average_score": 87.5,
      "streak_days": 15
    },
    "course_progress": [
      {
        "course_id": "770e8400-e29b-41d4-a716-446655440000",
        "course_name": "Introduction to Python Programming",
        "progress": 75.0,
        "time_spent": 450,
        "last_accessed": "2024-03-15T14:30:00Z"
      },
      {
        "course_id": "880e8400-e29b-41d4-a716-446655440000",
        "course_name": "Data Structures",
        "progress": 100.0,
        "time_spent": 600,
        "last_accessed": "2024-03-10T16:00:00Z"
      }
    ],
    "weekly_activity": [
      {
        "date": "2024-03-09",
        "time_spent": 120,
        "topics_completed": 3
      },
      {
        "date": "2024-03-10",
        "time_spent": 180,
        "topics_completed": 4
      },
      {
        "date": "2024-03-11",
        "time_spent": 90,
        "topics_completed": 2
      },
      {
        "date": "2024-03-12",
        "time_spent": 150,
        "topics_completed": 3
      },
      {
        "date": "2024-03-13",
        "time_spent": 60,
        "topics_completed": 1
      },
      {
        "date": "2024-03-14",
        "time_spent": 200,
        "topics_completed": 5
      },
      {
        "date": "2024-03-15",
        "time_spent": 100,
        "topics_completed": 2
      }
    ]
  }
}
```

---

## 2. Get Accessibility Analytics

**Endpoint:** `GET /api/analytics/accessibility`

**Description:** Get accessibility feature usage analytics

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "feature_usage": {
      "bionic_reading": 45,
      "voice_navigation": 120,
      "text_to_speech": 89,
      "high_contrast": 200
    },
    "accessibility_score": 85.5,
    "recommendations": [
      "Consider enabling bionic reading for better comprehension",
      "Voice navigation can help with hands-free learning",
      "Try text-to-speech for audio learning"
    ]
  }
}
```

---

## 3. Track Accessibility Feature Usage

**Endpoint:** `POST /api/analytics/accessibility/{feature}`

**Description:** Track when user uses an accessibility feature

**Path Parameters:**
- `feature` (string): Feature name
  - `bionic_reading`
  - `voice_navigation`
  - `text_to_speech`
  - `high_contrast`

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Example Request:**
```
POST /api/analytics/accessibility/bionic_reading
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Tracked usage of bionic_reading"
}
```

---

## Frontend Implementation Examples

### React Dashboard Component

```typescript
// components/AnalyticsDashboard.tsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface PerformanceData {
  overview: {
    total_time_spent: number;
    courses_completed: number;
    average_score: number;
    streak_days: number;
  };
  weekly_activity: Array<{
    date: string;
    time_spent: number;
    topics_completed: number;
  }>;
}

export const AnalyticsDashboard: React.FC<{ token: string }> = ({ token }) => {
  const [data, setData] = useState<PerformanceData | null>(null);
  const [period, setPeriod] = useState('month');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [period]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `http://localhost:8000/api/analytics/performance?period=${period}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      setData(response.data.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!data) return <div>No data available</div>;

  return (
    <div className="analytics-dashboard">
      <div className="overview-cards">
        <div className="card">
          <h3>Total Time</h3>
          <p>{Math.floor(data.overview.total_time_spent / 60)}h {data.overview.total_time_spent % 60}m</p>
        </div>
        <div className="card">
          <h3>Courses Completed</h3>
          <p>{data.overview.courses_completed}</p>
        </div>
        <div className="card">
          <h3>Average Score</h3>
          <p>{data.overview.average_score}%</p>
        </div>
        <div className="card">
          <h3>Streak Days</h3>
          <p>{data.overview.streak_days} days</p>
        </div>
      </div>

      <div className="activity-chart">
        <h3>Weekly Activity</h3>
        <LineChart width={800} height={400} data={data.weekly_activity}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="time_spent" stroke="#8884d8" name="Time Spent (min)" />
          <Line type="monotone" dataKey="topics_completed" stroke="#82ca9d" name="Topics Completed" />
        </LineChart>
      </div>

      <div className="period-selector">
        <button onClick={() => setPeriod('week')}>Week</button>
        <button onClick={() => setPeriod('month')}>Month</button>
        <button onClick={() => setPeriod('semester')}>Semester</button>
      </div>
    </div>
  );
};
```

### Vue.js Analytics Composable

```javascript
// composables/useAnalytics.js
import { ref, computed } from 'vue';
import axios from 'axios';

export function useAnalytics(token) {
  const performanceData = ref(null);
  const accessibilityData = ref(null);
  const loading = ref(false);
  const error = ref(null);

  const totalHours = computed(() => {
    if (!performanceData.value) return 0;
    return Math.floor(performanceData.value.overview.total_time_spent / 60);
  });

  const fetchPerformance = async (period = 'month', courseId = null) => {
    loading.value = true;
    error.value = null;

    try {
      let url = `/api/analytics/performance?period=${period}`;
      if (courseId) url += `&course_id=${courseId}`;

      const response = await axios.get(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      performanceData.value = response.data.data;
    } catch (err) {
      error.value = err.response?.data?.error?.message || 'Failed to fetch analytics';
    } finally {
      loading.value = false;
    }
  };

  const fetchAccessibility = async () => {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.get('/api/analytics/accessibility', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      accessibilityData.value = response.data.data;
    } catch (err) {
      error.value = err.response?.data?.error?.message || 'Failed to fetch accessibility data';
    } finally {
      loading.value = false;
    }
  };

  const trackFeatureUsage = async (feature) => {
    try {
      await axios.post(
        `/api/analytics/accessibility/${feature}`,
        {},
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
    } catch (err) {
      console.error('Failed to track feature usage:', err);
    }
  };

  return {
    performanceData,
    accessibilityData,
    loading,
    error,
    totalHours,
    fetchPerformance,
    fetchAccessibility,
    trackFeatureUsage
  };
}
```