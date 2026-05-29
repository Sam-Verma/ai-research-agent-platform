from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.tool_agent import tool_agent

router = APIRouter(
    prefix="/tool-agent",
    tags=["tool-agent"]
)


class ToolAgentRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask_tool_agent(
    request: ToolAgentRequest
):

    result = await tool_agent(
        request.question
    )

    return result