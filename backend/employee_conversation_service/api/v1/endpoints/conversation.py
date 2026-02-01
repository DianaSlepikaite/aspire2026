"""
Conversation management endpoints (employee service).
"""

import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from employee_conversation_service.models.schemas import (
    ConversationStartRequest,
    ConversationStartResponse,
    MessageRequest,
    MessageResponse,
    ConversationStatusResponse,
    ConversationCompleteResponse,
    ConversationHistory,
)
from employee_conversation_service.services.conversation_service import (
    ConversationService,
)
from employee_conversation_service.core.exceptions import (
    ConversationNotFoundError,
    ConversationError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/start",
    response_model=ConversationStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new conversation",
    description="Initialize a new employee conversation session",
    tags=["conversation"],
)
async def start_conversation(request: ConversationStartRequest):
    """Start a new employee conversation."""
    try:
        service = ConversationService()
        return await service.start_conversation(request)
    except ConversationError as e:
        logger.error("Failed to start conversation: %s", e)
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to start conversation"},
        )


@router.post(
    "/{conversation_id}/message",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message",
    description="Send a text message in an ongoing conversation",
    tags=["conversation"],
)
async def send_message(conversation_id: UUID, request: MessageRequest):
    """Send a message in the conversation."""
    try:
        service = ConversationService()
        return await service.send_message(conversation_id, request)
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message},
        )
    except ConversationError as e:
        logger.error("Failed to send message: %s", e)
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to process message"},
        )


@router.get(
    "/{conversation_id}/status",
    response_model=ConversationStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get conversation status",
    description="Get current status of a conversation",
    tags=["conversation"],
)
async def get_conversation_status(conversation_id: UUID):
    """Get conversation status."""
    try:
        service = ConversationService()
        return await service.get_conversation_status(conversation_id)
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message},
        )
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get status"},
        )


@router.post(
    "/{conversation_id}/complete",
    response_model=ConversationCompleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete a conversation",
    description="Finalize a conversation and generate summary",
    tags=["conversation"],
)
async def complete_conversation(conversation_id: UUID):
    """Complete a conversation."""
    try:
        service = ConversationService()
        return await service.complete_conversation(conversation_id)
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message},
        )
    except ConversationError as e:
        logger.error("Failed to complete: %s", e)
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to complete conversation"},
        )


@router.get(
    "/{conversation_id}/history",
    response_model=ConversationHistory,
    status_code=status.HTTP_200_OK,
    summary="Get conversation history",
    description="Get the full message history of a conversation",
    tags=["conversation"],
)
async def get_conversation_history(conversation_id: UUID):
    """Get conversation history."""
    try:
        service = ConversationService()
        return await service.get_conversation_history(conversation_id)
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message},
        )
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get history"},
        )
