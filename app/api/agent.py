from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.workflow import graph

router = APIRouter(
    prefix="/agent",
    tags=["agent"]
)


class AgentRequest(BaseModel):
    question: str


@router.post("/research")
async def run_agent_workflow(
    request: AgentRequest
):

    result = await graph.ainvoke(
        {
            "question": request.question
        }
    )

    return result