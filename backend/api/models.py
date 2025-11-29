from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    patient_id: Optional[str] = None
    file_ids: Optional[List[str]] = []


from pydantic import BaseModel
from typing import List


class ChatResponse(BaseModel):
    session_id: str
    messages: List[str]
    needs_human_review: bool = False
    agent_trace: List[str] = []

