# Quiz & Assessment System - Complete Guide

## Overview

The ALIA platform includes a comprehensive quiz and assessment system that allows lecturers to create interactive quizzes for topics within their courses. This guide covers the complete implementation from backend to frontend.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Database Schema](#database-schema)
3. [Backend API Endpoints](#backend-api-endpoints)
4. [Frontend Implementation](#frontend-implementation)
5. [Quiz Types & Question Formats](#quiz-types--question-formats)
6. [Student Quiz Taking Flow](#student-quiz-taking-flow)
7. [Grading & Scoring](#grading--scoring)
8. [Best Practices](#best-practices)

---

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Quiz Builder │  │ Quiz Taker   │  │ Results View │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Quiz CRUD    │  │ Attempt API  │  │ Grading      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    Database (SQLite)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ quizzes      │  │ quiz_attempts│  │ topics       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Quizzes Table

```sql
CREATE TABLE quizzes (
    id UUID PRIMARY KEY,
    title VARCHAR NOT NULL,
    description TEXT,
    topic_id UUID REFERENCES topics(id),
    time_limit INTEGER,  -- in minutes
    passing_score FLOAT DEFAULT 70.0,
    max_attempts INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,
    questions JSON,  -- Array of question objects
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### Quiz Attempts Table

```sql
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY,
    quiz_id UUID REFERENCES quizzes(id),
    user_id UUID REFERENCES users(id),
    score FLOAT,
    answers JSON,  -- User's submitted answers
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    time_taken INTEGER  -- in seconds
);
```

### Question JSON Structure

```json
{
  "id": "q1",
  "question": "What is Python?",
  "type": "multiple_choice",
  "options": [
    {"id": "a", "text": "A programming language"},
    {"id": "b", "text": "A snake"},
    {"id": "c", "text": "A framework"}
  ],
  "correct_answer": "a",
  "explanation": "Python is a high-level programming language",
  "points": 1.0
}
```

---


## Backend API Endpoints

### 1. Create Quiz

**Endpoint:** `POST /api/lecturer/quizzes`

**Authentication:** Required (Lecturer/Admin only)

**Request Body:**
```json
{
  "title": "Python Basics Quiz",
  "description": "Test your knowledge of Python fundamentals",
  "topic_id": "550e8400-e29b-41d4-a716-446655440000",
  "time_limit": 30,
  "passing_score": 70.0,
  "max_attempts": 3,
  "questions": [
    {
      "id": "q1",
      "question": "What is the output of print(2 + 2)?",
      "type": "multiple_choice",
      "options": [
        {"id": "a", "text": "4"},
        {"id": "b", "text": "22"},
        {"id": "c", "text": "Error"}
      ],
      "correct_answer": "a",
      "explanation": "2 + 2 equals 4 in Python",
      "points": 1.0
    },
    {
      "id": "q2",
      "question": "Python is case-sensitive",
      "type": "true_false",
      "options": [
        {"id": "true", "text": "True"},
        {"id": "false", "text": "False"}
      ],
      "correct_answer": "true",
      "explanation": "Python is case-sensitive, 'Variable' and 'variable' are different",
      "points": 1.0
    }
  ]
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "title": "Python Basics Quiz",
    "description": "Test your knowledge of Python fundamentals",
    "topic_id": "550e8400-e29b-41d4-a716-446655440000",
    "time_limit": 30,
    "passing_score": 70.0,
    "max_attempts": 3,
    "is_active": true,
    "questions": [...],
    "created_at": "2024-03-15T10:00:00Z"
  }
}
```

---

### 2. Update Quiz

**Endpoint:** `PUT /api/lecturer/quizzes/{quiz_id}`

**Authentication:** Required (Lecturer/Admin only)

**Request Body:**
```json
{
  "title": "Updated Quiz Title",
  "time_limit": 45,
  "is_active": false
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "title": "Updated Quiz Title",
    "time_limit": 45,
    "is_active": false,
    ...
  }
}
```

---

### 3. Delete Quiz

**Endpoint:** `DELETE /api/lecturer/quizzes/{quiz_id}`

**Authentication:** Required (Lecturer/Admin only)

**Success Response (200):**
```json
{
  "success": true,
  "message": "Quiz deleted successfully"
}
```

---

### 4. Get Quiz (Student View)

**Endpoint:** `GET /api/courses/{course_id}/topics/{topic_id}/quiz`

**Authentication:** Required (Student)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "title": "Python Basics Quiz",
    "description": "Test your knowledge",
    "time_limit": 30,
    "passing_score": 70.0,
    "max_attempts": 3,
    "attempts_taken": 1,
    "questions": [
      {
        "id": "q1",
        "question": "What is Python?",
        "type": "multiple_choice",
        "options": [
          {"id": "a", "text": "A programming language"},
          {"id": "b", "text": "A snake"}
        ],
        "points": 1.0
      }
    ]
  }
}
```

**Note:** Correct answers are NOT included in student view

---

### 5. Submit Quiz Attempt

**Endpoint:** `POST /api/courses/{course_id}/topics/{topic_id}/quiz/submit`

**Authentication:** Required (Student)

**Request Body:**
```json
{
  "quiz_id": "660e8400-e29b-41d4-a716-446655440000",
  "answers": {
    "q1": "a",
    "q2": "true",
    "q3": "Python is a high-level language"
  },
  "time_taken": 1200
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "attempt_id": "770e8400-e29b-41d4-a716-446655440000",
    "score": 85.5,
    "passed": true,
    "total_questions": 10,
    "correct_answers": 9,
    "time_taken": 1200,
    "feedback": [
      {
        "question_id": "q1",
        "correct": true,
        "your_answer": "a",
        "correct_answer": "a",
        "explanation": "Correct! Python is a programming language"
      },
      {
        "question_id": "q2",
        "correct": false,
        "your_answer": "false",
        "correct_answer": "true",
        "explanation": "Python is case-sensitive"
      }
    ]
  }
}
```

---

### 6. Get Quiz Attempts History

**Endpoint:** `GET /api/courses/{course_id}/topics/{topic_id}/quiz/attempts`

**Authentication:** Required (Student)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "attempts": [
      {
        "id": "770e8400-e29b-41d4-a716-446655440000",
        "score": 85.5,
        "passed": true,
        "started_at": "2024-03-15T10:00:00Z",
        "completed_at": "2024-03-15T10:20:00Z",
        "time_taken": 1200
      }
    ],
    "best_score": 85.5,
    "attempts_remaining": 2
  }
}
```

---


## Quiz Types & Question Formats

### Supported Question Types

#### 1. Multiple Choice

```typescript
interface MultipleChoiceQuestion {
  id: string;
  question: string;
  type: "multiple_choice";
  options: Array<{
    id: string;
    text: string;
  }>;
  correct_answer: string;  // Option ID
  explanation?: string;
  points: number;
}
```

**Example:**
```json
{
  "id": "q1",
  "question": "Which of the following is a Python web framework?",
  "type": "multiple_choice",
  "options": [
    {"id": "a", "text": "Django"},
    {"id": "b", "text": "React"},
    {"id": "c", "text": "Angular"},
    {"id": "d", "text": "Vue"}
  ],
  "correct_answer": "a",
  "explanation": "Django is a Python web framework. React, Angular, and Vue are JavaScript frameworks.",
  "points": 1.0
}
```

---

#### 2. True/False

```typescript
interface TrueFalseQuestion {
  id: string;
  question: string;
  type: "true_false";
  options: [
    { id: "true", text: "True" },
    { id: "false", text: "False" }
  ];
  correct_answer: "true" | "false";
  explanation?: string;
  points: number;
}
```

**Example:**
```json
{
  "id": "q2",
  "question": "Python supports multiple inheritance",
  "type": "true_false",
  "options": [
    {"id": "true", "text": "True"},
    {"id": "false", "text": "False"}
  ],
  "correct_answer": "true",
  "explanation": "Python supports multiple inheritance, allowing a class to inherit from multiple parent classes.",
  "points": 1.0
}
```

---

#### 3. Short Answer

```typescript
interface ShortAnswerQuestion {
  id: string;
  question: string;
  type: "short_answer";
  correct_answer: string;  // Expected answer or keywords
  explanation?: string;
  points: number;
}
```

**Example:**
```json
{
  "id": "q3",
  "question": "What keyword is used to define a function in Python?",
  "type": "short_answer",
  "correct_answer": "def",
  "explanation": "The 'def' keyword is used to define functions in Python.",
  "points": 2.0
}
```

---


## Frontend Implementation

### React Quiz Builder Component

```typescript
// components/QuizBuilder.tsx
import React, { useState } from 'react';
import axios from 'axios';

interface Question {
  id: string;
  question: string;
  type: 'multiple_choice' | 'true_false' | 'short_answer';
  options?: Array<{ id: string; text: string }>;
  correct_answer: string;
  explanation?: string;
  points: number;
}

interface QuizBuilderProps {
  topicId: string;
  token: string;
  onSave: (quizId: string) => void;
}

export const QuizBuilder: React.FC<QuizBuilderProps> = ({ topicId, token, onSave }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [timeLimit, setTimeLimit] = useState(30);
  const [passingScore, setPassingScore] = useState(70);
  const [maxAttempts, setMaxAttempts] = useState(3);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [saving, setSaving] = useState(false);

  const addQuestion = (type: Question['type']) => {
    const newQuestion: Question = {
      id: `q${Date.now()}`,
      question: '',
      type,
      options: type !== 'short_answer' ? [
        { id: 'a', text: '' },
        { id: 'b', text: '' }
      ] : undefined,
      correct_answer: '',
      explanation: '',
      points: 1.0
    };

    if (type === 'true_false') {
      newQuestion.options = [
        { id: 'true', text: 'True' },
        { id: 'false', text: 'False' }
      ];
    }

    setQuestions([...questions, newQuestion]);
  };

  const updateQuestion = (index: number, updates: Partial<Question>) => {
    const updated = [...questions];
    updated[index] = { ...updated[index], ...updates };
    setQuestions(updated);
  };

  const addOption = (questionIndex: number) => {
    const updated = [...questions];
    const question = updated[questionIndex];
    if (question.options) {
      const nextId = String.fromCharCode(97 + question.options.length); // a, b, c, d...
      question.options.push({ id: nextId, text: '' });
      setQuestions(updated);
    }
  };

  const removeOption = (questionIndex: number, optionIndex: number) => {
    const updated = [...questions];
    const question = updated[questionIndex];
    if (question.options && question.options.length > 2) {
      question.options.splice(optionIndex, 1);
      setQuestions(updated);
    }
  };

  const updateOption = (questionIndex: number, optionIndex: number, text: string) => {
    const updated = [...questions];
    const question = updated[questionIndex];
    if (question.options) {
      question.options[optionIndex].text = text;
      setQuestions(updated);
    }
  };

  const removeQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
  };

  const saveQuiz = async () => {
    if (!title || questions.length === 0) {
      alert('Please provide a title and at least one question');
      return;
    }

    setSaving(true);

    try {
      const response = await axios.post(
        'http://localhost:8000/api/lecturer/quizzes',
        {
          title,
          description,
          topic_id: topicId,
          time_limit: timeLimit,
          passing_score: passingScore,
          max_attempts: maxAttempts,
          questions
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        onSave(response.data.data.id);
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to save quiz');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="quiz-builder">
      <h2>Create Quiz</h2>

      {/* Quiz Settings */}
      <div className="quiz-settings">
        <div className="form-group">
          <label>Quiz Title *</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter quiz title"
          />
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Brief description of the quiz"
            rows={3}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Time Limit (minutes)</label>
            <input
              type="number"
              value={timeLimit}
              onChange={(e) => setTimeLimit(Number(e.target.value))}
              min={1}
            />
          </div>

          <div className="form-group">
            <label>Passing Score (%)</label>
            <input
              type="number"
              value={passingScore}
              onChange={(e) => setPassingScore(Number(e.target.value))}
              min={0}
              max={100}
            />
          </div>

          <div className="form-group">
            <label>Max Attempts</label>
            <input
              type="number"
              value={maxAttempts}
              onChange={(e) => setMaxAttempts(Number(e.target.value))}
              min={1}
            />
          </div>
        </div>
      </div>

      {/* Questions */}
      <div className="questions-section">
        <h3>Questions ({questions.length})</h3>

        {questions.map((question, qIndex) => (
          <div key={question.id} className="question-card">
            <div className="question-header">
              <span>Question {qIndex + 1}</span>
              <button onClick={() => removeQuestion(qIndex)} className="btn-danger">
                Remove
              </button>
            </div>

            <div className="form-group">
              <label>Question Text *</label>
              <textarea
                value={question.question}
                onChange={(e) => updateQuestion(qIndex, { question: e.target.value })}
                placeholder="Enter your question"
                rows={2}
              />
            </div>

            <div className="form-group">
              <label>Question Type</label>
              <select
                value={question.type}
                onChange={(e) => {
                  const newType = e.target.value as Question['type'];
                  updateQuestion(qIndex, { 
                    type: newType,
                    options: newType === 'short_answer' ? undefined : 
                            newType === 'true_false' ? [
                              { id: 'true', text: 'True' },
                              { id: 'false', text: 'False' }
                            ] : [{ id: 'a', text: '' }, { id: 'b', text: '' }]
                  });
                }}
              >
                <option value="multiple_choice">Multiple Choice</option>
                <option value="true_false">True/False</option>
                <option value="short_answer">Short Answer</option>
              </select>
            </div>

            {/* Options for multiple choice and true/false */}
            {question.options && (
              <div className="options-section">
                <label>Options</label>
                {question.options.map((option, oIndex) => (
                  <div key={option.id} className="option-row">
                    <input
                      type="radio"
                      name={`correct-${qIndex}`}
                      checked={question.correct_answer === option.id}
                      onChange={() => updateQuestion(qIndex, { correct_answer: option.id })}
                    />
                    <input
                      type="text"
                      value={option.text}
                      onChange={(e) => updateOption(qIndex, oIndex, e.target.value)}
                      placeholder={`Option ${option.id.toUpperCase()}`}
                      disabled={question.type === 'true_false'}
                    />
                    {question.type === 'multiple_choice' && question.options!.length > 2 && (
                      <button onClick={() => removeOption(qIndex, oIndex)}>×</button>
                    )}
                  </div>
                ))}
                {question.type === 'multiple_choice' && (
                  <button onClick={() => addOption(qIndex)} className="btn-secondary">
                    Add Option
                  </button>
                )}
              </div>
            )}

            {/* Short answer correct answer */}
            {question.type === 'short_answer' && (
              <div className="form-group">
                <label>Correct Answer *</label>
                <input
                  type="text"
                  value={question.correct_answer}
                  onChange={(e) => updateQuestion(qIndex, { correct_answer: e.target.value })}
                  placeholder="Enter the correct answer"
                />
              </div>
            )}

            <div className="form-group">
              <label>Explanation (shown after submission)</label>
              <textarea
                value={question.explanation}
                onChange={(e) => updateQuestion(qIndex, { explanation: e.target.value })}
                placeholder="Explain the correct answer"
                rows={2}
              />
            </div>

            <div className="form-group">
              <label>Points</label>
              <input
                type="number"
                value={question.points}
                onChange={(e) => updateQuestion(qIndex, { points: Number(e.target.value) })}
                min={0.5}
                step={0.5}
              />
            </div>
          </div>
        ))}

        <div className="add-question-buttons">
          <button onClick={() => addQuestion('multiple_choice')} className="btn-primary">
            + Multiple Choice
          </button>
          <button onClick={() => addQuestion('true_false')} className="btn-primary">
            + True/False
          </button>
          <button onClick={() => addQuestion('short_answer')} className="btn-primary">
            + Short Answer
          </button>
        </div>
      </div>

      {/* Save Button */}
      <div className="actions">
        <button onClick={saveQuiz} disabled={saving} className="btn-success">
          {saving ? 'Saving...' : 'Save Quiz'}
        </button>
      </div>
    </div>
  );
};
```

---


### React Quiz Taker Component (Student View)

```typescript
// components/QuizTaker.tsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface QuizTakerProps {
  courseId: string;
  topicId: string;
  token: string;
  onComplete: (score: number) => void;
}

export const QuizTaker: React.FC<QuizTakerProps> = ({ 
  courseId, 
  topicId, 
  token, 
  onComplete 
}) => {
  const [quiz, setQuiz] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [submitting, setSubmitting] = useState(false);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    loadQuiz();
  }, []);

  useEffect(() => {
    if (quiz && quiz.time_limit) {
      setTimeRemaining(quiz.time_limit * 60); // Convert to seconds

      const timer = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            submitQuiz(); // Auto-submit when time runs out
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [quiz]);

  const loadQuiz = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/courses/${courseId}/topics/${topicId}/quiz`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );
      setQuiz(response.data.data);
    } catch (error) {
      console.error('Failed to load quiz:', error);
    }
  };

  const handleAnswerChange = (questionId: string, answer: string) => {
    setAnswers({ ...answers, [questionId]: answer });
  };

  const submitQuiz = async () => {
    if (submitting) return;

    setSubmitting(true);
    const timeTaken = Math.floor((Date.now() - startTime) / 1000);

    try {
      const response = await axios.post(
        `http://localhost:8000/api/courses/${courseId}/topics/${topicId}/quiz/submit`,
        {
          quiz_id: quiz.id,
          answers,
          time_taken: timeTaken
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        onComplete(response.data.data.score);
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit quiz');
      setSubmitting(false);
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getAnsweredCount = (): number => {
    return Object.keys(answers).length;
  };

  if (!quiz) {
    return <div>Loading quiz...</div>;
  }

  return (
    <div className="quiz-taker">
      {/* Quiz Header */}
      <div className="quiz-header">
        <h2>{quiz.title}</h2>
        <p>{quiz.description}</p>
        
        <div className="quiz-info">
          <div className="info-item">
            <span>Questions:</span>
            <strong>{quiz.questions.length}</strong>
          </div>
          <div className="info-item">
            <span>Passing Score:</span>
            <strong>{quiz.passing_score}%</strong>
          </div>
          {quiz.time_limit && (
            <div className="info-item timer">
              <span>Time Remaining:</span>
              <strong className={timeRemaining < 300 ? 'warning' : ''}>
                {formatTime(timeRemaining)}
              </strong>
            </div>
          )}
          <div className="info-item">
            <span>Progress:</span>
            <strong>{getAnsweredCount()} / {quiz.questions.length}</strong>
          </div>
        </div>
      </div>

      {/* Questions */}
      <div className="questions-container">
        {quiz.questions.map((question: any, index: number) => (
          <div key={question.id} className="question-card">
            <div className="question-number">Question {index + 1}</div>
            <div className="question-text">{question.question}</div>
            <div className="question-points">{question.points} point(s)</div>

            {/* Multiple Choice / True False */}
            {question.type !== 'short_answer' && question.options && (
              <div className="options">
                {question.options.map((option: any) => (
                  <label key={option.id} className="option-label">
                    <input
                      type="radio"
                      name={question.id}
                      value={option.id}
                      checked={answers[question.id] === option.id}
                      onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                    />
                    <span>{option.text}</span>
                  </label>
                ))}
              </div>
            )}

            {/* Short Answer */}
            {question.type === 'short_answer' && (
              <div className="short-answer">
                <textarea
                  value={answers[question.id] || ''}
                  onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                  placeholder="Type your answer here..."
                  rows={3}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Submit Button */}
      <div className="quiz-actions">
        <button
          onClick={submitQuiz}
          disabled={submitting || getAnsweredCount() === 0}
          className="btn-primary btn-large"
        >
          {submitting ? 'Submitting...' : 'Submit Quiz'}
        </button>
        <p className="warning-text">
          {getAnsweredCount() < quiz.questions.length && 
            `You have ${quiz.questions.length - getAnsweredCount()} unanswered question(s)`
          }
        </p>
      </div>
    </div>
  );
};
```

---

### Quiz Results Component

```typescript
// components/QuizResults.tsx
import React from 'react';

interface QuizResultsProps {
  results: {
    score: number;
    passed: boolean;
    total_questions: number;
    correct_answers: number;
    time_taken: number;
    feedback: Array<{
      question_id: string;
      correct: boolean;
      your_answer: string;
      correct_answer: string;
      explanation: string;
    }>;
  };
  onRetake?: () => void;
  onContinue?: () => void;
}

export const QuizResults: React.FC<QuizResultsProps> = ({ 
  results, 
  onRetake, 
  onContinue 
}) => {
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="quiz-results">
      {/* Score Summary */}
      <div className={`score-card ${results.passed ? 'passed' : 'failed'}`}>
        <div className="score-circle">
          <div className="score-value">{results.score.toFixed(1)}%</div>
          <div className="score-label">
            {results.passed ? 'Passed!' : 'Not Passed'}
          </div>
        </div>

        <div className="score-details">
          <div className="detail-item">
            <span>Correct Answers:</span>
            <strong>{results.correct_answers} / {results.total_questions}</strong>
          </div>
          <div className="detail-item">
            <span>Time Taken:</span>
            <strong>{formatTime(results.time_taken)}</strong>
          </div>
        </div>
      </div>

      {/* Question Feedback */}
      <div className="feedback-section">
        <h3>Question Review</h3>
        {results.feedback.map((item, index) => (
          <div key={item.question_id} className={`feedback-card ${item.correct ? 'correct' : 'incorrect'}`}>
            <div className="feedback-header">
              <span className="question-number">Question {index + 1}</span>
              <span className={`status-badge ${item.correct ? 'correct' : 'incorrect'}`}>
                {item.correct ? '✓ Correct' : '✗ Incorrect'}
              </span>
            </div>

            <div className="feedback-content">
              <div className="answer-comparison">
                <div className="your-answer">
                  <label>Your Answer:</label>
                  <span className={item.correct ? 'correct' : 'incorrect'}>
                    {item.your_answer}
                  </span>
                </div>
                {!item.correct && (
                  <div className="correct-answer">
                    <label>Correct Answer:</label>
                    <span className="correct">{item.correct_answer}</span>
                  </div>
                )}
              </div>

              {item.explanation && (
                <div className="explanation">
                  <label>Explanation:</label>
                  <p>{item.explanation}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="results-actions">
        {!results.passed && onRetake && (
          <button onClick={onRetake} className="btn-secondary">
            Retake Quiz
          </button>
        )}
        {onContinue && (
          <button onClick={onContinue} className="btn-primary">
            Continue Learning
          </button>
        )}
      </div>
    </div>
  );
};
```

---


### Vue.js Quiz Builder Component

```vue
<template>
  <div class="quiz-builder">
    <h2>Create Quiz</h2>

    <!-- Quiz Settings -->
    <div class="quiz-settings">
      <div class="form-group">
        <label>Quiz Title *</label>
        <input v-model="quizData.title" placeholder="Enter quiz title" />
      </div>

      <div class="form-group">
        <label>Description</label>
        <textarea v-model="quizData.description" rows="3" />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Time Limit (min)</label>
          <input v-model.number="quizData.time_limit" type="number" min="1" />
        </div>
        <div class="form-group">
          <label>Passing Score (%)</label>
          <input v-model.number="quizData.passing_score" type="number" min="0" max="100" />
        </div>
        <div class="form-group">
          <label>Max Attempts</label>
          <input v-model.number="quizData.max_attempts" type="number" min="1" />
        </div>
      </div>
    </div>

    <!-- Questions -->
    <div class="questions-section">
      <h3>Questions ({{ questions.length }})</h3>

      <div v-for="(question, qIndex) in questions" :key="question.id" class="question-card">
        <div class="question-header">
          <span>Question {{ qIndex + 1 }}</span>
          <button @click="removeQuestion(qIndex)" class="btn-danger">Remove</button>
        </div>

        <div class="form-group">
          <label>Question Text *</label>
          <textarea v-model="question.question" rows="2" />
        </div>

        <div class="form-group">
          <label>Type</label>
          <select v-model="question.type" @change="handleTypeChange(qIndex)">
            <option value="multiple_choice">Multiple Choice</option>
            <option value="true_false">True/False</option>
            <option value="short_answer">Short Answer</option>
          </select>
        </div>

        <!-- Options -->
        <div v-if="question.options" class="options-section">
          <label>Options</label>
          <div v-for="(option, oIndex) in question.options" :key="option.id" class="option-row">
            <input
              type="radio"
              :name="`correct-${qIndex}`"
              :value="option.id"
              v-model="question.correct_answer"
            />
            <input
              v-model="option.text"
              :placeholder="`Option ${option.id.toUpperCase()}`"
              :disabled="question.type === 'true_false'"
            />
            <button
              v-if="question.type === 'multiple_choice' && question.options.length > 2"
              @click="removeOption(qIndex, oIndex)"
            >
              ×
            </button>
          </div>
          <button
            v-if="question.type === 'multiple_choice'"
            @click="addOption(qIndex)"
            class="btn-secondary"
          >
            Add Option
          </button>
        </div>

        <!-- Short Answer -->
        <div v-if="question.type === 'short_answer'" class="form-group">
          <label>Correct Answer *</label>
          <input v-model="question.correct_answer" placeholder="Enter correct answer" />
        </div>

        <div class="form-group">
          <label>Explanation</label>
          <textarea v-model="question.explanation" rows="2" />
        </div>

        <div class="form-group">
          <label>Points</label>
          <input v-model.number="question.points" type="number" min="0.5" step="0.5" />
        </div>
      </div>

      <div class="add-question-buttons">
        <button @click="addQuestion('multiple_choice')" class="btn-primary">
          + Multiple Choice
        </button>
        <button @click="addQuestion('true_false')" class="btn-primary">
          + True/False
        </button>
        <button @click="addQuestion('short_answer')" class="btn-primary">
          + Short Answer
        </button>
      </div>
    </div>

    <!-- Save -->
    <div class="actions">
      <button @click="saveQuiz" :disabled="saving" class="btn-success">
        {{ saving ? 'Saving...' : 'Save Quiz' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';

const props = defineProps<{
  topicId: string;
  token: string;
}>();

const emit = defineEmits<{
  saved: [quizId: string];
}>();

const quizData = ref({
  title: '',
  description: '',
  time_limit: 30,
  passing_score: 70,
  max_attempts: 3
});

const questions = ref<any[]>([]);
const saving = ref(false);

const addQuestion = (type: string) => {
  const newQuestion: any = {
    id: `q${Date.now()}`,
    question: '',
    type,
    correct_answer: '',
    explanation: '',
    points: 1.0
  };

  if (type === 'multiple_choice') {
    newQuestion.options = [
      { id: 'a', text: '' },
      { id: 'b', text: '' }
    ];
  } else if (type === 'true_false') {
    newQuestion.options = [
      { id: 'true', text: 'True' },
      { id: 'false', text: 'False' }
    ];
  }

  questions.value.push(newQuestion);
};

const removeQuestion = (index: number) => {
  questions.value.splice(index, 1);
};

const handleTypeChange = (index: number) => {
  const question = questions.value[index];
  if (question.type === 'short_answer') {
    delete question.options;
  } else if (question.type === 'true_false') {
    question.options = [
      { id: 'true', text: 'True' },
      { id: 'false', text: 'False' }
    ];
  } else if (question.type === 'multiple_choice' && !question.options) {
    question.options = [
      { id: 'a', text: '' },
      { id: 'b', text: '' }
    ];
  }
};

const addOption = (questionIndex: number) => {
  const question = questions.value[questionIndex];
  if (question.options) {
    const nextId = String.fromCharCode(97 + question.options.length);
    question.options.push({ id: nextId, text: '' });
  }
};

const removeOption = (questionIndex: number, optionIndex: number) => {
  const question = questions.value[questionIndex];
  if (question.options && question.options.length > 2) {
    question.options.splice(optionIndex, 1);
  }
};

const saveQuiz = async () => {
  if (!quizData.value.title || questions.value.length === 0) {
    alert('Please provide a title and at least one question');
    return;
  }

  saving.value = true;

  try {
    const response = await axios.post(
      'http://localhost:8000/api/lecturer/quizzes',
      {
        ...quizData.value,
        topic_id: props.topicId,
        questions: questions.value
      },
      {
        headers: {
          'Authorization': `Bearer ${props.token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (response.data.success) {
      emit('saved', response.data.data.id);
    }
  } catch (error: any) {
    alert(error.response?.data?.detail || 'Failed to save quiz');
  } finally {
    saving.value = false;
  }
};
</script>

<style scoped>
.quiz-builder {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.quiz-settings {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.question-card {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.question-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  font-weight: bold;
}

.options-section {
  margin: 1rem 0;
}

.option-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  align-items: center;
}

.option-row input[type="text"] {
  flex: 1;
}

.add-question-buttons {
  display: flex;
  gap: 1rem;
  margin: 1rem 0;
}

.actions {
  margin-top: 2rem;
  text-align: center;
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1.1rem;
}
</style>
```

---


## Student Quiz Taking Flow

### Complete User Journey

```
1. Student navigates to topic
   ↓
2. System checks if quiz exists for topic
   ↓
3. Display quiz information (title, time limit, attempts remaining)
   ↓
4. Student clicks "Start Quiz"
   ↓
5. Timer starts (if time limit set)
   ↓
6. Student answers questions
   ↓
7. Student submits quiz OR time runs out (auto-submit)
   ↓
8. Backend grades quiz
   ↓
9. Display results with feedback
   ↓
10. Update progress tracking
```

### Implementation Example

```typescript
// pages/TopicView.tsx
import React, { useState, useEffect } from 'react';
import { QuizTaker } from '../components/QuizTaker';
import { QuizResults } from '../components/QuizResults';

export const TopicView: React.FC = () => {
  const [quizState, setQuizState] = useState<'not_started' | 'in_progress' | 'completed'>('not_started');
  const [quizResults, setQuizResults] = useState<any>(null);
  const [quizInfo, setQuizInfo] = useState<any>(null);

  useEffect(() => {
    checkQuizAvailability();
  }, []);

  const checkQuizAvailability = async () => {
    // Check if quiz exists and get attempt info
    try {
      const response = await axios.get(
        `/api/courses/${courseId}/topics/${topicId}/quiz/info`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      setQuizInfo(response.data.data);
    } catch (error) {
      // No quiz available
      setQuizInfo(null);
    }
  };

  const startQuiz = () => {
    setQuizState('in_progress');
  };

  const handleQuizComplete = (results: any) => {
    setQuizResults(results);
    setQuizState('completed');
  };

  const handleRetake = () => {
    if (quizInfo.attempts_remaining > 0) {
      setQuizState('in_progress');
      setQuizResults(null);
    }
  };

  return (
    <div className="topic-view">
      {/* Topic Content */}
      <div className="topic-content">
        <h1>{topic.title}</h1>
        <div dangerouslySetInnerHTML={{ __html: topic.content }} />
      </div>

      {/* Quiz Section */}
      {quizInfo && (
        <div className="quiz-section">
          {quizState === 'not_started' && (
            <div className="quiz-intro">
              <h3>📝 Quiz: {quizInfo.title}</h3>
              <p>{quizInfo.description}</p>
              <div className="quiz-details">
                <p>⏱️ Time Limit: {quizInfo.time_limit} minutes</p>
                <p>📊 Passing Score: {quizInfo.passing_score}%</p>
                <p>🔄 Attempts Remaining: {quizInfo.attempts_remaining}</p>
              </div>
              <button onClick={startQuiz} className="btn-primary">
                Start Quiz
              </button>
            </div>
          )}

          {quizState === 'in_progress' && (
            <QuizTaker
              courseId={courseId}
              topicId={topicId}
              token={token}
              onComplete={handleQuizComplete}
            />
          )}

          {quizState === 'completed' && quizResults && (
            <QuizResults
              results={quizResults}
              onRetake={quizInfo.attempts_remaining > 0 ? handleRetake : undefined}
              onContinue={() => navigateToNextTopic()}
            />
          )}
        </div>
      )}
    </div>
  );
};
```

---

## Grading & Scoring

### Automatic Grading Logic

```python
# Backend grading service
def grade_quiz(quiz: Quiz, answers: Dict[str, str]) -> Dict[str, Any]:
    """
    Grade a quiz attempt
    
    Args:
        quiz: Quiz object with questions
        answers: Dictionary of question_id -> answer
        
    Returns:
        Grading results with score and feedback
    """
    total_points = sum(q['points'] for q in quiz.questions)
    earned_points = 0
    feedback = []
    
    for question in quiz.questions:
        question_id = question['id']
        user_answer = answers.get(question_id, '')
        correct_answer = question['correct_answer']
        
        # Grade based on question type
        if question['type'] in ['multiple_choice', 'true_false']:
            is_correct = user_answer.lower() == correct_answer.lower()
        elif question['type'] == 'short_answer':
            # Case-insensitive, trimmed comparison
            is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        else:
            is_correct = False
        
        if is_correct:
            earned_points += question['points']
        
        feedback.append({
            'question_id': question_id,
            'correct': is_correct,
            'your_answer': user_answer,
            'correct_answer': correct_answer,
            'explanation': question.get('explanation', '')
        })
    
    score = (earned_points / total_points * 100) if total_points > 0 else 0
    passed = score >= quiz.passing_score
    
    return {
        'score': round(score, 2),
        'passed': passed,
        'total_questions': len(quiz.questions),
        'correct_answers': sum(1 for f in feedback if f['correct']),
        'feedback': feedback
    }
```

### Advanced Grading Features

#### Partial Credit (Future Enhancement)

```python
def grade_with_partial_credit(question, user_answer, correct_answer):
    """
    Award partial credit for close answers
    """
    if question['type'] == 'short_answer':
        # Use fuzzy matching
        from difflib import SequenceMatcher
        similarity = SequenceMatcher(None, 
                                    user_answer.lower(), 
                                    correct_answer.lower()).ratio()
        
        if similarity >= 0.9:
            return 1.0  # Full credit
        elif similarity >= 0.7:
            return 0.5  # Half credit
        else:
            return 0.0  # No credit
    
    return 1.0 if user_answer == correct_answer else 0.0
```

---

## Best Practices

### For Lecturers

1. **Question Design**
   - Write clear, unambiguous questions
   - Avoid trick questions
   - Provide helpful explanations
   - Balance difficulty levels

2. **Quiz Configuration**
   - Set reasonable time limits (1-2 minutes per question)
   - Allow multiple attempts for learning
   - Set passing score at 70-80%
   - Include 5-15 questions per quiz

3. **Feedback**
   - Always provide explanations for correct answers
   - Explain why wrong answers are incorrect
   - Link to relevant course materials

### For Students

1. **Preparation**
   - Review topic content thoroughly
   - Take notes on key concepts
   - Practice with similar questions

2. **During Quiz**
   - Read questions carefully
   - Manage time wisely
   - Answer all questions
   - Review before submitting

3. **After Quiz**
   - Review feedback carefully
   - Understand mistakes
   - Revisit topic content if needed

### For Developers

1. **Security**
   - Never send correct answers to frontend before submission
   - Validate all inputs on backend
   - Prevent quiz tampering
   - Rate limit submissions

2. **Performance**
   - Cache quiz data
   - Optimize database queries
   - Handle concurrent submissions
   - Implement proper indexing

3. **User Experience**
   - Auto-save progress
   - Show clear time warnings
   - Provide progress indicators
   - Handle network errors gracefully

---

## CSS Styling Examples

```css
/* quiz-builder.css */
.quiz-builder {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.quiz-settings {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.question-card {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e9ecef;
}

.option-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  align-items: center;
}

.option-row input[type="radio"] {
  width: 20px;
  height: 20px;
}

.option-row input[type="text"] {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

/* quiz-taker.css */
.quiz-taker {
  max-width: 800px;
  margin: 0 auto;
}

.quiz-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.quiz-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.info-item {
  background: rgba(255,255,255,0.1);
  padding: 0.75rem;
  border-radius: 4px;
}

.timer.warning {
  background: #dc3545;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.questions-container {
  margin-bottom: 2rem;
}

.question-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.question-number {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.question-text {
  font-size: 1.125rem;
  font-weight: 500;
  margin-bottom: 1rem;
  color: #212529;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option-label {
  display: flex;
  align-items: center;
  padding: 1rem;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-label:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

.option-label input[type="radio"] {
  margin-right: 0.75rem;
  width: 20px;
  height: 20px;
}

/* quiz-results.css */
.quiz-results {
  max-width: 800px;
  margin: 0 auto;
}

.score-card {
  text-align: center;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
}

.score-card.passed {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
}

.score-card.failed {
  background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
  color: white;
}

.score-circle {
  display: inline-block;
  padding: 2rem;
}

.score-value {
  font-size: 3rem;
  font-weight: bold;
}

.score-label {
  font-size: 1.25rem;
  margin-top: 0.5rem;
}

.feedback-card {
  background: white;
  border-left: 4px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.feedback-card.correct {
  border-left-color: #28a745;
  background: #f8fff9;
}

.feedback-card.incorrect {
  border-left-color: #dc3545;
  background: #fff8f8;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-badge.correct {
  background: #28a745;
  color: white;
}

.status-badge.incorrect {
  background: #dc3545;
  color: white;
}

.explanation {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  font-style: italic;
}
```

---

## Complete Integration Example

```typescript
// CourseBuilder.tsx - Integrating quiz builder into course creation
import React, { useState } from 'react';
import { QuizBuilder } from './QuizBuilder';

export const CourseBuilder: React.FC = () => {
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [showQuizBuilder, setShowQuizBuilder] = useState(false);

  const handleAddQuiz = (topicId: string) => {
    setSelectedTopic(topicId);
    setShowQuizBuilder(true);
  };

  const handleQuizSaved = (quizId: string) => {
    console.log('Quiz saved:', quizId);
    setShowQuizBuilder(false);
    // Refresh topic data
  };

  return (
    <div className="course-builder">
      {/* Course structure */}
      <div className="course-structure">
        {modules.map(module => (
          <div key={module.id} className="module">
            <h3>{module.title}</h3>
            {module.topics.map(topic => (
              <div key={topic.id} className="topic">
                <span>{topic.title}</span>
                <button onClick={() => handleAddQuiz(topic.id)}>
                  {topic.has_quiz ? 'Edit Quiz' : 'Add Quiz'}
                </button>
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Quiz Builder Modal */}
      {showQuizBuilder && selectedTopic && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button onClick={() => setShowQuizBuilder(false)} className="close-btn">
              ×
            </button>
            <QuizBuilder
              topicId={selectedTopic}
              token={token}
              onSave={handleQuizSaved}
            />
          </div>
        </div>
      )}
    </div>
  );
};
```

---

## Summary

This guide provides everything needed to implement quizzes in the ALIA platform:

- ✅ Database schema and models
- ✅ Backend API endpoints
- ✅ Frontend components (React & Vue)
- ✅ Grading logic
- ✅ Student quiz-taking flow
- ✅ Best practices
- ✅ Complete styling

The system supports multiple question types, automatic grading, time limits, multiple attempts, and detailed feedback to enhance the learning experience.
