import json

from app.services.llm_service import LLMService

from app.tools.retrieval_tool import (
    search_documents,
    retrieval_tool_definition,
)


llm_service = LLMService()


TOOLS = [
    retrieval_tool_definition
]


async def tool_agent(question: str):

    messages = [
        {
            "role": "system",
            "content": """
            You are an AI research assistant.

            Use tools when necessary.
            """
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response = await (
        llm_service.client.chat.completions.create(
            model=llm_service.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
    )

    message = response.choices[0].message

    if message.tool_calls:

        tool_call = message.tool_calls[0]

        function_name = (
            tool_call.function.name
        )

        arguments = json.loads(
            tool_call.function.arguments
        )

        if function_name == "search_documents":

            tool_result = search_documents(
                query=arguments["query"]
            )

            messages.append(message)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                }
            )

            final_response = await (
                llm_service.client.chat.completions.create(
                    model=llm_service.model,
                    messages=messages,
                )
            )

            return {
                "answer":
                    final_response
                    .choices[0]
                    .message
                    .content,

                "tool_used": function_name,
            }

    return {
        "answer": message.content,
        "tool_used": None,
    }