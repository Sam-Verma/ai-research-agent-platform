from pydantic import BaseModel
from fastapi import APIRouter

from app.rag.retrieval import RetrievalService

router = APIRouter(
    prefix="/rag",
    tags=["rag"]
)

retrieval_service = RetrievalService()


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(
    request: QuestionRequest
):

    result = await retrieval_service.ask(
        request.question
    )

    return result