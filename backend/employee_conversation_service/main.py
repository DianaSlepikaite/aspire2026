"""
FastAPI application entry point for Employee Conversation Service.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from employee_conversation_service.config import get_settings
from employee_conversation_service.api.v1.router import api_router
from employee_conversation_service.core.database import (
    initialize_database,
    close_database,
)

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize and close database."""
    logger.info("Employee Conversation Service starting...")
    try:
        await initialize_database()
    except Exception as e:
        logger.warning("Database initialization failed: %s", e)
    yield
    logger.info("Employee Conversation Service shutting down...")
    await close_database()


app = FastAPI(
    title="Employee Conversation Service",
    description=(
        "Employee profile extraction and orchestration via Employee Service Agent. "
        "**Agent endpoints** (process-upload, process-document, generate-resume, clarifying-questions) "
        "are under the **agent** tag. Use this service at port **8001** (Swagger: http://localhost:8001/docs)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "agent",
            "description": "Employee Service Agent: process-upload, process-document, generate-resume, clarifying-questions",
        },
        {
            "name": "conversation",
            "description": "Conversation: start, message, status, complete, history",
        },
        {"name": "speech", "description": "Speech: transcribe, synthesize, voices"},
        {
            "name": "speech-streaming",
            "description": "Real-time speech streaming over WebSocket: /speech/stream",
        },
        {"name": "health", "description": "Health check endpoints"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Employee Conversation Service",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "agent_base": f"{settings.API_V1_PREFIX}/agent",
        "agent_endpoints": [
            "POST /api/v1/agent/process-upload",
            "POST /api/v1/agent/process-document",
            "GET /api/v1/agent/generate-resume/{employee_profile_id}",
            "POST /api/v1/agent/clarifying-questions",
        ],
        "conversation_base": f"{settings.API_V1_PREFIX}/conversation",
        "speech_base": f"{settings.API_V1_PREFIX}/speech",
        "speech_stream_ws": f"{settings.API_V1_PREFIX}/speech/stream",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "employee_conversation_service.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.APP_ENV == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
