"""
Conversation management endpoints.
"""

import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from employee_conversation_service.config import get_settings
from employee_conversation_service.models.schemas import (
    ConversationStartRequest,
    ConversationStartResponse,
    MessageRequest,
    MessageResponse,
    ConversationStatusResponse,
    ConversationCompleteResponse,
    ConversationHistory,
    ConversationDocumentUploadResponse,
    EmployeeLookupResponse
)
from employee_conversation_service.services.conversation_service import ConversationService
from employee_conversation_service.services.document_upload_service import DocumentUploadService
from employee_conversation_service.core.exceptions import (
    ConversationNotFoundError,
    ConversationError,
    ConversationTimeoutError,
    DocumentUploadError,
    DocumentParsingError,
    AzureOpenAIError,
    BlobStorageError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/lookup",
    response_model=EmployeeLookupResponse,
    status_code=status.HTTP_200_OK,
    summary="Look up employee conversations",
    description="Look up an employee's conversation history by employee_id or employee_email"
)
async def lookup_employee(
    employee_id: Optional[str] = Query(None, description="PS Employee ID"),
    employee_email: Optional[str] = Query(None, description="Employee email address")
):
    """
    Look up an employee's previous conversations.

    At least one of employee_id or employee_email must be provided.
    Returns conversation history, counts, and latest profile data.
    """
    if not employee_id and not employee_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "At least one of employee_id or employee_email is required"}
        )

    try:
        conversation_service = ConversationService()
        response = await conversation_service.lookup_employee(
            employee_id=employee_id,
            employee_email=employee_email
        )
        return response
    except ConversationError as e:
        logger.error(f"Failed to lookup employee: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error looking up employee: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to lookup employee"}
        )


@router.post(
    "/{conversation_id}/resume",
    response_model=ConversationStartResponse,
    status_code=status.HTTP_200_OK,
    summary="Resume a conversation",
    description="Resume an in-progress conversation"
)
async def resume_conversation(conversation_id: UUID):
    """
    Resume an in-progress conversation.

    Resets the conversation timeout and generates a welcome-back message
    that recaps where the conversation left off.
    """
    try:
        conversation_service = ConversationService()
        response = await conversation_service.resume_conversation(conversation_id)
        return response
    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message}
        )
    except ConversationError as e:
        logger.error(f"Failed to resume conversation: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error resuming conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to resume conversation"}
        )


@router.post(
    "/start",
    response_model=ConversationStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new conversation",
    description="Initialize a new conversation session with an employee"
)
async def start_conversation(request: ConversationStartRequest):
    """
    Start a new conversation session.

    Creates a new employee profile and returns initial greeting message.
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
    information to update the employee profile.
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
    of the employee's profile.
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


@router.post(
    "/{conversation_id}/upload-document",
    response_model=ConversationDocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a document to a conversation",
    description="Upload a CV/resume document within an active conversation to enrich the profile",
)
async def upload_conversation_document(
    conversation_id: UUID,
    file: UploadFile = File(..., description="PDF or DOCX file"),
):
    """
    Upload a CV/resume document within an active conversation.

    Parses the document, extracts structured data, and merges it into the
    existing profile using a 'document fills gaps, conversation wins conflicts'
    strategy.
    """
    settings = get_settings()

    if not settings.ENABLE_DOCUMENT_UPLOAD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Document upload is disabled"},
        )

    try:
        file_bytes = await file.read()

        upload_service = DocumentUploadService()
        response = await upload_service.upload_for_conversation(
            conversation_id=conversation_id,
            file_bytes=file_bytes,
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
        )

        return response

    except ConversationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message},
        )
    except DocumentUploadError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except DocumentParsingError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except AzureOpenAIError as e:
        logger.error(f"OpenAI extraction failed: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except BlobStorageError as e:
        logger.error(f"Blob storage error: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except Exception as e:
        logger.error(f"Unexpected error during conversation document upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to process document upload"},
        )
