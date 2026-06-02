from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.responses import StreamingResponse

from app.schemas.chat import (
    ChatRequest
)

from app.services.agent_service import ChatAgentService
from app.api.dependencies import (
    get_llm_service,
    get_chat_memory_service,
    get_embedding_service,
    get_qdrant_service,
    get_workflow_service,
)

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


def get_chat_agent_service(
    llm_service = Depends(get_llm_service),
    memory_service = Depends(get_chat_memory_service),
    embedding_service = Depends(get_embedding_service),
    qdrant_service = Depends(get_qdrant_service),
) -> ChatAgentService:
    return ChatAgentService(
        llm_service=llm_service,
        chat_memory_service=memory_service,
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
    )


@router.post("/")
async def chat(
    request: ChatRequest,
    agent_service: ChatAgentService = Depends(get_chat_agent_service),
):
    return await agent_service.execute(
        project_id=request.project_id,
        session_id=request.session_id,
        question=request.question,
        stream=False,
    )


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    agent_service: ChatAgentService = Depends(get_chat_agent_service),
):
    return StreamingResponse(
        agent_service.execute(
            project_id=request.project_id,
            session_id=request.session_id,
            question=request.question,
            stream=True,
        ),
        media_type="text/event-stream",
    )


@router.post("/research")
async def research_chat(
    request: ChatRequest,
    workflow_service = Depends(get_workflow_service),
):
    return await workflow_service.execute(
        project_id=request.project_id,
        session_id=request.session_id,
        question=request.question,
    )