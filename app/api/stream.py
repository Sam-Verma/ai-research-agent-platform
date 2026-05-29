from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.llm_service import LLMService
from app.prompts.research import RESEARCH_PROMPT


router = APIRouter(
    prefix="/stream",
    tags=["stream"]
)

llm_service = LLMService()


class StreamRequest(BaseModel):
    topic: str


@router.post("/generate")
async def stream_response(
    request: StreamRequest
):

    prompt = RESEARCH_PROMPT.format_messages(
        topic=request.topic
    )

    async def event_generator():

        async for chunk in llm_service.stream_generate(
            messages=prompt
        ):

            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/plain"
    )