from fastapi import APIRouter

from app.services.llm_service import LLMService
from app.prompts.research import RESEARCH_PROMPT

router = APIRouter(
    prefix="/llm",
    tags=["llm"]
)

llm_service = LLMService()


@router.post("/generate")
async def generate_text():

    prompt = RESEARCH_PROMPT.format_messages(
        topic="AI agents"
    )

    response = await llm_service.generate(
        messages=prompt
    )

    return {
        "response": response
    }