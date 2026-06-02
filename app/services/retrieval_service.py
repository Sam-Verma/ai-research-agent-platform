from app.services.llm_service import (
    LLMService
)

from app.services.context.context_builder import (
    ContextBuilder
)

from app.services.context.prompt_builder import (
    PromptBuilder
)

from app.services.chat_memory_service import (
    ChatMemoryService
)


class RetrievalService:

    def __init__(self):

        self.llm_service = (
            LLMService()
        )

        self.context_builder = (
            ContextBuilder()
        )

        self.chat_memory = (
            ChatMemoryService()
        )

    async def ask(
        self,
        project_id: int,
        session_id: str,
        question: str,
    ):

        await self.chat_memory.save_message(
            project_id=project_id,
            session_id=session_id,
            role="user",
            content=question,
        )

        context = (
            await self.context_builder.build(
                project_id=project_id,
                session_id=session_id,
                query=question,
            )
        )

        messages = (
            PromptBuilder.build(
                question=question,
                context=context,
            )
        )

        response = (
            await self.llm_service.generate(
                messages=messages,
                temperature=0.3,
            )
        )

        await self.chat_memory.save_message(
            project_id=project_id,
            session_id=session_id,
            role="assistant",
            content=response,
        )

        return {
            "answer": response,

            "memory_used":
                len(context.memory),

            "sources_found":
                len(context.documents),

            "sources": list(
                set(
                    [
                        doc.source
                        for doc
                        in context.documents
                    ]
                )
            )
        }