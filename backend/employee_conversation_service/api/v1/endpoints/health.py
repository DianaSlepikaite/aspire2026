"""Health check endpoint."""

from datetime import datetime, timezone
from fastapi import APIRouter

from employee_conversation_service.services.storage_service import StorageService

router = APIRouter()


@router.get("")
async def health():
    """Basic health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "Employee Conversation Service",
    }


@router.get("/detailed")
async def detailed_health():
    """Detailed health check including database connectivity."""
    services = []
    # Database
    try:
        storage = StorageService()
        db_healthy = await storage.check_health()
        services.append(
            {
                "name": "database",
                "status": "healthy" if db_healthy else "unhealthy",
                "message": "Connected" if db_healthy else "Connection failed",
            }
        )
    except Exception as e:
        services.append(
            {
                "name": "database",
                "status": "unhealthy",
                "message": str(e),
            }
        )
    overall = (
        "healthy" if all(s["status"] == "healthy" for s in services) else "degraded"
    )
    return {
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": services,
        "version": "1.0.0",
    }
