"""
API v1 router aggregation.
"""

from fastapi import APIRouter

from employee_conversation_service.api.v1.endpoints import (
    health,
    conversation,
    employee_profiles,
    speech,
    document,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    conversation.router,
    prefix="/conversation",
    tags=["conversation"]
)

api_router.include_router(
    employee_profiles.router,
    prefix="/employee-profiles",
    tags=["employee-profiles"]
)

api_router.include_router(
    speech.router,
    prefix="/speech",
    tags=["speech"]
)

api_router.include_router(
    document.router,
    prefix="/document",
    tags=["document"]
)
