import os
import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
)

from app.rag.ingestion import IngestionPipeline

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


@router.post("/pdf")
async def upload_pdf(
    project_id: int = Form(...),
    file: UploadFile = File(...)
):

    
    file_path = f"{UPLOAD_DIR}/{uuid.uuid4()}_{file.filename}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    result = pipeline.ingest_pdf(
        file_path=file_path,
        project_id=project_id
    )

    return {
        "project_id": project_id,
        **result
    }