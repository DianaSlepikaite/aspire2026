"""
Employee profile endpoints.
"""

import logging
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query

from employee_conversation_service.models.schemas import EmployeeProfile, EmployeeProfileUpdate
from employee_conversation_service.services.storage_service import StorageService
from employee_conversation_service.core.exceptions import (
    EmployeeProfileNotFoundError,
    StorageError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{profile_id}",
    response_model=EmployeeProfile,
    status_code=status.HTTP_200_OK,
    summary="Get employee profile",
    description="Retrieve a complete employee profile by ID",
    tags=["profiles"],
)
async def get_employee_profile(profile_id: UUID):
    """Get an employee profile by ID."""
    try:
        storage = StorageService()
        profile = await storage.get_employee_profile(profile_id)

        if not profile:
            raise EmployeeProfileNotFoundError(
                profile_id=profile_id,
                message=f"Employee profile {profile_id} not found"
            )

        return profile
    except EmployeeProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "details": e.details},
        )
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
            detail={"error": "Failed to retrieve employee profile"},
        )


@router.patch(
    "/{profile_id}",
    response_model=EmployeeProfile,
    status_code=status.HTTP_200_OK,
    summary="Update employee profile",
    description="Update employee profile fields",
    tags=["profiles"],
)
async def update_employee_profile(profile_id: UUID, payload: EmployeeProfileUpdate):
    """Update an employee profile by ID."""
    try:
        storage = StorageService()
        profile = await storage.update_employee_profile(profile_id, payload)
        return profile
    except EmployeeProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "details": e.details},
        )
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
            detail={"error": "Failed to update employee profile"},
        )


@router.get(
    "/",
    response_model=List[EmployeeProfile],
    status_code=status.HTTP_200_OK,
    summary="List employee profiles",
    description="Get a list of all employee profiles with pagination",
    tags=["profiles"],
)
async def list_employee_profiles(
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of profiles to return"),
    offset: int = Query(default=0, ge=0, description="Number of profiles to skip"),
):
    """List employee profiles with pagination."""
    try:
        storage = StorageService()
        profiles = await storage.list_profiles(
            limit=limit,
            offset=offset,
        )
        return profiles
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
            detail={"error": "Failed to list employee profiles"},
        )
