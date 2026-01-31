"""
Conversation management endpoints.
"""

import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from client_need_service.models.schemas import (
    ConversationStartRequest,
    ConversationStartResponse,
    MessageRequest,
    MessageResponse,
    ConversationStatusResponse,
    ConversationCompleteResponse,
    ConversationHistory
)
from client_need_service.services.conversation_service import ConversationService
from client_need_service.core.exceptions import (
    ConversationNotFoundError,
    ConversationError,
    ConversationTimeoutError
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/start",
    response_model=ConversationStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new conversation",
    description="Initialize a new conversation session with a client"
)
async def start_conversation(request: ConversationStartRequest):
    """
    Start a new conversation session.

    Creates a new client need profile and returns initial greeting message.
    """
    try:
        conversation_service = ConversationService()
        response = await conversation_service.start_conversation(request)
        return response
    except ConversationError as e:
        logger.error(f"Failed to start conversation: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error starting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to start conversation"}
        )


@router.post(
    "/{conversation_id}/message",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message",
    description="Send a text message in an ongoing conversation"
)
async def send_message(
    conversation_id: UUID,
    request: MessageRequest
):
    """
    Send a message in the conversation.

    Processes the user's message, generates an AI response, and extracts
    information to update the client need profile.
    """
    try:
        conversation_service = ConversationService()
        response = await conversation_service.send_message(conversation_id, request)
        return response
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message}
        )
    except ConversationTimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail={"error": e.message, "details": e.details}
        )
    except ConversationError as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to process message"}
        )


@router.get(
    "/{conversation_id}/status",
    response_model=ConversationStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get conversation status",
    description="Get current status and progress of a conversation"
)
async def get_conversation_status(conversation_id: UUID):
    """
    Get conversation status.

    Returns conversation metadata, progress metrics, and completion readiness.
    """
    try:
        conversation_service = ConversationService()
        response = await conversation_service.get_conversation_status(conversation_id)
        return response
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message}
        )
    except Exception as e:
        logger.error(f"Unexpected error getting conversation status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get conversation status"}
        )


@router.post(
    "/{conversation_id}/complete",
    response_model=ConversationCompleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete a conversation",
    description="Finalize a conversation and generate a summary"
)
async def complete_conversation(conversation_id: UUID):
    """
    Complete a conversation.

    Marks the conversation as complete and generates a comprehensive summary
    of the client's needs.
    """
    try:
        conversation_service = ConversationService()
        response = await conversation_service.complete_conversation(conversation_id)
        return response
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message}
        )
    except ConversationError as e:
        logger.error(f"Failed to complete conversation: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error completing conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to complete conversation"}
        )


@router.get(
    "/{conversation_id}/history",
    response_model=ConversationHistory,
    status_code=status.HTTP_200_OK,
    summary="Get conversation history",
    description="Get the full message history of a conversation"
)
async def get_conversation_history(conversation_id: UUID):
    """
    Get conversation history.

    Returns all messages in the conversation in chronological order.
    """
    try:
        conversation_service = ConversationService()
        response = await conversation_service.get_conversation_history(conversation_id)
        return response
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message}
        )
    except Exception as e:
        logger.error(f"Unexpected error getting conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get conversation history"}
        )
