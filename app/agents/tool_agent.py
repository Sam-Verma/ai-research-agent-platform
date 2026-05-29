from app.services.llm_service import LLMService
from app.tools.retrieval_tool import search_documents


llm_service = LLMService()


async def tool_agent(question: str):

    retrieval_context = search_documents(
        question
    )

    messages = [
        {
            "role": "system",
            "content": f"""
            You are an AI research agent.

            Use the provided retrieved context
            to answer accurately.

            Retrieved Context:
            {retrieval_context}
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
        "answer": response,
        "retrieved_context": retrieval_context,
    }