# Quiz System Implementation Checklist

## Backend Implementation

### ✅ Already Implemented

- [x] Database models (Quiz, QuizAttempt)
- [x] Quiz schemas (QuizCreate, QuizUpdate, QuizResponse)
- [x] Lecturer service methods (create_quiz, update_quiz, delete_quiz)
- [x] API endpoints (POST /lecturer/quizzes, PUT /lecturer/quizzes/{id}, DELETE /lecturer/quizzes/{id})

### 🔨 Needs Implementation

#### 1. Student Quiz API Endpoints

Create new file: `app/api/quizzes.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/courses/{course_id}/topics/{topic_id}/quiz", tags=["Quizzes"])

@router.get("/info")
async def get_quiz_info(
    course_id: str,
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz information for a topic (without correct answers)"""
    pass

@router.get("")
async def get_quiz(
    course_id: str,
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz questions (without correct answers)"""
    pass

@router.post("/submit")
async def submit_quiz(
    course_id: str,
    topic_id: str,
    submission: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit quiz answers and get results"""
    pass

@router.get("/attempts")
async def get_attempts(
    course_id: str,
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's quiz attempt history"""
    pass
```

#### 2. Quiz Service

Create: `app/services/quiz_service.py`

```python
class QuizService:
    @staticmethod
    def get_quiz_by_topic(db: Session, topic_id: str):
        """Get active quiz for a topic"""
        pass
    
    @staticmethod
    def get_quiz_for_student(db: Session, topic_id: str, user_id: str):
        """Get quiz without correct answers"""
        pass
    
    @staticmethod
    def submit_quiz_attempt(db: Session, quiz_id: str, user_id: str, answers: dict, time_taken: int):
        """Grade and save quiz attempt"""
        pass
    
    @staticmethod
    def get_user_attempts(db: Session, quiz_id: str, user_id: str):
        """Get user's attempt history"""
        pass
    
    @staticmethod
    def can_attempt_quiz(db: Session, quiz_id: str, user_id: str) -> bool:
        """Check if user can take quiz"""
        pass
```

#### 3. Register Quiz Router

In `app/main.py`:

```python
from app.api import quizzes

app.include_router(quizzes.router)
```

---

## Frontend Implementation

### Required Components

#### 1. QuizBuilder.tsx
- ✅ Create in: `frontend/src/components/QuizBuilder.tsx`
- Features: Add/edit/remove questions, configure settings
- See full implementation in QUIZ_ASSESSMENT_GUIDE.md

#### 2. QuizTaker.tsx
- ✅ Create in: `frontend/src/components/QuizTaker.tsx`
- Features: Display questions, timer, answer selection, submission
- See full implementation in QUIZ_ASSESSMENT_GUIDE.md

#### 3. QuizResults.tsx
- ✅ Create in: `frontend/src/components/QuizResults.tsx`
- Features: Show score, feedback, retry option
- See full implementation in QUIZ_ASSESSMENT_GUIDE.md

#### 4. Integration Points

Update existing components:

**CourseBuilder.tsx:**
```typescript
// Add "Add Quiz" button to each topic
<button onClick={() => openQuizBuilder(topic.id)}>
  {topic.has_quiz ? 'Edit Quiz' : 'Add Quiz'}
</button>
```

**TopicView.tsx:**
```typescript
// Check for quiz and display quiz section
{hasQuiz && (
  <QuizSection topicId={topic.id} />
)}
```

---

## Testing Checklist

### Backend Tests

- [ ] Test quiz creation with valid data
- [ ] Test quiz creation with invalid topic_id
- [ ] Test quiz update by owner
- [ ] Test quiz update by non-owner (should fail)
- [ ] Test quiz deletion
- [ ] Test quiz submission with correct answers
- [ ] Test quiz submission with incorrect answers
- [ ] Test quiz submission exceeding max attempts
- [ ] Test time limit enforcement
- [ ] Test grading logic for all question types

### Frontend Tests

- [ ] Quiz builder renders correctly
- [ ] Can add/remove questions
- [ ] Can add/remove options
- [ ] Form validation works
- [ ] Quiz saves successfully
- [ ] Quiz taker displays questions
- [ ] Timer counts down correctly
- [ ] Auto-submit on time expiry
- [ ] Results display correctly
- [ ] Can retry quiz if attempts remaining

---

## Deployment Steps

1. **Database Migration**
   ```bash
   # Create migration for quiz tables
   alembic revision --autogenerate -m "Add quiz and quiz_attempts tables"
   alembic upgrade head
   ```

2. **Install Dependencies**
   ```bash
   # No new dependencies needed
   ```

3. **Environment Variables**
   ```bash
   # Add to .env if needed
   QUIZ_AUTO_GRADE=true
   QUIZ_SHOW_FEEDBACK=true
   ```

4. **Test Endpoints**
   ```bash
   # Test quiz creation
   curl -X POST http://localhost:8000/api/lecturer/quizzes \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d @test_quiz.json
   ```

5. **Deploy Frontend**
   ```bash
   cd frontend
   npm run build
   npm run deploy
   ```

---

## Quick Start

### For Lecturers

1. Navigate to your course
2. Select a topic
3. Click "Add Quiz"
4. Add questions using the quiz builder
5. Configure time limit and passing score
6. Save quiz
7. Quiz is now available to students

### For Students

1. Navigate to topic with quiz
2. Review quiz information
3. Click "Start Quiz"
4. Answer all questions
5. Submit before time runs out
6. Review results and feedback
7. Retry if needed and attempts remaining

---

## Support & Resources

- Full API documentation: `docs/QUIZ_ASSESSMENT_GUIDE.md`
- Backend code: `app/api/lecturer.py`, `app/services/lecturer_service.py`
- Database models: `app/models/assessment.py`
- Schemas: `app/schemas/assessment.py`
