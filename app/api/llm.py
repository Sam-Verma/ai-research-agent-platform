from fastapi import APIRouter

from app.services.llm_service import LLMService

router = APIRouter(prefix="/llm", tags=["llm"])

llm_service = LLMService()


@router.post("/generate")
async def generate_text():

    response = await llm_service.generate(
        prompt="Explain what an AI agent is in simple terms."
    )

    return {
        "response": response
    }