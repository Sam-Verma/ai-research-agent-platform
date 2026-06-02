import json

from app.services.llm_service import (
    LLMService
)

from app.services.chat_memory_service import (
    ChatMemoryService
)

from app.tools.retrieval_tool import (
    search_documents,
)

from app.tools.web_search_tool import (
    web_search,
)

from app.agents.tool_agent import (
    TOOLS
)

memory_service = (
    ChatMemoryService()
)

llm_service = (
    LLMService()
)


async def stream_tool_agent(
    project_id: int,
    session_id: str,
    question: str,
):

    await memory_service.get_or_create_session(
        project_id=project_id,
        session_id=session_id,
    )

    history = await (
        memory_service.get_history(
            project_id=project_id,
            session_id=session_id,
        )
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
You are an advanced AI research assistant.

Use project documents first.

Use web search for
recent or missing information.

Use multiple tools
when necessary.

Never hallucinate.
            """.strip()
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

    message = (
        response.choices[0].message
    )

    if message.tool_calls:

        messages.append(message)

        for tool_call in (
            message.tool_calls
        ):

            function_name = (
                tool_call.function.name
            )

            arguments = json.loads(
                tool_call.function.arguments
            )

            tool_result = None

            if (
                function_name
                == "search_documents"
            ):

                tool_result = (
                    search_documents(
                        query=arguments.get(
                            "query"
                        ),
                        project_id=project_id,
                    )
                )

            elif (
                function_name
                == "web_search"
            ):

                tool_result = (
                    web_search(
                        query=arguments.get(
                            "query"
                        )
                    )
                )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id":
                        tool_call.id,

                    "content":
                        str(tool_result),
                }
            )

    full_response = ""

    async for token in (
        llm_service.stream_generate(
            messages=messages,
            temperature=0.3,
        )
    ):

        full_response += token

        yield (
            f"data: {token}\n\n"
        )

    await memory_service.save_message(
        project_id=project_id,
        session_id=session_id,
        role="assistant",
        content=full_response,
    )

    yield "data: [DONE]\n\n"