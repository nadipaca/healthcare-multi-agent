from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    messages: List[str]
