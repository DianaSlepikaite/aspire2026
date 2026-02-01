"""
Employee profile CRUD endpoints.
"""

import logging
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from employee_conversation_service.models.schemas import (
    EmployeeProfile,
    EmployeeProfileList,
    EmployeeProfileUpdate
)
from employee_conversation_service.services.storage_service import StorageService
from employee_conversation_service.core.exceptions import EmployeeProfileNotFoundError, StorageError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=EmployeeProfileList,
    status_code=status.HTTP_200_OK,
    summary="List employee profiles",
    description="Get a paginated list of employee profiles with optional filters"
)
async def list_employee_profiles(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by conversation status"),
    experience_level: Optional[str] = Query(None, description="Filter by PS experience level/grade"),
    bench_status: Optional[str] = Query(None, description="Filter by bench status (on_project, on_bench, rolling_off, partially_allocated)"),
    career_track: Optional[str] = Query(None, description="Filter by career track"),
    min_completeness: Optional[int] = Query(None, ge=0, le=100, description="Minimum profile completeness score"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List employee profiles.

    Supports filtering by status, experience level, bench status, career track,
    and minimum completeness score. Results are paginated.
    """
    try:
        storage_service = StorageService()

        # Build filters
        filters = {}
        if status_filter:
            filters["status"] = status_filter
        if experience_level:
            filters["experience_level"] = experience_level
        if bench_status:
            filters["bench_status"] = bench_status
        if career_track:
            filters["career_track"] = career_track
        if min_completeness is not None:
            filters["min_completeness"] = min_completeness

        # Get employee profiles
        profiles, total = await storage_service.list_employee_profiles(
            filters=filters,
            limit=limit,
            offset=offset
        )

        return EmployeeProfileList(
            items=profiles,
            total=total,
            limit=limit,
            offset=offset
        )

    except StorageError as e:
        logger.error(f"Failed to list employee profiles: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error listing employee profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to list employee profiles"}
        )


@router.get(
    "/{id}",
    response_model=EmployeeProfile,
    status_code=status.HTTP_200_OK,
    summary="Get employee profile",
    description="Get a specific employee profile by ID"
)
async def get_employee_profile(id: UUID):
    """
    Get an employee profile by ID.

    Returns the complete profile including all extracted information.
    """
    try:
        storage_service = StorageService()

        profile = await storage_service.get_employee_profile(id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Employee profile not found: {id}"}
            )

        return profile

    except HTTPException:
        raise
    except StorageError as e:
        logger.error(f"Failed to get employee profile: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error getting employee profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get employee profile"}
        )


@router.patch(
    "/{id}",
    response_model=EmployeeProfile,
    status_code=status.HTTP_200_OK,
    summary="Update employee profile",
    description="Update an employee profile (e.g., manual corrections)"
)
async def update_employee_profile(
    id: UUID,
    update: EmployeeProfileUpdate
):
    """
    Update an employee profile.

    Allows manual corrections or updates to the profile information.
    Fields edited here are tracked so the AI agent won't overwrite them.
    """
    try:
        storage_service = StorageService()

        # Track which fields the user is manually editing
        edited_fields = [
            k for k, v in update.model_dump(exclude_none=True).items()
            if k not in (
                "conversation_status", "conversation_started_at",
                "conversation_completed_at", "profile_completeness_score",
                "user_edited_fields", "uploaded_documents",
            )
        ]

        if edited_fields:
            # Fetch current profile to merge with existing edited-fields list
            current = await storage_service.get_employee_profile(id)
            if current:
                existing_edited = current.user_edited_fields or []
                merged_edited = list(set(existing_edited + edited_fields))
                update.user_edited_fields = merged_edited

        updated_profile = await storage_service.update_employee_profile(id, update)

        return updated_profile

    except EmployeeProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message}
        )
    except StorageError as e:
        logger.error(f"Failed to update employee profile: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error updating employee profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to update employee profile"}
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete employee profile",
    description="Delete an employee profile"
)
async def delete_employee_profile(id: UUID):
    """
    Delete an employee profile.

    Permanently removes the profile and all associated conversation data.
    """
    try:
        storage_service = StorageService()

        await storage_service.delete_employee_profile(id)

        return None

    except EmployeeProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message}
        )
    except StorageError as e:
        logger.error(f"Failed to delete employee profile: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting employee profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to delete employee profile"}
        )
