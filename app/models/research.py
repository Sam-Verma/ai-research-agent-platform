from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

class ResearchProject(Base):
    __tablename__ = "research_projects"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(255))

    query: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending"
    )

    chat_sessions = relationship(
        "ChatSession",
        back_populates="project"
    )