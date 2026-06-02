from fastapi import (
    APIRouter
)

from fastapi.responses import (
    StreamingResponse
)

from app.schemas.chat import (
    ChatRequest
)

from app.agents.stream_tool_agent import (
    stream_tool_agent
)

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("/stream")
async def stream_chat(
    request: ChatRequest
):

    return StreamingResponse(
        stream_tool_agent(
            project_id=request.project_id,
            session_id=request.session_id,
            question=request.question,
        ),
        media_type=(
            "text/event-stream"
        ),
    )