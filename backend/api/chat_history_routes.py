from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import db_helper
from api.security import get_current_user

router = APIRouter(prefix="/api/chat", tags=["chat_history"])

class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: str
    last_message_at: str
    message_count: int
    first_message: Optional[str]

class MessageResponse(BaseModel):
    message_id: str
    role: str
    content: str
    timestamp: str
    agent_name: Optional[str]
    needs_human_review: bool

@router.get("/sessions")
async def get_chat_sessions(
    limit: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """Get patient's recent chat sessions"""
    try:
        patient_id = current_user.get("patient_id")
        
        if not patient_id:
            raise HTTPException(status_code=400, detail="Patient ID not found in token")
        
        # Verify patient exists in database
        from database.db_helper import get_patient_by_id
        patient = get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=401, 
                detail="Patient account not found. Please log out and log back in."
            )
        
        sessions = db_helper.get_patient_chat_sessions(patient_id, limit)
        
        return {
            "status": "success",
            "sessions": sessions,
            "count": len(sessions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all messages from a specific session"""
    try:
        patient_id = current_user.get("patient_id")
        
        # Verify session ownership
        conn = db_helper.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT patient_id FROM chat_sessions 
            WHERE session_id = ? AND is_active = 1
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result or result[0] != patient_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this session")
        
        messages = db_helper.get_session_messages(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "messages": messages,
            "count": len(messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete (archive) a chat session"""
    try:
        patient_id = current_user.get("patient_id")
        
        success = db_helper.delete_chat_session(session_id, patient_id)
        
        if not success:
            raise HTTPException(status_code=403, detail="Not authorized or session not found")
        
        return {
            "status": "success",
            "message": "Session deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/create")
async def create_new_session(
    current_user: dict = Depends(get_current_user)
):
    """Create a new chat session"""
    try:
        patient_id = current_user.get("patient_id")
        
        session = db_helper.create_chat_session(patient_id)
        
        return {
            "status": "success",
            "session": session
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))