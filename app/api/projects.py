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