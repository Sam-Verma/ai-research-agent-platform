import asyncio

from app.schemas.context import (
    UnifiedContext
)

from app.services.context.memory_context import (
    MemoryContextService
)

from app.rag.retrieval import (
    RetrievalService
)


class ContextBuilder:

    def __init__(self):

        self.memory_service = (
            MemoryContextService()
        )

        self.retrieval_service = (
            RetrievalService()
        )

    async def build(
        self,
        project_id: int,
        session_id: str,
        query: str,
    ) -> UnifiedContext:

        memory_task = (
            self.memory_service
            .get_recent_messages(
                project_id=project_id,
                session_id=session_id,
            )
        )

        retrieval_task = (
            self.retrieval_service
            .retrieve(
                project_id=project_id,
                question=query,
            )
        )

        (
            memory,
            documents
        ) = await asyncio.gather(
            memory_task,
            retrieval_task,
        )

        return UnifiedContext(
            memory=memory,
            documents=documents,
        )