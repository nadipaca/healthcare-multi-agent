from datetime import datetime
from typing import List, Dict, Any
from .audit import audit_log_event

# Simple in-memory store; replace with Postgres or similar.
SESSION_MESSAGES: Dict[str, List[Dict[str, Any]]] = {}


def store_message(session_id: str, role: str, content: str):
    audit_log_event(
        actor=role,
        action="message",
        session_id=session_id,
        metadata={"length": len(content)},
    )
    SESSION_MESSAGES.setdefault(session_id, []).append(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "role": role,
            "content": content,
        }
    )
