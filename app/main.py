from fastapi import FastAPI
import structlog

from app.core.config import settings
from app.core.logging import setup_logging

from app.api.health import router as health_router
from app.api.llm import router as llm_router

setup_logging()

logger = structlog.get_logger()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(llm_router)


@app.on_event("startup")
async def startup_event():
    logger.info(
        "Application started",
        app=settings.APP_NAME
    )


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")

    return {
        "app": settings.APP_NAME,
        "model": settings.LLM_MODEL,
        "status": "running"
    }