"""
Employee document endpoints.
"""

import logging
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, HTTPException, status, Query

from employee_conversation_service.models.schemas import EmployeeDocument
from employee_conversation_service.services.storage_service import StorageService
from employee_conversation_service.core.exceptions import StorageError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=List[EmployeeDocument],
    status_code=status.HTTP_200_OK,
    summary="List employee documents",
    description="List documents, optionally filtered by employee profile",
    tags=["documents"],
)
async def list_employee_documents(
    employee_profile_id: Optional[UUID] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """List employee documents with optional profile filter."""
    try:
        storage = StorageService()
        docs = await storage.list_documents(
            employee_profile_id=employee_profile_id, limit=limit, offset=offset
        )
        return docs
    except StorageError as e:
        logger.exception("Storage error: %s", e)
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to list documents"},
        )


@router.get(
    "/{document_id}",
    response_model=EmployeeDocument,
    status_code=status.HTTP_200_OK,
    summary="Get employee document",
    description="Retrieve a document by ID",
    tags=["documents"],
)
async def get_employee_document(document_id: UUID):
    """Get an employee document by ID."""
    try:
        storage = StorageService()
        doc = await storage.get_document(document_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Document not found"},
            )
        return doc
    except StorageError as e:
        logger.exception("Storage error: %s", e)
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to retrieve document"},
        )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete employee document",
    description="Delete a document by ID",
    tags=["documents"],
)
async def delete_employee_document(document_id: UUID):
    """Delete an employee document by ID."""
    try:
        storage = StorageService()
        await storage.delete_document(document_id)
        return {"deleted": True}
    except StorageError as e:
        logger.exception("Storage error: %s", e)
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to delete document"},
        )
