import json
from typing import AsyncGenerator, Union, Dict, Any

from app.services.llm_service import LLMService
from app.services.chat_memory_service import ChatMemoryService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService

from app.tools.retrieval_tool import (
    search_documents,
    retrieval_tool_definition,
)
from app.tools.web_search_tool import (
    web_search,
    web_search_tool_definition,
)

from app.tools.scrape_tool import (
    scrape_website,
    scrape_tool_definition,
)

TOOLS = [
    retrieval_tool_definition,
    web_search_tool_definition,
    scrape_tool_definition,
]


class ChatAgentService:
    def __init__(
        self,
        llm_service: LLMService,
        chat_memory_service: ChatMemoryService,
        embedding_service: EmbeddingService,
        qdrant_service: QdrantService,
    ):
        self.llm_service = llm_service
        self.memory_service = chat_memory_service
        self.embedding_service = embedding_service
        self.qdrant_service = qdrant_service

    async def execute(
        self,
        project_id: int,
        session_id: str,
        question: str,
        stream: bool = False,
    ) -> Union[Dict[str, Any], AsyncGenerator[str, None]]:
        
        await self.memory_service.get_or_create_session(
            project_id=project_id,
            session_id=session_id,
        )

        history = await self.memory_service.get_history(
            project_id=project_id,
            session_id=session_id,
        )

        await self.memory_service.save_message(
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

Rules:
- Prefer project documents first.
- Use web search when needed for recent or missing information.
- Use multiple tools if necessary.
- Never hallucinate.
- Be concise but informative.
- Cite retrieved evidence naturally.
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
            self.llm_service.client.chat.completions.create(
                model=self.llm_service.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        )

        message = response.choices[0].message
        tools_used = []

        if message.tool_calls:
            messages.append(message)

            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                tools_used.append(function_name)
                tool_result = None

                if function_name == "search_documents":
                    tool_result = search_documents(
                        query=arguments.get("query"),
                        project_id=project_id,
                        embedding_service=self.embedding_service,
                        qdrant_service=self.qdrant_service,
                    )
                elif function_name == "web_search":
                    tool_result = web_search(
                        query=arguments.get("query")
                    )
                elif function_name == "scrape_website":
                    tool_result = scrape_website(
                        url=arguments.get("url")
                    )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result),
                    }
                )

            if stream:
                return self._stream_response(project_id, session_id, messages)
            else:
                return await self._generate_response(project_id, session_id, messages, tools_used)

        if stream:
            return self._stream_direct_response(project_id, session_id, message.content)
        
        await self.memory_service.save_message(
            project_id=project_id,
            session_id=session_id,
            role="assistant",
            content=message.content,
        )
        return {
            "answer": message.content,
            "tools_used": [],
        }

    async def _stream_response(self, project_id: int, session_id: str, messages: list) -> AsyncGenerator[str, None]:
        full_response = ""
        async for token in self.llm_service.stream_generate(
            messages=messages,
            temperature=0.3,
        ):
            full_response += token
            yield f"data: {token}\n\n"

        await self.memory_service.save_message(
            project_id=project_id,
            session_id=session_id,
            role="assistant",
            content=full_response,
        )
        yield "data: [DONE]\n\n"

    async def _stream_direct_response(self, project_id: int, session_id: str, content: str) -> AsyncGenerator[str, None]:
        await self.memory_service.save_message(
            project_id=project_id,
            session_id=session_id,
            role="assistant",
            content=content,
        )
        # Assuming the token is streamed in one go if there were no tools
        yield f"data: {content}\n\n"
        yield "data: [DONE]\n\n"

    async def _generate_response(self, project_id: int, session_id: str, messages: list, tools_used: list) -> Dict[str, Any]:
        final_response = await (
            self.llm_service.client.chat.completions.create(
                model=self.llm_service.model,
                messages=messages,
                tools=TOOLS,
            )
        )

        message = final_response.choices[0].message
        final_answer = message.content

        # Handle edge case where the model insists on calling another tool
        if not final_answer and message.tool_calls:
            final_answer = f"I tried to use another tool: {message.tool_calls[0].function.name}, but I can only run one step at a time."

        await self.memory_service.save_message(
            project_id=project_id,
            session_id=session_id,
            role="assistant",
            content=final_answer,
        )

        return {
            "answer": final_answer,
            "tools_used": tools_used,
        }
