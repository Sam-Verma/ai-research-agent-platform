from fastapi import FastAPI
import structlog
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging

from app.api.health import router as health_router
from app.api.llm import router as llm_router

from app.api.upload import router as upload_router
from app.api.rag import router as rag_router

from app.api.chat import (
    router as chat_router
)

from app.api.projects import (
    router as projects_router,
)

from app.api.dependencies import get_qdrant_service, get_llm_service

setup_logging()

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started", app=settings.APP_NAME)
    
    qdrant_service = get_qdrant_service()
    qdrant_service.create_collection()
    logger.info("Qdrant collection initialized")
    
    yield
    
    # Cleanup resources
    llm_service = get_llm_service()
    await llm_service.close()
    logger.info("Application shutdown, resources cleaned up")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(health_router)
app.include_router(projects_router)
app.include_router(llm_router)
app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(rag_router)


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")

    return {
        "app": settings.APP_NAME,
        "model": settings.LLM_MODEL,
        "status": "running"
    }