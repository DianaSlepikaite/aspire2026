"""
Storage service for Supabase database operations.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from supabase import Client

from employee_conversation_service.core.database import get_supabase_client
from employee_conversation_service.core.exceptions import (
    StorageError,
    EmployeeProfileNotFoundError,
    ConversationNotFoundError
)
from employee_conversation_service.models.schemas import (
    EmployeeProfileCreate,
    EmployeeProfileUpdate,
    EmployeeProfile,
    ConversationMessageCreate,
    ConversationMessage,
    ConversationStatus,
    ExtractionHistoryCreate,
    ExtractionHistory
)

logger = logging.getLogger(__name__)


class StorageService:
    """Service for database operations with Supabase."""

    def __init__(self):
        """Initialize storage service."""
        self.client: Optional[Client] = None

    async def _get_client(self) -> Client:
        """Get Supabase client instance."""
        if self.client is None:
            self.client = await get_supabase_client()
        return self.client

    async def create_employee_profile(
        self,
        data: EmployeeProfileCreate
    ) -> EmployeeProfile:
        """
        Create a new employee profile.

        Args:
            data: Employee profile creation data

        Returns:
            Created employee profile

        Raises:
            StorageError: If creation fails
        """
        try:
            client = await self._get_client()

            # Prepare data for insertion
            insert_data = {
                "id": str(uuid4()),
                "conversation_id": str(data.conversation_id),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "conversation_status": ConversationStatus.IN_PROGRESS.value,
                "total_messages": 0,
                "conversation_started_at": datetime.utcnow().isoformat(),
                "profile_completeness_score": 0,
                **data.model_dump(exclude={"conversation_id"}, exclude_none=True)
            }

            # Insert into database
            result = client.table("employee_profiles").insert(insert_data).execute()

            if not result.data:
                raise StorageError("Failed to create employee profile")

            logger.info(f"Created employee profile: {result.data[0]['id']}")

            return EmployeeProfile(**result.data[0])

        except Exception as e:
            logger.error(f"Failed to create employee profile: {e}")
            raise StorageError(
                f"Failed to create employee profile: {str(e)}",
                details={"error": str(e)}
            )

    async def update_employee_profile(
        self,
        id: UUID,
        data: EmployeeProfileUpdate
    ) -> EmployeeProfile:
        """
        Update an existing employee profile.

        Args:
            id: Employee profile ID
            data: Update data

        Returns:
            Updated employee profile

        Raises:
            EmployeeProfileNotFoundError: If profile not found
            StorageError: If update fails
        """
        try:
            client = await self._get_client()

            # Prepare update data
            update_data = data.model_dump(exclude_none=True)
            update_data["updated_at"] = datetime.utcnow().isoformat()

            # Update in database
            result = client.table("employee_profiles").update(update_data).eq(
                "id", str(id)
            ).execute()

            if not result.data:
                raise EmployeeProfileNotFoundError(str(id))

            logger.info(f"Updated employee profile: {id}")

            return EmployeeProfile(**result.data[0])

        except EmployeeProfileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update employee profile: {e}")
            raise StorageError(
                f"Failed to update employee profile: {str(e)}",
                details={"error": str(e)}
            )

    async def get_employee_profile(self, id: UUID) -> Optional[EmployeeProfile]:
        """
        Get an employee profile by ID.

        Args:
            id: Employee profile ID

        Returns:
            Employee profile if found, None otherwise

        Raises:
            StorageError: If query fails
        """
        try:
            client = await self._get_client()

            result = client.table("employee_profiles").select("*").eq(
                "id", str(id)
            ).execute()

            if not result.data:
                return None

            return EmployeeProfile(**result.data[0])

        except Exception as e:
            logger.error(f"Failed to get employee profile: {e}")
            raise StorageError(
                f"Failed to get employee profile: {str(e)}",
                details={"error": str(e)}
            )

    async def get_by_conversation_id(
        self,
        conversation_id: UUID
    ) -> Optional[EmployeeProfile]:
        """
        Get employee profile by conversation ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Employee profile if found, None otherwise

        Raises:
            StorageError: If query fails
        """
        try:
            client = await self._get_client()

            result = client.table("employee_profiles").select("*").eq(
                "conversation_id", str(conversation_id)
            ).execute()

            if not result.data:
                return None

            return EmployeeProfile(**result.data[0])

        except Exception as e:
            logger.error(f"Failed to get employee profile by conversation ID: {e}")
            raise StorageError(
                f"Failed to get employee profile: {str(e)}",
                details={"error": str(e)}
            )

    async def list_employee_profiles(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[EmployeeProfile], int]:
        """
        List employee profiles with optional filters and pagination.

        Args:
            filters: Optional filters (status, experience_level, bench_status, career_track)
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            Tuple of (list of employee profiles, total count)

        Raises:
            StorageError: If query fails
        """
        try:
            client = await self._get_client()

            # Build query
            query = client.table("employee_profiles").select("*", count="exact")

            # Apply filters
            if filters:
                if "status" in filters:
                    query = query.eq("conversation_status", filters["status"])
                if "experience_level" in filters:
                    query = query.eq("experience_level", filters["experience_level"])
                if "min_completeness" in filters:
                    query = query.gte(
                        "profile_completeness_score",
                        filters["min_completeness"]
                    )
                if "bench_status" in filters:
                    query = query.eq("bench_status", filters["bench_status"])
                if "career_track" in filters:
                    query = query.eq("career_track", filters["career_track"])

            # Apply pagination and ordering
            query = query.order("created_at", desc=True).range(
                offset, offset + limit - 1
            )

            result = query.execute()

            # Parse results
            profiles = [EmployeeProfile(**item) for item in result.data]
            total = result.count if result.count is not None else len(profiles)

            logger.info(f"Listed {len(profiles)} employee profiles (total: {total})")

            return profiles, total

        except Exception as e:
            logger.error(f"Failed to list employee profiles: {e}")
            raise StorageError(
                f"Failed to list employee profiles: {str(e)}",
                details={"error": str(e)}
            )

    async def delete_employee_profile(self, id: UUID) -> bool:
        """
        Delete an employee profile.

        Args:
            id: Employee profile ID

        Returns:
            True if deleted successfully

        Raises:
            EmployeeProfileNotFoundError: If profile not found
            StorageError: If deletion fails
        """
        try:
            client = await self._get_client()

            result = client.table("employee_profiles").delete().eq(
                "id", str(id)
            ).execute()

            if not result.data:
                raise EmployeeProfileNotFoundError(str(id))

            logger.info(f"Deleted employee profile: {id}")

            return True

        except EmployeeProfileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete employee profile: {e}")
            raise StorageError(
                f"Failed to delete employee profile: {str(e)}",
                details={"error": str(e)}
            )

    # Conversation Message Operations

    async def save_message(
        self,
        message: ConversationMessageCreate
    ) -> ConversationMessage:
        """
        Save a conversation message.

        Args:
            message: Message to save

        Returns:
            Saved message

        Raises:
            StorageError: If save fails
        """
        try:
            client = await self._get_client()

            insert_data = {
                "id": str(uuid4()),
                "conversation_id": str(message.conversation_id),
                "created_at": datetime.utcnow().isoformat(),
                **message.model_dump(exclude={"conversation_id"}, exclude_none=True)
            }

            result = client.table("employee_conversation_messages").insert(insert_data).execute()

            if not result.data:
                raise StorageError("Failed to save message")

            # Increment total_messages count in employee_profiles
            await self._increment_message_count(message.conversation_id)

            logger.debug(f"Saved message for conversation: {message.conversation_id}")

            return ConversationMessage(**result.data[0])

        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise StorageError(
                f"Failed to save message: {str(e)}",
                details={"error": str(e)}
            )

    async def _increment_message_count(self, conversation_id: UUID):
        """Increment the total_messages count for a conversation."""
        try:
            client = await self._get_client()

            # Get current count
            result = client.table("employee_profiles").select("total_messages").eq(
                "conversation_id", str(conversation_id)
            ).execute()

            if result.data:
                current_count = result.data[0].get("total_messages", 0)
                client.table("employee_profiles").update({
                    "total_messages": current_count + 1,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("conversation_id", str(conversation_id)).execute()

        except Exception as e:
            logger.warning(f"Failed to increment message count: {e}")

    async def get_conversation_history(
        self,
        conversation_id: UUID,
        limit: Optional[int] = None
    ) -> List[ConversationMessage]:
        """
        Get conversation message history.

        Args:
            conversation_id: Conversation ID
            limit: Optional limit on number of messages

        Returns:
            List of conversation messages

        Raises:
            StorageError: If query fails
        """
        try:
            client = await self._get_client()

            query = client.table("employee_conversation_messages").select("*").eq(
                "conversation_id", str(conversation_id)
            ).order("created_at", desc=False)

            if limit:
                # Get most recent messages within limit
                total_result = client.table("employee_conversation_messages").select(
                    "id", count="exact"
                ).eq("conversation_id", str(conversation_id)).execute()

                total_count = total_result.count or 0
                offset = max(0, total_count - limit)

                query = query.range(offset, offset + limit - 1)

            result = query.execute()

            messages = [ConversationMessage(**item) for item in result.data]

            logger.debug(
                f"Retrieved {len(messages)} messages for conversation: {conversation_id}"
            )

            return messages

        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            raise StorageError(
                f"Failed to get conversation history: {str(e)}",
                details={"error": str(e)}
            )

    # Extraction History Operations

    async def save_extraction(
        self,
        extraction: ExtractionHistoryCreate
    ) -> ExtractionHistory:
        """
        Save an extraction history entry.

        Args:
            extraction: Extraction data to save

        Returns:
            Saved extraction history

        Raises:
            StorageError: If save fails
        """
        try:
            client = await self._get_client()

            insert_data = {
                "id": str(uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                **extraction.model_dump(exclude_none=True)
            }

            result = client.table("employee_extraction_history").insert(insert_data).execute()

            if not result.data:
                raise StorageError("Failed to save extraction")

            logger.debug(
                f"Saved extraction for conversation: {extraction.conversation_id}"
            )

            return ExtractionHistory(**result.data[0])

        except Exception as e:
            logger.error(f"Failed to save extraction: {e}")
            raise StorageError(
                f"Failed to save extraction: {str(e)}",
                details={"error": str(e)}
            )

    async def check_health(self) -> bool:
        """
        Check if database connection is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            client = await self._get_client()
            # Simple query to test connection
            client.table("employee_profiles").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
