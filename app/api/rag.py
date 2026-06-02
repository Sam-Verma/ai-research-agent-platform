from fastapi import (
    APIRouter,
    Depends
)

from pydantic import (
    BaseModel
)

from app.services.retrieval_service import (
    RetrievalService
)


router = APIRouter(
    prefix="/rag",
    tags=["legacy-rag"]
)

retrieval_service = (
    RetrievalService()
)


class QuestionRequest(
    BaseModel
):
    project_id: int
    session_id: str
    question: str


@router.post("/ask")
async def ask_question(
    request: QuestionRequest
):

    result = (
        await retrieval_service.ask(
            project_id=request.project_id,
            session_id=request.session_id,
            question=request.question,
        )
    )

    return result