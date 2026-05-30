from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.chat import ChatRequest
from app.agents.tool_agent import tool_agent

router = APIRouter(
    prefix="/tool-agent",
    tags=["tool-agent"]
)


class ToolAgentRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask(request: ChatRequest):
    
    return await tool_agent(
        project_id=request.project_id,
        session_id=request.session_id,
        question=request.question,
    )