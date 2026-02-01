"""
FastAPI application entry point for Employee Conversation Service Agent.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.logging import setup_logging
from employee_conversation_service.core.database import initialize_database, close_database
from employee_conversation_service.core.exceptions import ServiceError
from employee_conversation_service.api.v1.router import api_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Employee Conversation Service Agent...")
    logger.info(f"Environment: {settings.APP_ENV}")

    # Initialize database connection
    try:
        await initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")

    # Check Azure OpenAI configuration
    if settings.has_azure_openai_credentials():
        logger.info("Azure OpenAI configured")
    else:
        logger.warning("Azure OpenAI not configured - conversational features will not work")

    # Check Azure Speech configuration
    if settings.has_azure_speech_credentials():
        logger.info("Azure Speech configured")
    else:
        logger.warning("Azure Speech not configured - speech features will not work")

    # Check Azure Blob Storage configuration
    if settings.has_azure_blob_credentials():
        logger.info("Azure Blob Storage configured")
    else:
        logger.warning("Azure Blob Storage not configured - document upload will use local fallback")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Employee Conversation Service Agent...")
    await close_database()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Employee Conversation Service Agent",
    description="AI-powered service for extracting employee skills, experience, and career goals through natural conversation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers

@app.exception_handler(ServiceError)
async def service_error_handler(request: Request, exc: ServiceError):
    """Handle custom service errors."""
    logger.error(f"Service error: {exc.message}", exc_info=exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


# Include API router
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)


# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="Root endpoint",
    description="Returns basic service information"
)
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Employee Conversation Service Agent",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.is_development(),
        log_level=settings.LOG_LEVEL.lower()
    )
