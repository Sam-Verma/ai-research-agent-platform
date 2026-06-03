from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    project_id: int
    session_id: str
    question: str
    mode: Optional[str] = None