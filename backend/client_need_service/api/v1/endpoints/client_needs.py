"""
Client needs CRUD endpoints.
"""

import logging
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from client_need_service.models.schemas import (
    ClientNeed,
    ClientNeedList,
    ClientNeedUpdate
)
from client_need_service.services.storage_service import StorageService
from client_need_service.core.exceptions import ClientNeedNotFoundError, StorageError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=ClientNeedList,
    status_code=status.HTTP_200_OK,
    summary="List client needs",
    description="Get a paginated list of client need profiles with optional filters"
)
async def list_client_needs(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by conversation status"),
    urgency: Optional[str] = Query(None, description="Filter by urgency level"),
    min_completeness: Optional[int] = Query(None, ge=0, le=100, description="Minimum profile completeness score"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List client need profiles.

    Supports filtering by status, urgency, and minimum completeness score.
    Results are paginated.
    """
    try:
        storage_service = StorageService()

        # Build filters
        filters = {}
        if status_filter:
            filters["status"] = status_filter
        if urgency:
            filters["urgency"] = urgency
        if min_completeness is not None:
            filters["min_completeness"] = min_completeness

        # Get client needs
        client_needs, total = await storage_service.list_client_needs(
            filters=filters,
            limit=limit,
            offset=offset
        )

        return ClientNeedList(
            items=client_needs,
            total=total,
            limit=limit,
            offset=offset
        )

    except StorageError as e:
        logger.error(f"Failed to list client needs: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error listing client needs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to list client needs"}
        )


@router.get(
    "/{id}",
    response_model=ClientNeed,
    status_code=status.HTTP_200_OK,
    summary="Get client need",
    description="Get a specific client need profile by ID"
)
async def get_client_need(id: UUID):
    """
    Get a client need profile by ID.

    Returns the complete profile including all extracted information.
    """
    try:
        storage_service = StorageService()

        client_need = await storage_service.get_client_need(id)

        if not client_need:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Client need not found: {id}"}
            )

        return client_need

    except HTTPException:
        raise
    except StorageError as e:
        logger.error(f"Failed to get client need: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error getting client need: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get client need"}
        )


@router.patch(
    "/{id}",
    response_model=ClientNeed,
    status_code=status.HTTP_200_OK,
    summary="Update client need",
    description="Update a client need profile (e.g., manual corrections)"
)
async def update_client_need(
    id: UUID,
    update: ClientNeedUpdate
):
    """
    Update a client need profile.

    Allows manual corrections or updates to the profile information.
    """
    try:
        storage_service = StorageService()

        updated_client_need = await storage_service.update_client_need(id, update)

        return updated_client_need

    except ClientNeedNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message}
        )
    except StorageError as e:
        logger.error(f"Failed to update client need: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error updating client need: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to update client need"}
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete client need",
    description="Delete a client need profile"
)
async def delete_client_need(id: UUID):
    """
    Delete a client need profile.

    Permanently removes the profile and all associated conversation data.
    """
    try:
        storage_service = StorageService()

        await storage_service.delete_client_need(id)

        return None

    except ClientNeedNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message}
        )
    except StorageError as e:
        logger.error(f"Failed to delete client need: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting client need: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to delete client need"}
        )
