"""
Health check endpoints.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, status

from employee_conversation_service.models.schemas import HealthCheck, DetailedHealthCheck, ServiceStatus
from employee_conversation_service.services.azure_openai_service import AzureOpenAIService
from employee_conversation_service.services.speech_service import SpeechService
from employee_conversation_service.services.storage_service import StorageService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=HealthCheck,
    status_code=status.HTTP_200_OK,
    summary="Basic health check",
    description="Returns basic health status of the service"
)
async def health_check():
    """Basic health check endpoint."""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow()
    )


@router.get(
    "/detailed",
    response_model=DetailedHealthCheck,
    status_code=status.HTTP_200_OK,
    summary="Detailed health check",
    description="Returns detailed health status including all dependent services"
)
async def detailed_health_check():
    """
    Detailed health check that verifies all services.
    """
    services = []

    # Check Azure OpenAI
    try:
        openai_service = AzureOpenAIService()
        openai_healthy = await openai_service.check_health()
        services.append(ServiceStatus(
            name="azure_openai",
            status="healthy" if openai_healthy else "unhealthy",
            message="Connected" if openai_healthy else "Not available"
        ))
    except Exception as e:
        services.append(ServiceStatus(
            name="azure_openai",
            status="unhealthy",
            message=f"Error: {str(e)}"
        ))

    # Check Azure Speech
    try:
        speech_service = SpeechService()
        # Note: Full health check is expensive, just check if configured
        speech_configured = speech_service._speech_config is not None
        services.append(ServiceStatus(
            name="azure_speech",
            status="healthy" if speech_configured else "unavailable",
            message="Configured" if speech_configured else "Not configured"
        ))
    except Exception as e:
        services.append(ServiceStatus(
            name="azure_speech",
            status="unhealthy",
            message=f"Error: {str(e)}"
        ))

    # Check Database
    try:
        storage_service = StorageService()
        db_healthy = await storage_service.check_health()
        services.append(ServiceStatus(
            name="database",
            status="healthy" if db_healthy else "unhealthy",
            message="Connected" if db_healthy else "Connection failed"
        ))
    except Exception as e:
        services.append(ServiceStatus(
            name="database",
            status="unhealthy",
            message=f"Error: {str(e)}"
        ))

    # Determine overall status
    overall_status = "healthy"
    if any(s.status == "unhealthy" for s in services):
        overall_status = "degraded"

    return DetailedHealthCheck(
        status=overall_status,
        timestamp=datetime.utcnow(),
        services=services,
        version="1.0.0"
    )
