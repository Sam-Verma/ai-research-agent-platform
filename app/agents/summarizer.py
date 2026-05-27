from app.services.llm_service import LLMService


llm_service = LLMService()


async def summarizer_node(state):

    research = state["research"]

    messages = [
        {
            "role": "system",
            "content": """
            You are a summarization agent.

            Create a concise final answer.
            """
        },
        {
            "role": "user",
            "content": research
        }
    ]

    response = await llm_service.generate(
        messages=messages
    )

    return {
        "answer": response
    }