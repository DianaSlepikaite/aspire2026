"""
API v1 router aggregation.
"""

from fastapi import APIRouter

from client_need_service.api.v1.endpoints import (
    health,
    conversation,
    client_needs,
    speech
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
    client_needs.router,
    prefix="/client-needs",
    tags=["client-needs"]
)

api_router.include_router(
    speech.router,
    prefix="/speech",
    tags=["speech"]
)
