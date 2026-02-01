"""
Document upload endpoints for standalone CV/resume uploads.
"""

import logging
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import (
    DocumentUploadError,
    DocumentParsingError,
    AzureOpenAIError,
    BlobStorageError,
)
from employee_conversation_service.models.schemas import DocumentUploadResponse
from employee_conversation_service.services.document_upload_service import (
    DocumentUploadService,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document (standalone)",
    description="Upload a CV/resume document for profile extraction without an active conversation",
)
async def upload_document(
    file: UploadFile = File(..., description="PDF or DOCX file"),
    employee_id: Optional[str] = Form(None, description="PS Employee ID"),
    employee_email: Optional[str] = Form(None, description="Employee email address"),
):
    """
    Upload a CV/resume document for standalone profile extraction.

    Accepts PDF or DOCX files up to the configured size limit.
    Parses the document, extracts structured profile data using GPT-4,
    and optionally stores the original in Azure Blob Storage.
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
        response = await upload_service.upload_standalone(
            file_bytes=file_bytes,
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            employee_id=employee_id,
            employee_email=employee_email,
        )

        return response

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
        logger.error(f"Unexpected error during document upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to process document upload"},
        )
