from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

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
    
    documents = relationship(
        "ProjectDocument",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    
    reports = relationship(
        "ResearchReport",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProjectDocument(Base):
    __tablename__ = "project_documents"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    project_id: Mapped[int] = mapped_column(
        ForeignKey("research_projects.id")
    )
    
    filename: Mapped[str] = mapped_column(String(255))
    
    uploaded_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    project = relationship(
        "ResearchProject",
        back_populates="documents"
    )


class ResearchReport(Base):
    __tablename__ = "research_reports"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    project_id: Mapped[int] = mapped_column(
        ForeignKey("research_projects.id")
    )
    
    title: Mapped[str] = mapped_column(String(255), default="Research Report")
    
    content: Mapped[str] = mapped_column(Text)
    
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    project = relationship(
        "ResearchProject",
        back_populates="reports"
    )