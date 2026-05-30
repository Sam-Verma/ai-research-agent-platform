import json

from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService

from app.tools.retrieval_tool import (
    search_documents,
    retrieval_tool_definition,
)

from app.tools.web_search_tool import (
    web_search,
    web_search_tool_definition,
)

memory_service = MemoryService()
llm_service = LLMService()

TOOLS = [
    retrieval_tool_definition,
    web_search_tool_definition,
]


async def tool_agent(
    project_id: str,
    session_id: str,
    question: str,
):

    await memory_service.get_or_create_session(
        project_id,
        session_id,
    )

    history = await memory_service.get_history(
        project_id,
        session_id,
    )

    await memory_service.save_message(
        project_id=project_id,
        session_id=session_id,
        role="user",
        content=question,
    )

    messages = [
        {
            "role": "system",
            "content": """
            You are an AI research assistant.

            Use tools when necessary.
            """
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

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
                    "content": str(tool_result),
                }
            )

            final_response = await (
                llm_service.client.chat.completions.create(
                    model=llm_service.model,
                    messages=messages,
                )
            )

            final_answer = (
                final_response
                .choices[0]
                .message
                .content
            )

            await memory_service.save_message(
                project_id=project_id,
                session_id=session_id,
                role="assistant",
                content=final_answer,
            )

            return {
                "answer": final_answer,
                "tool_used": function_name,
            }

        elif function_name == "web_search":

            tool_result = web_search(
                query=arguments["query"]
            )

            messages.append(message)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result),
                }
            )

            final_response = await (
                llm_service.client.chat.completions.create(
                    model=llm_service.model,
                    messages=messages,
                )
            )

            final_answer = (
                final_response
                .choices[0]
                .message
                .content
            )

            await memory_service.save_message(
                project_id=project_id,
                session_id=session_id,
                role="assistant",
                content=final_answer,
            )

            return {
                "answer": final_answer,
                "tool_used": function_name,
            }

    await memory_service.save_message(
        project_id=project_id,
        session_id=session_id,
        role="assistant",
        content=message.content,
    )

    return {
        "answer": message.content,
        "tool_used": None,
    }