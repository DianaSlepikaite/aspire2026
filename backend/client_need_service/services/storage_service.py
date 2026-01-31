"""
Storage service for PostgreSQL database operations.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import asyncpg

from client_need_service.core.database import get_db_pool
from client_need_service.core.exceptions import (
    StorageError,
    ClientNeedNotFoundError,
    ConversationNotFoundError
)
from client_need_service.models.schemas import (
    ClientNeedCreate,
    ClientNeedUpdate,
    ClientNeed,
    ConversationMessageCreate,
    ConversationMessage,
    ConversationStatus,
    ExtractionHistoryCreate,
    ExtractionHistory
)

logger = logging.getLogger(__name__)


class StorageService:
    """Service for database operations with PostgreSQL."""

    def __init__(self):
        """Initialize storage service."""
        self.pool: Optional[asyncpg.Pool] = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Get PostgreSQL connection pool."""
        if self.pool is None:
            self.pool = await get_db_pool()
        return self.pool

    async def create_client_need(
        self,
        data: ClientNeedCreate
    ) -> ClientNeed:
        """
        Create a new client need profile.

        Args:
            data: Client need creation data

        Returns:
            Created client need

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
            result = client.table("client_needs").insert(insert_data).execute()

            if not result.data:
                raise StorageError("Failed to create client need")

            logger.info(f"Created client need: {result.data[0]['id']}")

            return ClientNeed(**result.data[0])

        except Exception as e:
            logger.error(f"Failed to create client need: {e}")
            raise StorageError(
                f"Failed to create client need: {str(e)}",
                details={"error": str(e)}
            )

    async def update_client_need(
        self,
        id: UUID,
        data: ClientNeedUpdate
    ) -> ClientNeed:
        """
        Update an existing client need profile.

        Args:
            id: Client need ID
            data: Update data

        Returns:
            Updated client need

        Raises:
            ClientNeedNotFoundError: If client need not found
            StorageError: If update fails
        """
        try:
            client = await self._get_client()

            # Prepare update data
            update_data = data.model_dump(exclude_none=True)
            update_data["updated_at"] = datetime.utcnow().isoformat()

            # Update in database
            result = client.table("client_needs").update(update_data).eq(
                "id", str(id)
            ).execute()

            if not result.data:
                raise ClientNeedNotFoundError(str(id))

            logger.info(f"Updated client need: {id}")

            return ClientNeed(**result.data[0])

        except ClientNeedNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update client need: {e}")
            raise StorageError(
                f"Failed to update client need: {str(e)}",
                details={"error": str(e)}
            )

    async def get_client_need(self, id: UUID) -> Optional[ClientNeed]:
        """
        Get a client need by ID.

        Args:
            id: Client need ID

        Returns:
            Client need if found, None otherwise

        Raises:
            StorageError: If query fails
        """
        try:
            client = await self._get_client()

            result = client.table("client_needs").select("*").eq(
                "id", str(id)
            ).execute()

            if not result.data:
                return None

            return ClientNeed(**result.data[0])

        except Exception as e:
            logger.error(f"Failed to get client need: {e}")
            raise StorageError(
                f"Failed to get client need: {str(e)}",
                details={"error": str(e)}
            )

    async def get_by_conversation_id(
        self,
        conversation_id: UUID
    ) -> Optional[ClientNeed]:
        """
        Get client need by conversation ID.

        Args:
            conversation_id: Conversation ID

        Returns:
            Client need if found, None otherwise

        Raises:
            StorageError: If query fails
        """
        try:
            client = await self._get_client()

            result = client.table("client_needs").select("*").eq(
                "conversation_id", str(conversation_id)
            ).execute()

            if not result.data:
                return None

            return ClientNeed(**result.data[0])

        except Exception as e:
            logger.error(f"Failed to get client need by conversation ID: {e}")
            raise StorageError(
                f"Failed to get client need: {str(e)}",
                details={"error": str(e)}
            )

    async def list_client_needs(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[ClientNeed], int]:
        """
        List client needs with optional filters and pagination.

        Args:
            filters: Optional filters (status, urgency, etc.)
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            Tuple of (list of client needs, total count)

        Raises:
            StorageError: If query fails
        """
        try:
            client = await self._get_client()

            # Build query
            query = client.table("client_needs").select("*", count="exact")

            # Apply filters
            if filters:
                if "status" in filters:
                    query = query.eq("conversation_status", filters["status"])
                if "urgency" in filters:
                    query = query.eq("urgency_level", filters["urgency"])
                if "min_completeness" in filters:
                    query = query.gte(
                        "profile_completeness_score",
                        filters["min_completeness"]
                    )

            # Apply pagination and ordering
            query = query.order("created_at", desc=True).range(
                offset, offset + limit - 1
            )

            result = query.execute()

            # Parse results
            client_needs = [ClientNeed(**item) for item in result.data]
            total = result.count if result.count is not None else len(client_needs)

            logger.info(f"Listed {len(client_needs)} client needs (total: {total})")

            return client_needs, total

        except Exception as e:
            logger.error(f"Failed to list client needs: {e}")
            raise StorageError(
                f"Failed to list client needs: {str(e)}",
                details={"error": str(e)}
            )

    async def delete_client_need(self, id: UUID) -> bool:
        """
        Delete a client need profile.

        Args:
            id: Client need ID

        Returns:
            True if deleted successfully

        Raises:
            ClientNeedNotFoundError: If client need not found
            StorageError: If deletion fails
        """
        try:
            client = await self._get_client()

            result = client.table("client_needs").delete().eq(
                "id", str(id)
            ).execute()

            if not result.data:
                raise ClientNeedNotFoundError(str(id))

            logger.info(f"Deleted client need: {id}")

            return True

        except ClientNeedNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete client need: {e}")
            raise StorageError(
                f"Failed to delete client need: {str(e)}",
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

            result = client.table("conversation_messages").insert(insert_data).execute()

            if not result.data:
                raise StorageError("Failed to save message")

            # Increment total_messages count in client_needs
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
            result = client.table("client_needs").select("total_messages").eq(
                "conversation_id", str(conversation_id)
            ).execute()

            if result.data:
                current_count = result.data[0].get("total_messages", 0)
                client.table("client_needs").update({
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

            query = client.table("conversation_messages").select("*").eq(
                "conversation_id", str(conversation_id)
            ).order("created_at", desc=False)

            if limit:
                # Get most recent messages within limit
                total_result = client.table("conversation_messages").select(
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

            result = client.table("extraction_history").insert(insert_data).execute()

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
            pool = await self._get_pool()
            # Simple query to test connection
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
