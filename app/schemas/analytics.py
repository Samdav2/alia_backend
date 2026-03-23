"""
Analytics schemas
"""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class WeeklyActivity(BaseModel):
    date: str
    time_spent: int
    topics_completed: int


class CourseProgress(BaseModel):
    course_id: str
    course_name: str
    progress: float
    time_spent: int
    last_accessed: Optional[datetime] = None


class PerformanceOverview(BaseModel):
    total_time_spent: int
    courses_completed: int
    average_score: float
    streak_days: int


class PerformanceAnalytics(BaseModel):
    overview: PerformanceOverview
    course_progress: List[CourseProgress]
    weekly_activity: List[WeeklyActivity]


class AccessibilityFeatureUsage(BaseModel):
    bionic_reading: int
    voice_navigation: int
    text_to_speech: int
    high_contrast: int


class AccessibilityAnalytics(BaseModel):
    feature_usage: AccessibilityFeatureUsage
    accessibility_score: float
    recommendations: List[str]