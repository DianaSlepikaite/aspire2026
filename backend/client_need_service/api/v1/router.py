"""
API v1 router aggregation.
"""

from fastapi import APIRouter

from client_need_service.api.v1.endpoints import (
    health,
    conversation,
    client_needs,
    speech,
    speech_websocket,
    intake,
    agent,
    matching,
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])

api_router.include_router(
    conversation.router, prefix="/conversation", tags=["conversation"]
)

api_router.include_router(
    client_needs.router, prefix="/client-needs", tags=["client-needs"]
)

api_router.include_router(speech.router, prefix="/speech", tags=["speech"])
api_router.include_router(
    speech_websocket.router, prefix="/speech", tags=["speech-streaming"]
)

api_router.include_router(intake.router, prefix="/intake", tags=["intake"])

api_router.include_router(agent.router, prefix="/agent", tags=["agent"])

api_router.include_router(matching.router, prefix="/matching", tags=["matching"])
