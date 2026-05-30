from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models.chat import (
    ChatSession,
    ChatMessage,
)


class MemoryService:

    async def get_or_create_session(
        self,
        session_id: str,
    ):

        async with AsyncSessionLocal() as db:

            result = await db.execute(
                select(ChatSession).where(
                    ChatSession.session_id == session_id
                )
            )

            session = result.scalar_one_or_none()

            if session:
                return session

            session = ChatSession(
                session_id=session_id
            )

            db.add(session)

            await db.commit()

            await db.refresh(session)

            return session

    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ):

        async with AsyncSessionLocal() as db:

            result = await db.execute(
                select(ChatSession).where(
                    ChatSession.session_id == session_id
                )
            )

            session = result.scalar_one()

            message = ChatMessage(
                session_db_id=session.id,
                role=role,
                content=content,
            )

            db.add(message)

            await db.commit()

    async def get_history(
        self,
        session_id: str,
        limit: int = 20,
    ):

        async with AsyncSessionLocal() as db:

            result = await db.execute(
                select(ChatSession).where(
                    ChatSession.session_id == session_id
                )
            )

            session = result.scalar_one_or_none()

            if not session:
                return []

            result = await db.execute(
                select(ChatMessage)
                .where(
                    ChatMessage.session_db_id == session.id
                )
                .order_by(ChatMessage.id.asc())
            )

            messages = result.scalars().all()

            return [
                {
                    "role": m.role,
                    "content": m.content,
                }
                for m in messages[-limit:]
            ]