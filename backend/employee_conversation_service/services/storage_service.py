"""
Storage service for PostgreSQL database operations.
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

import asyncpg

from employee_conversation_service.core.database import get_db_pool
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

# Table names
PROFILES_TABLE = "employee_agent.employee_profiles"
MESSAGES_TABLE = "employee_agent.employee_conversation_messages"
EXTRACTIONS_TABLE = "employee_agent.employee_extraction_history"


def _jsonb_safe(value):
    """Make a value safe for JSONB storage (JSON-serializable)."""
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {k: _jsonb_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonb_safe(item) for item in value]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return float(value)
    return value


def _prepare_value(value):
    """Prepare a single value for database insertion."""
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (dict, list)):
        # Dicts and lists go to JSONB columns - make them JSON-safe
        return _jsonb_safe(value)
    return value


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
            pool = await self._get_pool()

            now = datetime.utcnow()
            profile_id = uuid4()

            # Base fields with native types
            insert_data = {
                "id": profile_id,
                "conversation_id": data.conversation_id,
                "created_at": now,
                "updated_at": now,
                "conversation_status": ConversationStatus.IN_PROGRESS.value,
                "total_messages": 0,
                "conversation_started_at": now,
                "profile_completeness_score": 0,
            }

            # Add non-None fields from creation data
            profile_data = data.model_dump(
                exclude={"conversation_id"},
                exclude_none=True
            )
            for key, value in profile_data.items():
                insert_data[key] = _prepare_value(value)

            columns = list(insert_data.keys())
            placeholders = [f"${i+1}" for i in range(len(columns))]
            values = list(insert_data.values())

            query = f"""
                INSERT INTO {PROFILES_TABLE} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, *values)

            if not row:
                raise StorageError("Failed to create employee profile")

            logger.info(f"Created employee profile: {row['id']}")

            return EmployeeProfile(**dict(row))

        except StorageError:
            raise
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
            pool = await self._get_pool()

            update_data = data.model_dump(exclude_none=True)
            update_data["updated_at"] = datetime.utcnow()

            set_clauses = []
            values = [id]  # $1 is always the id

            for i, (key, value) in enumerate(update_data.items(), start=2):
                set_clauses.append(f"{key} = ${i}")
                values.append(_prepare_value(value))

            query = f"""
                UPDATE {PROFILES_TABLE}
                SET {', '.join(set_clauses)}
                WHERE id = $1
                RETURNING *
            """

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, *values)

            if not row:
                raise EmployeeProfileNotFoundError(str(id))

            logger.info(f"Updated employee profile: {id}")

            return EmployeeProfile(**dict(row))

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
            pool = await self._get_pool()

            query = f"SELECT * FROM {PROFILES_TABLE} WHERE id = $1"

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, id)

            if not row:
                return None

            return EmployeeProfile(**dict(row))

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
            pool = await self._get_pool()

            query = f"SELECT * FROM {PROFILES_TABLE} WHERE conversation_id = $1"

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, conversation_id)

            if not row:
                return None

            return EmployeeProfile(**dict(row))

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
            pool = await self._get_pool()

            conditions = []
            values = []
            param_idx = 1

            if filters:
                if "status" in filters:
                    conditions.append(f"conversation_status = ${param_idx}")
                    values.append(filters["status"])
                    param_idx += 1
                if "experience_level" in filters:
                    conditions.append(f"experience_level = ${param_idx}")
                    values.append(filters["experience_level"])
                    param_idx += 1
                if "min_completeness" in filters:
                    conditions.append(f"profile_completeness_score >= ${param_idx}")
                    values.append(filters["min_completeness"])
                    param_idx += 1
                if "bench_status" in filters:
                    conditions.append(f"bench_status = ${param_idx}")
                    values.append(filters["bench_status"])
                    param_idx += 1
                if "career_track" in filters:
                    conditions.append(f"career_track = ${param_idx}")
                    values.append(filters["career_track"])
                    param_idx += 1

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            # Count query
            count_query = f"SELECT COUNT(*) FROM {PROFILES_TABLE} {where_clause}"

            # Data query
            data_query = f"""
                SELECT * FROM {PROFILES_TABLE}
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
            """

            async with pool.acquire() as conn:
                total = await conn.fetchval(count_query, *values)
                rows = await conn.fetch(data_query, *values, limit, offset)

            profiles = [EmployeeProfile(**dict(row)) for row in rows]

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
            pool = await self._get_pool()

            query = f"DELETE FROM {PROFILES_TABLE} WHERE id = $1 RETURNING id"

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, id)

            if not row:
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
            pool = await self._get_pool()

            now = datetime.utcnow()
            msg_id = uuid4()

            insert_data = {
                "id": msg_id,
                "conversation_id": message.conversation_id,
                "created_at": now,
            }

            msg_data = message.model_dump(
                exclude={"conversation_id"},
                exclude_none=True
            )
            for key, value in msg_data.items():
                insert_data[key] = _prepare_value(value)

            columns = list(insert_data.keys())
            placeholders = [f"${i+1}" for i in range(len(columns))]
            values = list(insert_data.values())

            query = f"""
                INSERT INTO {MESSAGES_TABLE} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, *values)

            if not row:
                raise StorageError("Failed to save message")

            # Increment total_messages count in employee_profiles
            await self._increment_message_count(message.conversation_id)

            logger.debug(f"Saved message for conversation: {message.conversation_id}")

            return ConversationMessage(**dict(row))

        except StorageError:
            raise
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

            query = f"""
                UPDATE {PROFILES_TABLE}
                SET total_messages = total_messages + 1,
                    updated_at = now()
                WHERE conversation_id = $1
            """

            async with pool.acquire() as conn:
                await conn.execute(query, conversation_id)

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
                # Get the most recent N messages, ordered ascending
                query = f"""
                    SELECT * FROM (
                        SELECT * FROM {MESSAGES_TABLE}
                        WHERE conversation_id = $1
                        ORDER BY created_at DESC
                        LIMIT $2
                    ) sub
                    ORDER BY created_at ASC
                """
                async with pool.acquire() as conn:
                    rows = await conn.fetch(query, conversation_id, limit)
            else:
                query = f"""
                    SELECT * FROM {MESSAGES_TABLE}
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

            now = datetime.utcnow()
            extraction_id = uuid4()

            insert_data = {
                "id": extraction_id,
                "created_at": now,
            }

            extraction_data = extraction.model_dump(exclude_none=True)
            for key, value in extraction_data.items():
                insert_data[key] = _prepare_value(value)

            columns = list(insert_data.keys())
            placeholders = [f"${i+1}" for i in range(len(columns))]
            values = list(insert_data.values())

            query = f"""
                INSERT INTO {EXTRACTIONS_TABLE} ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
                RETURNING *
            """

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, *values)

            if not row:
                raise StorageError("Failed to save extraction")

            logger.debug(
                f"Saved extraction for conversation: {extraction.conversation_id}"
            )

            return ExtractionHistory(**dict(row))

        except StorageError:
            raise
        except Exception as e:
            logger.error(f"Failed to save extraction: {e}")
            raise StorageError(
                f"Failed to save extraction: {str(e)}",
                details={"error": str(e)}
            )

    # Employee Lookup Operations

    async def find_employee_profiles_by_identifier(
        self,
        employee_id: Optional[str] = None,
        employee_email: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> tuple[List[EmployeeProfile], int]:
        """
        Find employee profiles by employee_id or employee_email.

        Args:
            employee_id: PS Employee ID (takes priority)
            employee_email: Employee email
            status_filter: Optional conversation status filter
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Tuple of (list of profiles, total count)
        """
        try:
            pool = await self._get_pool()

            conditions = []
            values = []
            param_idx = 1

            if employee_id:
                conditions.append(f"employee_id = ${param_idx}")
                values.append(employee_id)
                param_idx += 1
            elif employee_email:
                conditions.append(f"employee_email = ${param_idx}")
                values.append(employee_email)
                param_idx += 1
            else:
                return [], 0

            if status_filter:
                conditions.append(f"conversation_status = ${param_idx}")
                values.append(status_filter)
                param_idx += 1

            where_clause = f"WHERE {' AND '.join(conditions)}"

            count_query = f"SELECT COUNT(*) FROM {PROFILES_TABLE} {where_clause}"

            data_query = f"""
                SELECT * FROM {PROFILES_TABLE}
                {where_clause}
                ORDER BY conversation_completed_at DESC NULLS LAST, created_at DESC
                LIMIT ${param_idx} OFFSET ${param_idx + 1}
            """

            async with pool.acquire() as conn:
                total = await conn.fetchval(count_query, *values)
                rows = await conn.fetch(data_query, *values, limit, offset)

            profiles = [EmployeeProfile(**dict(row)) for row in rows]

            logger.info(
                f"Found {len(profiles)} profiles for employee lookup (total: {total})"
            )

            return profiles, total

        except Exception as e:
            logger.error(f"Failed to find employee profiles by identifier: {e}")
            raise StorageError(
                f"Failed to find employee profiles: {str(e)}",
                details={"error": str(e)}
            )

    async def get_latest_completed_profile(
        self,
        employee_id: Optional[str] = None,
        employee_email: Optional[str] = None
    ) -> Optional[EmployeeProfile]:
        """
        Get the most recently completed profile for an employee.

        Args:
            employee_id: PS Employee ID (takes priority)
            employee_email: Employee email

        Returns:
            Most recent completed profile, or None
        """
        try:
            pool = await self._get_pool()

            if employee_id:
                query = f"""
                    SELECT * FROM {PROFILES_TABLE}
                    WHERE employee_id = $1 AND conversation_status = 'completed'
                    ORDER BY conversation_completed_at DESC
                    LIMIT 1
                """
                param = employee_id
            elif employee_email:
                query = f"""
                    SELECT * FROM {PROFILES_TABLE}
                    WHERE employee_email = $1 AND conversation_status = 'completed'
                    ORDER BY conversation_completed_at DESC
                    LIMIT 1
                """
                param = employee_email
            else:
                return None

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, param)

            if not row:
                return None

            return EmployeeProfile(**dict(row))

        except Exception as e:
            logger.error(f"Failed to get latest completed profile: {e}")
            raise StorageError(
                f"Failed to get latest completed profile: {str(e)}",
                details={"error": str(e)}
            )

    async def get_in_progress_conversation(
        self,
        employee_id: Optional[str] = None,
        employee_email: Optional[str] = None
    ) -> Optional[EmployeeProfile]:
        """
        Get the most recent in-progress conversation for an employee.

        Args:
            employee_id: PS Employee ID (takes priority)
            employee_email: Employee email

        Returns:
            Most recent in-progress profile, or None
        """
        try:
            pool = await self._get_pool()

            if employee_id:
                query = f"""
                    SELECT * FROM {PROFILES_TABLE}
                    WHERE employee_id = $1 AND conversation_status = 'in_progress'
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                param = employee_id
            elif employee_email:
                query = f"""
                    SELECT * FROM {PROFILES_TABLE}
                    WHERE employee_email = $1 AND conversation_status = 'in_progress'
                    ORDER BY created_at DESC
                    LIMIT 1
                """
                param = employee_email
            else:
                return None

            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, param)

            if not row:
                return None

            return EmployeeProfile(**dict(row))

        except Exception as e:
            logger.error(f"Failed to get in-progress conversation: {e}")
            raise StorageError(
                f"Failed to get in-progress conversation: {str(e)}",
                details={"error": str(e)}
            )

    async def get_conversation_count_for_employee(
        self,
        employee_id: Optional[str] = None,
        employee_email: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Get conversation counts grouped by status for an employee.

        Args:
            employee_id: PS Employee ID (takes priority)
            employee_email: Employee email

        Returns:
            Dict like {"completed": 3, "in_progress": 1, "total": 4}
        """
        try:
            pool = await self._get_pool()

            if employee_id:
                query = f"""
                    SELECT conversation_status, COUNT(*) as cnt
                    FROM {PROFILES_TABLE}
                    WHERE employee_id = $1
                    GROUP BY conversation_status
                """
                param = employee_id
            elif employee_email:
                query = f"""
                    SELECT conversation_status, COUNT(*) as cnt
                    FROM {PROFILES_TABLE}
                    WHERE employee_email = $1
                    GROUP BY conversation_status
                """
                param = employee_email
            else:
                return {"total": 0}

            async with pool.acquire() as conn:
                rows = await conn.fetch(query, param)

            counts: Dict[str, int] = {}
            total = 0
            for row in rows:
                status = row["conversation_status"]
                count = row["cnt"]
                counts[status] = count
                total += count

            counts["total"] = total

            return counts

        except Exception as e:
            logger.error(f"Failed to get conversation count for employee: {e}")
            raise StorageError(
                f"Failed to get conversation count: {str(e)}",
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
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
