from fastapi import (
    APIRouter
)

from app.schemas.chat import (
    ChatRequest
)

from app.agents.tool_agent import (
    tool_agent
)

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("/")
async def chat(
    request: ChatRequest
):

    return await tool_agent(
        project_id=request.project_id,
        session_id=request.session_id,
        question=request.question,
    )