from fastapi import APIRouter
from pydantic import BaseModel

from app.services.llm_service import LLMService
from app.prompts.research import RESEARCH_PROMPT

router = APIRouter(
    prefix="/llm",
    tags=["llm"]
)

llm_service = LLMService()


class GenerateRequest(BaseModel):
    topic: str


@router.post("/generate")
async def generate_text(request: GenerateRequest):

    prompt = RESEARCH_PROMPT.format_messages(
        topic=request.topic
    )

    response = await llm_service.generate(
        messages=prompt
    )

    return {
        "response": response
    }