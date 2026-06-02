from app.services.chat_memory_service import (
    ChatMemoryService
)


class MemoryContextService:

    def __init__(self):

        self.memory_service = (
            ChatMemoryService()
        )

    async def get_recent_messages(
        self,
        project_id: int,
        session_id: str,
        limit: int = 8,
    ):

        return (
            await self.memory_service
            .get_recent_messages(
                project_id=project_id,
                session_id=session_id,
                limit=limit,
            )
        )