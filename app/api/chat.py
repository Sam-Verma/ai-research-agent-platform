from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
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


@router.get("/history")
async def get_history(
    project_id: int,
    session_id: str = "default-session",
    memory_service = Depends(get_chat_memory_service)
):
    history = await memory_service.get_history(project_id, session_id, limit=50)
    return {"messages": history}


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
    generator = await agent_service.execute(
        project_id=request.project_id,
        session_id=request.session_id,
        question=request.question,
        stream=True,
    )
    return StreamingResponse(
        generator,
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


@router.get("/sessions")
async def get_sessions(
    project_id: int,
    memory_service = Depends(get_chat_memory_service),
):
    sessions = await memory_service.list_sessions(project_id)
    return {"sessions": sessions}


@router.delete("/sessions")
async def delete_session(
    project_id: int,
    session_id: str,
    memory_service = Depends(get_chat_memory_service),
):
    deleted = await memory_service.delete_session(project_id, session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}