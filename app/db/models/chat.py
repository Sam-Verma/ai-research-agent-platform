from sqlalchemy import (
    String,
    Text,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base_class import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    session_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    session_db_id: Mapped[int] = mapped_column(
        ForeignKey("chat_sessions.id")
    )

    role: Mapped[str] = mapped_column(
        String(50)
    )

    content: Mapped[str] = mapped_column(
        Text
    )

    session = relationship(
        "ChatSession",
        back_populates="messages",
    )