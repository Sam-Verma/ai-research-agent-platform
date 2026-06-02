import os
import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends
)

from app.services.ingestion_service import IngestionPipeline

router = APIRouter(
    prefix="/upload",
    tags=["upload"]
)

pipeline = IngestionPipeline()

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.research import ProjectDocument

@router.post("/pdf")
async def upload_pdf(
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):

    
    file_path = f"{UPLOAD_DIR}/{uuid.uuid4()}_{file.filename}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    result = pipeline.ingest_pdf(
        file_path=file_path,
        project_id=project_id
    )
    
    doc = ProjectDocument(
        project_id=project_id,
        filename=file.filename
    )
    db.add(doc)
    await db.commit()

    return {
        "project_id": project_id,
        **result
    }