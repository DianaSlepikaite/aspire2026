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
    ExtractionHistory,
    ClientIntakePackage,
    ClientIntakePackageUpdate,
    IntakeStatus
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

    @staticmethod
    def _client_need_from_row(row: asyncpg.Record) -> ClientNeed:
        """
        Convert database row to ClientNeed object, parsing JSONB fields.

        Args:
            row: Database row

        Returns:
            ClientNeed object
        """
        import json

        data = dict(row)

        # JSONB fields that need parsing (must match jsonb_fields in update_client_need)
        jsonb_fields = [
            "required_skills", "preferred_skills", "collaboration_tools",
            "key_challenges", "certifications_required", "required_roles",
            "missing_information", "success_criteria", "risk_factors",
            "communication_preferences", "work_location_details",
            "conversation_transcript", "raw_audio_references", "tags",
        ]

        for field in jsonb_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    data[field] = None

        return ClientNeed(**data)

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
            pool = await self._get_pool()

            # Generate UUID for new record
            new_id = uuid4()
            now = datetime.utcnow()

            # Prepare data
            query = """
                INSERT INTO client_needs (
                    id, conversation_id, created_at, updated_at,
                    conversation_status, total_messages, conversation_started_at,
                    profile_completeness_score, client_name, client_email,
                    client_phone, client_company, source_channel
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING *
            """

            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    query,
                    new_id,
                    data.conversation_id,
                    now,
                    now,
                    ConversationStatus.IN_PROGRESS.value,
                    0,
                    now,
                    0,
                    data.client_name,
                    data.client_email,
                    data.client_phone,
                    data.client_company,
                    data.source_channel
                )

            if not row:
                raise StorageError("Failed to create client need")

            logger.info(f"Created client need: {row['id']}")

            return self._client_need_from_row(row)

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
            pool = await self._get_pool()

            # Get the update fields
            update_dict = data.model_dump(exclude_none=True)

            if not update_dict:
                # If no fields to update, just return the current record
                return await self.get_client_need(id)

            # Build dynamic UPDATE query
            update_fields = []
            values = []
            param_idx = 1

            # JSONB fields that need JSON serialization
            jsonb_fields = {
                "required_skills", "preferred_skills", "collaboration_tools",
                "key_challenges", "certifications_required", "required_roles"
            }

            for key, value in update_dict.items():
                # Convert lists/dicts to JSON for JSONB fields
                if key in jsonb_fields and isinstance(value, (list, dict)):
                    import json
                    update_fields.append(f"{key} = ${param_idx}::jsonb")
                    values.append(json.dumps(value))
                else:
                    update_fields.append(f"{key} = ${param_idx}")
                    values.append(value)
                param_idx += 1

            # Add updated_at
            update_fields.append(f"updated_at = ${param_idx}")
            values.append(datetime.utcnow())
            param_idx += 1

            # Add id for WHERE clause
            values.append(id)

            query = f"""
                UPDATE client_needs
                SET {', '.join(update_fields)}
                WHERE id = ${param_idx}
                RETURNING *
            """

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, *values)

            if not row:
                raise ClientNeedNotFoundError(str(id))

            logger.info(f"Updated client need: {id}")

            return self._client_need_from_row(row)

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
            pool = await self._get_pool()

            query = "SELECT * FROM client_needs WHERE id = $1"

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, id)

            if not row:
                return None

            return self._client_need_from_row(row)

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
            pool = await self._get_pool()

            query = "SELECT * FROM client_needs WHERE conversation_id = $1"

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, conversation_id)

            if not row:
                return None

            return self._client_need_from_row(row)

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
            pool = await self._get_pool()

            # Build WHERE clause
            where_conditions = []
            where_values = []
            param_idx = 1

            if filters:
                if "status" in filters:
                    where_conditions.append(f"conversation_status = ${param_idx}")
                    where_values.append(filters["status"])
                    param_idx += 1

                if "urgency" in filters:
                    where_conditions.append(f"urgency_level = ${param_idx}")
                    where_values.append(filters["urgency"])
                    param_idx += 1

                if "min_completeness" in filters:
                    where_conditions.append(f"profile_completeness_score >= ${param_idx}")
                    where_values.append(filters["min_completeness"])
                    param_idx += 1

            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)

            # Get total count
            count_query = f"SELECT COUNT(*) FROM client_needs {where_clause}"

            # Get paginated results
            data_query = f"""
                SELECT * FROM client_needs
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
            """

            async with pool.acquire() as conn:
                total = await conn.fetchval(count_query, *where_values)
                rows = await conn.fetch(data_query, *where_values, limit, offset)

            client_needs = [self._client_need_from_row(row) for row in rows]

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
            pool = await self._get_pool()

            query = "DELETE FROM client_needs WHERE id = $1 RETURNING id"

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, id)

            if not row:
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
            pool = await self._get_pool()

            new_id = uuid4()
            now = datetime.utcnow()

            query = """
                INSERT INTO conversation_messages (
                    id, conversation_id, role, content, created_at
                )
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            """

            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    query,
                    new_id,
                    message.conversation_id,
                    message.role,
                    message.content,
                    now
                )

            if not row:
                raise StorageError("Failed to save message")

            # Increment total_messages count in client_needs
            await self._increment_message_count(message.conversation_id)

            logger.debug(f"Saved message for conversation: {message.conversation_id}")

            return ConversationMessage(**dict(row))

        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            raise StorageError(
                f"Failed to save message: {str(e)}",
                details={"error": str(e)}
            )

    async def _increment_message_count(self, conversation_id: UUID):
        """Increment the total_messages count for a conversation."""
        try:
            pool = await self._get_pool()

            query = """
                UPDATE client_needs
                SET total_messages = total_messages + 1,
                    updated_at = $2
                WHERE conversation_id = $1
            """

            async with pool.acquire() as conn:
                await conn.execute(query, conversation_id, datetime.utcnow())

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
            pool = await self._get_pool()

            if limit:
                query = """
                    SELECT * FROM conversation_messages
                    WHERE conversation_id = $1
                    ORDER BY created_at ASC
                    LIMIT $2
                """
                async with pool.acquire() as conn:
                    rows = await conn.fetch(query, conversation_id, limit)
            else:
                query = """
                    SELECT * FROM conversation_messages
                    WHERE conversation_id = $1
                    ORDER BY created_at ASC
                """
                async with pool.acquire() as conn:
                    rows = await conn.fetch(query, conversation_id)

            messages = [ConversationMessage(**dict(row)) for row in rows]

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
            pool = await self._get_pool()

            new_id = uuid4()
            now = datetime.utcnow()

            query = """
                INSERT INTO extraction_history (
                    id, conversation_id, message_number, extracted_fields,
                    completeness_score, created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING *
            """

            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    query,
                    new_id,
                    extraction.conversation_id,
                    extraction.message_number,
                    extraction.extracted_fields,
                    extraction.completeness_score,
                    now
                )

            if not row:
                raise StorageError("Failed to save extraction")

            logger.debug(
                f"Saved extraction for conversation: {extraction.conversation_id}"
            )

            return ExtractionHistory(**dict(row))

        except Exception as e:
            logger.error(f"Failed to save extraction: {e}")
            raise StorageError(
                f"Failed to save extraction: {str(e)}",
                details={"error": str(e)}
            )

    # Intake Package Operations

    async def create_intake_package(
        self,
        data: Dict[str, Any]
    ) -> ClientIntakePackage:
        """
        Create a new intake package.

        Args:
            data: Intake package data dictionary

        Returns:
            Created intake package

        Raises:
            StorageError: If creation fails
        """
        try:
            pool = await self._get_pool()

            new_id = uuid4()
            now = datetime.utcnow()

            query = """
                INSERT INTO intake_packages (
                    id, created_at, updated_at, status, source_type,
                    client_name, client_email, raw_content, normalized_content,
                    metadata, processing_notes, audit_trail
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING *
            """

            import json

            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    query,
                    new_id,
                    now,
                    now,
                    data.get("status", IntakeStatus.PENDING.value),
                    data["source_type"],
                    data.get("client_name"),
                    data.get("client_email"),
                    data.get("raw_content"),
                    json.dumps(data.get("normalized_content")) if data.get("normalized_content") else None,
                    json.dumps(data.get("metadata")) if data.get("metadata") else None,
                    data.get("processing_notes"),
                    json.dumps(data.get("audit_trail", []))
                )

            if not row:
                raise StorageError("Failed to create intake package")

            logger.info(f"Created intake package: {row['id']}")

            return ClientIntakePackage.from_db_row(dict(row))

        except Exception as e:
            logger.error(f"Failed to create intake package: {e}")
            raise StorageError(
                f"Failed to create intake package: {str(e)}",
                details={"error": str(e)}
            )

    async def get_intake_package(self, id: UUID) -> Optional[ClientIntakePackage]:
        """
        Get an intake package by ID.

        Args:
            id: Intake package ID

        Returns:
            Intake package if found, None otherwise

        Raises:
            StorageError: If query fails
        """
        try:
            pool = await self._get_pool()

            query = "SELECT * FROM intake_packages WHERE id = $1"

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, id)

            if not row:
                return None

            return ClientIntakePackage.from_db_row(dict(row))

        except Exception as e:
            logger.error(f"Failed to get intake package: {e}")
            raise StorageError(
                f"Failed to get intake package: {str(e)}",
                details={"error": str(e)}
            )

    async def update_intake_package(
        self,
        id: UUID,
        data: ClientIntakePackageUpdate
    ) -> ClientIntakePackage:
        """
        Update an intake package.

        Args:
            id: Intake package ID
            data: Update data

        Returns:
            Updated intake package

        Raises:
            StorageError: If update fails
        """
        try:
            pool = await self._get_pool()

            update_dict = data.model_dump(exclude_none=True)

            if not update_dict:
                return await self.get_intake_package(id)

            import json

            # Build dynamic UPDATE query
            update_fields = []
            values = []
            param_idx = 1

            for key, value in update_dict.items():
                if key in ["normalized_content", "audit_trail"]:
                    value = json.dumps(value)

                update_fields.append(f"{key} = ${param_idx}")
                values.append(value)
                param_idx += 1

            # Add updated_at
            update_fields.append(f"updated_at = ${param_idx}")
            values.append(datetime.utcnow())
            param_idx += 1

            # Add id for WHERE clause
            values.append(id)

            query = f"""
                UPDATE intake_packages
                SET {', '.join(update_fields)}
                WHERE id = ${param_idx}
                RETURNING *
            """

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, *values)

            if not row:
                raise StorageError(f"Intake package not found: {id}")

            logger.info(f"Updated intake package: {id}")

            return ClientIntakePackage.from_db_row(dict(row))

        except Exception as e:
            logger.error(f"Failed to update intake package: {e}")
            raise StorageError(
                f"Failed to update intake package: {str(e)}",
                details={"error": str(e)}
            )

    async def list_intake_packages(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[ClientIntakePackage], int]:
        """
        List intake packages with optional filters and pagination.

        Args:
            filters: Optional filters (status, source_type, etc.)
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            Tuple of (list of intake packages, total count)

        Raises:
            StorageError: If query fails
        """
        try:
            pool = await self._get_pool()

            # Build WHERE clause
            where_conditions = []
            where_values = []
            param_idx = 1

            if filters:
                if "status" in filters:
                    where_conditions.append(f"status = ${param_idx}")
                    where_values.append(filters["status"])
                    param_idx += 1

                if "source_type" in filters:
                    where_conditions.append(f"source_type = ${param_idx}")
                    where_values.append(filters["source_type"])
                    param_idx += 1

                if "client_email" in filters:
                    where_conditions.append(f"client_email = ${param_idx}")
                    where_values.append(filters["client_email"])
                    param_idx += 1

            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)

            # Get total count
            count_query = f"SELECT COUNT(*) FROM intake_packages {where_clause}"

            # Get paginated results
            data_query = f"""
                SELECT * FROM intake_packages
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
            """

            async with pool.acquire() as conn:
                total = await conn.fetchval(count_query, *where_values)
                rows = await conn.fetch(data_query, *where_values, limit, offset)

            intake_packages = [ClientIntakePackage.from_db_row(dict(row)) for row in rows]

            logger.info(f"Listed {len(intake_packages)} intake packages (total: {total})")

            return intake_packages, total

        except Exception as e:
            logger.error(f"Failed to list intake packages: {e}")
            raise StorageError(
                f"Failed to list intake packages: {str(e)}",
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
