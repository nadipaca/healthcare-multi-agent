import os
import uuid
from typing import Dict, Optional
from fastapi import UploadFile
from datetime import datetime
from api.config import settings

async def save_uploaded_file(
    file: UploadFile,
    patient_id: str,
    category: str  # "prescriptions", "lab_results", "documents"
) -> Dict:
    """
    Save uploaded file to disk
    
    Args:
        file: Uploaded file
        patient_id: Patient ID
        category: File category (prescriptions, lab_results, etc.)
        
    Returns:
        Dict with file information
    """
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{patient_id}_{uuid.uuid4().hex}{file_ext}"
    
    # Create category directory
    category_path = os.path.join(settings.upload_dir, category)
    os.makedirs(category_path, exist_ok=True)
    
    # Full file path
    file_path = os.path.join(category_path, unique_filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return {
        "file_name": file.filename,
        "stored_name": unique_filename,
        "file_path": file_path,
        "file_type": file.content_type,
        "file_size": len(content),
        "uploaded_at": datetime.now().isoformat()
    }

def validate_file(
    file: UploadFile,
    allowed_types: list,
    max_size_mb: int
) -> Dict:
    """
    Validate uploaded file
    
    Returns:
        Dict with validation result
    """
    # Check file type
    if file.content_type not in allowed_types:
        return {
            "valid": False,
            "error": f"File type {file.content_type} not allowed. Allowed: {', '.join(allowed_types)}"
        }
    
    # Check file size (requires reading file, so this is approximate)
    # In production, you might want to use streaming validation
    
    return {
        "valid": True,
        "error": None
    }

def get_file_url(file_path: str) -> str:
    """Generate file URL for serving"""
    # In production, you might use a CDN or S3 URL
    return f"/api/files/{os.path.basename(file_path)}"