"""API v1 router aggregation."""

from fastapi import APIRouter

from employee_conversation_service.api.v1.endpoints import (
    health,
    agent,
    conversation,
    speech,
    speech_websocket,
    profile,
    documents,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(
    conversation.router, prefix="/conversation", tags=["conversation"]
)
api_router.include_router(speech.router, prefix="/speech", tags=["speech"])
api_router.include_router(
    speech_websocket.router, prefix="/speech", tags=["speech-streaming"]
)
api_router.include_router(
    profile.router, prefix="/employee-profiles", tags=["profiles"]
)
api_router.include_router(
    documents.router, prefix="/employee-documents", tags=["documents"]
)
