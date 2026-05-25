import os

from fastapi import (
    APIRouter,
    UploadFile,
    File,
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
    file: UploadFile = File(...)
):

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    result = pipeline.ingest_pdf(
        file_path=file_path
    )

    return result