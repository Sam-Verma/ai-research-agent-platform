from fastapi import FastAPI
import structlog

from app.core.config import settings
from app.core.logging import setup_logging

from app.api.health import router as health_router
from app.api.llm import router as llm_router

from app.services.qdrant_service import QdrantService
from app.api.upload import router as upload_router
from app.api.rag import router as rag_router
from app.api.stream import router as stream_router

from app.api.chat import (
    router as chat_router
)
from app.api.chat_stream import (
    router as chat_stream_router
)

from app.api.projects import (
    router as projects_router,
)

setup_logging()

logger = structlog.get_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(projects_router)
app.include_router(llm_router)
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(chat_stream_router)
app.include_router(rag_router)
app.include_router(stream_router)


@app.on_event("startup")
async def startup_event():

    logger.info(
        "Application started",
        app=settings.APP_NAME
    )

    qdrant_service = QdrantService()
    qdrant_service.create_collection()

    logger.info(
        "Qdrant collection initialized"
    )


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")

    return {
        "app": settings.APP_NAME,
        "model": settings.LLM_MODEL,
        "status": "running"
    }