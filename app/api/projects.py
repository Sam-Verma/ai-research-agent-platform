from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.research import ResearchProject
from app.schemas.project import (
    CreateProjectRequest,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post("/")
async def create_project(
    request: CreateProjectRequest,
    db: AsyncSession = Depends(get_db),
):

    project = ResearchProject(
        title=request.title,
        query=request.query,
        status="pending",
    )

    db.add(project)

    await db.commit()
    await db.refresh(project)

    return {
        "id": project.id,
        "title": project.title,
        "query": project.query,
        "status": project.status,
    }


@router.get("/")
async def list_projects(
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(ResearchProject)
    )

    projects = result.scalars().all()

    return [
        {
            "id": project.id,
            "title": project.title,
            "query": project.query,
            "status": project.status,
        }
        for project in projects
    ]


@router.get("/{project_id}")
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(ResearchProject).where(
            ResearchProject.id == project_id
        )
    )

    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return {
        "id": project.id,
        "title": project.title,
        "query": project.query,
        "status": project.status,
    }


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):

    result = await db.execute(
        select(ResearchProject).where(
            ResearchProject.id == project_id
        )
    )

    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    await db.delete(project)
    await db.commit()

    return {
        "message": "Project deleted"
    }

from pydantic import BaseModel
class CreateReportRequest(BaseModel):
    title: str = "Research Report"
    content: str

from app.models.research import ProjectDocument, ResearchReport

@router.get("/{project_id}/documents")
async def list_project_documents(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ProjectDocument).where(ProjectDocument.project_id == project_id))
    docs = result.scalars().all()
    return [{"id": d.id, "filename": d.filename, "uploaded_at": d.uploaded_at} for d in docs]

@router.get("/{project_id}/reports")
async def list_project_reports(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ResearchReport).where(ResearchReport.project_id == project_id))
    reports = result.scalars().all()
    return [{"id": r.id, "title": r.title, "content": r.content, "created_at": r.created_at} for r in reports]

@router.post("/{project_id}/reports")
async def save_project_report(
    project_id: int,
    request: CreateReportRequest,
    db: AsyncSession = Depends(get_db),
):
    report = ResearchReport(project_id=project_id, title=request.title, content=request.content)
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return {"id": report.id, "title": report.title, "created_at": report.created_at}