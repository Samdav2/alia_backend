from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import get_db
from services import ai_service

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.post("/summarize")
async def summarize(request: schemas.SummarizeRequest):
    summary = await ai_service.summarize_text(request.text)
    return {"summary": summary}

@router.post("/assessment")
async def assessment(request: schemas.AssessmentRequest, db: Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    question = await ai_service.generate_adaptive_question(course.title, request.current_score)
    return {"question": question}
