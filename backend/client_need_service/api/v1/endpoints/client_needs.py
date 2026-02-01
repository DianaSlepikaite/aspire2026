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
    ClientNeedMessageRequest,
    ClientNeedMessageResponse,
    ClientNeedUpdate
)
from client_need_service.services.need_extraction_service import NeedExtractionService
from client_need_service.services.storage_service import StorageService
from client_need_service.core.exceptions import ClientNeedNotFoundError, StorageError, ServiceError

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

        # Ensure completeness/missing info are up to date for list display
        extraction_service = NeedExtractionService()
        refreshed_needs = []
        for need in client_needs:
            profile_dict = need.model_dump(exclude_none=True)
            completeness = extraction_service.calculate_completeness_score(profile_dict)
            missing_fields = extraction_service.identify_missing_fields(profile_dict)
            if (
                completeness != need.profile_completeness_score
                or (missing_fields and missing_fields != (need.missing_information or []))
            ):
                need = await storage_service.update_client_need(
                    need.id,
                    ClientNeedUpdate(
                        profile_completeness_score=completeness,
                        missing_information=missing_fields
                    )
                )
            refreshed_needs.append(need)

        return ClientNeedList(
            items=refreshed_needs,
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


@router.post(
    "/{id}/message",
    response_model=ClientNeedMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Update client need from message",
    description="Update a client need profile by extracting info from a user message"
)
async def update_client_need_from_message(
    id: UUID,
    request: ClientNeedMessageRequest
):
    """
    Update a client need profile using a user message.

    Extracts structured fields from the message and updates the existing profile.
    """
    try:
        storage_service = StorageService()
        extraction_service = NeedExtractionService()

        client_need = await storage_service.get_client_need(id)
        if not client_need:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Client need not found: {id}"}
            )

        update, metadata = await extraction_service.extract_needs_from_text(
            request.message,
            client_name=client_need.client_name,
            client_email=client_need.client_email
        )

        updated_client_need = await storage_service.update_client_need(id, update)

        profile_dict = updated_client_need.model_dump(exclude_none=True)
        completeness = extraction_service.calculate_completeness_score(profile_dict)
        missing_fields = extraction_service.identify_missing_fields(profile_dict)
        critical_missing = extraction_service.identify_critical_missing_fields(profile_dict)

        updated_client_need = await storage_service.update_client_need(
            id,
            ClientNeedUpdate(
                profile_completeness_score=completeness,
                missing_information=missing_fields
            )
        )

        return ClientNeedMessageResponse(
            client_need=updated_client_need,
            profile_completeness=completeness,
            missing_fields=missing_fields,
            critical_missing_fields=critical_missing
        )

    except HTTPException:
        raise
    except (ServiceError, StorageError) as e:
        logger.error(f"Failed to update client need from message: {e}")
        raise HTTPException(
            status_code=getattr(e, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
            detail={"error": getattr(e, "message", str(e)), "details": getattr(e, "details", None)}
        )
    except Exception as e:
        logger.error(f"Unexpected error updating client need from message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to update client need from message"}
        )
