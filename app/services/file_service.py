"""
File management service
"""
import os
import uuid
from typing import Optional, List, Dict, Any
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.file import File
from app.config import get_settings

settings = get_settings()


class FileService:
    @staticmethod
    def save_uploaded_file(
        db: Session,
        file: UploadFile,
        uploaded_by: str,
        context: str = 'general',
        course_id: Optional[str] = None,
        module_id: Optional[str] = None,
        topic_id: Optional[str] = None,
        file_type: Optional[str] = None,
        alt_text: Optional[str] = None,
        description: Optional[str] = None,
        is_public: bool = False
    ) -> File:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create upload directory if it doesn't exist
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # Save file to disk
        file_path = os.path.join(settings.upload_dir, unique_filename)
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Validate context associations
        if context == 'course' and not course_id:
            raise ValueError("course_id is required for course context")
        elif context == 'module' and not module_id:
            raise ValueError("module_id is required for module context")
        elif context == 'topic' and not topic_id:
            raise ValueError("topic_id is required for topic context")
        
        # Create file record in database
        db_file = File(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_type=file_type or file_extension,
            file_size=len(content),
            mime_type=file.content_type,
            uploaded_by=uploaded_by,
            is_public=is_public,
            context=context,
            course_id=course_id,
            module_id=module_id,
            topic_id=topic_id,
            alt_text=alt_text,
            description=description,
            status='completed'
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file

    @staticmethod
    def get_file_by_id(db: Session, file_id: str) -> Optional[File]:
        return db.query(File).filter(File.id == file_id).first()

    @staticmethod
    def get_files_by_context(
        db: Session,
        context: str,
        course_id: Optional[str] = None,
        module_id: Optional[str] = None,
        topic_id: Optional[str] = None,
        uploaded_by: Optional[str] = None
    ) -> List[File]:
        """Get files by context (course/module/topic)"""
        query = db.query(File).filter(File.context == context)
        
        if context == 'course' and course_id:
            query = query.filter(File.course_id == course_id)
        elif context == 'module' and module_id:
            query = query.filter(File.module_id == module_id)
        elif context == 'topic' and topic_id:
            query = query.filter(File.topic_id == topic_id)
        
        if uploaded_by:
            query = query.filter(File.uploaded_by == uploaded_by)
        
        return query.order_by(File.created_at.desc()).all()

    @staticmethod
    def delete_file(db: Session, file_id: str, user_id: str) -> bool:
        file_record = db.query(File).filter(
            File.id == file_id,
            File.uploaded_by == user_id
        ).first()
        
        if file_record:
            # Delete file from disk
            if os.path.exists(file_record.file_path):
                os.remove(file_record.file_path)
            
            # Delete record from database
            db.delete(file_record)
            db.commit()
            return True
        return False

    @staticmethod
    def update_file_metadata(
        db: Session,
        file_id: str,
        user_id: str,
        alt_text: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[File]:
        """Update file metadata"""
        file_record = db.query(File).filter(
            File.id == file_id,
            File.uploaded_by == user_id
        ).first()
        
        if file_record:
            if alt_text is not None:
                file_record.alt_text = alt_text
            if description is not None:
                file_record.description = description
            
            db.commit()
            db.refresh(file_record)
            return file_record
        return None

    @staticmethod
    def is_allowed_file_type(filename: str) -> bool:
        file_extension = os.path.splitext(filename)[1].lower()
        return file_extension in settings.allowed_file_types

    @staticmethod
    def is_file_size_valid(file_size: int) -> bool:
        return file_size <= settings.max_file_size

    @staticmethod
    def get_file_stats_by_context(db: Session, context: str, context_id: str) -> Dict[str, Any]:
        """Get file statistics for a specific context"""
        query = db.query(File).filter(File.context == context)
        
        if context == 'course':
            query = query.filter(File.course_id == context_id)
        elif context == 'module':
            query = query.filter(File.module_id == context_id)
        elif context == 'topic':
            query = query.filter(File.topic_id == context_id)
        
        files = query.all()
        
        return {
            'total_files': len(files),
            'total_size': sum(f.file_size for f in files),
            'file_types': list(set(f.file_type for f in files)),
            'latest_upload': max((f.created_at for f in files), default=None)
        }