"""
File management API routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.orm import Session
from typing import Optional, Literal
from app.database import get_db
from app.schemas.file import FileUploadResponse, FileResponse, FileListResponse
from app.services.file_service import FileService
from app.core.security import get_current_user
from app.models.user import User
from app.config import get_settings
import uuid
import os

settings = get_settings()

router = APIRouter(prefix="/api/files", tags=["File Management"])


@router.post("/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    context: str = Form('general'),
    file_type: Optional[str] = Form(None),
    course_id: Optional[str] = Form(None),
    module_id: Optional[str] = Form(None),
    topic_id: Optional[str] = Form(None),
    alt_text: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload file with context (course/module/topic)"""
    
    # Validate context
    valid_contexts = ['course', 'module', 'topic', 'general']
    if context not in valid_contexts:
        raise HTTPException(status_code=400, detail=f"Invalid context. Must be one of: {valid_contexts}")
    
    # Validate UUID formats if provided
    try:
        if course_id:
            uuid.UUID(course_id)
        if module_id:
            uuid.UUID(module_id)
        if topic_id:
            uuid.UUID(topic_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    # Validate file type
    if not FileService.is_allowed_file_type(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Validate file size
    file_content = await file.read()
    if not FileService.is_file_size_valid(len(file_content)):
        raise HTTPException(status_code=400, detail="File size too large")
    
    # Reset file pointer
    await file.seek(0)
    
    try:
        # Save file with context
        db_file = FileService.save_uploaded_file(
            db=db,
            file=file,
            uploaded_by=str(current_user.id),
            context=context,
            course_id=course_id,
            module_id=module_id,
            topic_id=topic_id,
            file_type=file_type,
            alt_text=alt_text,
            description=description
        )
        
        return {
            "success": True,
            "data": {
                "file_id": str(db_file.id),
                "filename": db_file.filename,
                "original_filename": db_file.original_filename,
                "url": f"{settings.base_url}/api/files/download/{db_file.id}",
                "type": db_file.file_type,
                "size": db_file.file_size,
                "context": db_file.context,
                "course_id": str(db_file.course_id) if db_file.course_id else None,
                "module_id": str(db_file.module_id) if db_file.module_id else None,
                "topic_id": str(db_file.topic_id) if db_file.topic_id else None,
                "uploaded_at": db_file.created_at,
                "uploaded_by": str(db_file.uploaded_by)
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=dict)
async def get_files(
    context: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    module_id: Optional[str] = Query(None),
    topic_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get files by context"""
    
    if context:
        # Validate UUID formats if provided
        try:
            if course_id:
                uuid.UUID(course_id)
            if module_id:
                uuid.UUID(module_id)
            if topic_id:
                uuid.UUID(topic_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        files = FileService.get_files_by_context(
            db=db,
            context=context,
            course_id=course_id,
            module_id=module_id,
            topic_id=topic_id,
            uploaded_by=str(current_user.id)
        )
    else:
        # Get all files for the user
        files = FileService.get_files_by_context(
            db=db,
            context='general',
            uploaded_by=str(current_user.id)
        )
    
    return {
        "success": True,
        "data": {
            "files": [
                {
                    **FileResponse.from_orm(f).model_dump(),
                    "url": f"{settings.base_url}/api/files/download/{f.id}"
                }
                for f in files
            ],
            "total": len(files),
            "context": context or 'general',
            "context_id": course_id or module_id or topic_id
        }
    }


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    db: Session = Depends(get_db)
):
    """Download/serve file"""
    
    # Validate UUID format
    try:
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    file_record = FileService.get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Check if file exists on disk
    if not os.path.exists(file_record.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Return file with proper headers
    return FastAPIFileResponse(
        path=file_record.file_path,
        filename=file_record.original_filename,
        media_type=file_record.mime_type or "application/octet-stream"
    )


@router.get("/{file_id}", response_model=dict)
async def get_file_info(
    file_id: str,
    db: Session = Depends(get_db)
):
    """Get file information"""
    
    # Validate UUID format
    try:
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    file_record = FileService.get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "success": True,
        "data": {
            **FileResponse.from_orm(file_record).model_dump(),
            "url": f"{settings.base_url}/api/files/download/{file_record.id}"
        }
    }


@router.put("/{file_id}", response_model=dict)
async def update_file_metadata(
    file_id: str,
    alt_text: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update file metadata"""
    
    # Validate UUID format
    try:
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    updated_file = FileService.update_file_metadata(
        db=db,
        file_id=file_id,
        user_id=str(current_user.id),
        alt_text=alt_text,
        description=description
    )
    
    if not updated_file:
        raise HTTPException(status_code=404, detail="File not found or access denied")
    
    return {
        "success": True,
        "data": FileResponse.from_orm(updated_file)
    }


@router.delete("/{file_id}", response_model=dict)
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete file"""
    
    # Validate UUID format
    try:
        uuid.UUID(file_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file ID format")
    
    success = FileService.delete_file(db, file_id, str(current_user.id))
    if not success:
        raise HTTPException(status_code=404, detail="File not found or access denied")
    
    return {
        "success": True,
        "message": "File deleted successfully"
    }


@router.get("/stats/{context}/{context_id}", response_model=dict)
async def get_file_stats(
    context: str,
    context_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file statistics for a specific context"""
    
    # Validate context
    valid_contexts = ['course', 'module', 'topic']
    if context not in valid_contexts:
        raise HTTPException(status_code=400, detail=f"Invalid context. Must be one of: {valid_contexts}")
    
    # Validate UUID format
    try:
        uuid.UUID(context_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid context ID format")
    
    stats = FileService.get_file_stats_by_context(db, context, context_id)
    
    return {
        "success": True,
        "data": stats
    }