from sqlalchemy import select

from app.db.session import (
    AsyncSessionLocal
)

from app.db.models.chat import (
    ChatSession,
    ChatMessage,
)


class ChatMemoryService:

    async def get_or_create_session(
        self,
        project_id: int,
        session_id: str,
    ):

        async with AsyncSessionLocal() as db:

            result = await db.execute(
                select(ChatSession).where(
                    ChatSession.project_id
                    == project_id,

                    ChatSession.session_id
                    == session_id,
                )
            )

            session = (
                result.scalar_one_or_none()
            )

            if session:
                return session

            session = ChatSession(
                session_id=session_id,
                project_id=project_id,
            )

            db.add(session)

            await db.commit()
            await db.refresh(session)

            return session

    async def save_message(
        self,
        project_id: int,
        session_id: str,
        role: str,
        content: str,
    ):

        async with AsyncSessionLocal() as db:

            result = await db.execute(
                select(ChatSession).where(
                    ChatSession.project_id
                    == project_id,

                    ChatSession.session_id
                    == session_id,
                )
            )

            session = (
                result.scalar_one_or_none()
            )

            if not session:

                session = ChatSession(
                    session_id=session_id,
                    project_id=project_id,
                )

                db.add(session)

                await db.commit()
                await db.refresh(session)

            message = ChatMessage(
                session_db_id=session.id,
                role=role,
                content=content,
            )

            db.add(message)

            await db.commit()

            await db.refresh(message)

            return message

    async def get_history(
        self,
        project_id: int,
        session_id: str,
        limit: int = 20,
    ):

        async with AsyncSessionLocal() as db:

            result = await db.execute(
                select(ChatSession).where(
                    ChatSession.project_id
                    == project_id,

                    ChatSession.session_id
                    == session_id,
                )
            )

            session = (
                result.scalar_one_or_none()
            )

            if not session:
                return []

            result = await db.execute(
                select(ChatMessage)
                .where(
                    ChatMessage.session_db_id
                    == session.id
                )
                .order_by(
                    ChatMessage.id.asc()
                )
            )

            messages = (
                result.scalars().all()
            )

            return [
                {
                    "role": m.role,
                    "content": m.content,
                }
                for m in messages[-limit:]
            ]

    async def get_recent_messages(
        self,
        project_id: int,
        session_id: str,
        limit: int = 8,
    ):

        history = await self.get_history(
            project_id=project_id,
            session_id=session_id,
            limit=limit,
        )

        return history