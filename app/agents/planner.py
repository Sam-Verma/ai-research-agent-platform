from app.services.llm_service import LLMService


llm_service = LLMService()


async def planner_node(state):

    question = state["question"]

    messages = [
        {
            "role": "system",
            "content": """
            You are a planning agent.

            Create a concise research plan
            for answering the user question.
            """
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response = await llm_service.generate(
        messages=messages
    )

    return {
        "plan": response
    }