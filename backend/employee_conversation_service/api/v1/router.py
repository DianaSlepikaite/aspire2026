"""API v1 router aggregation."""

from fastapi import APIRouter

from employee_conversation_service.api.v1.endpoints import health, agent

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
