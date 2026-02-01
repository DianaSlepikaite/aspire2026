"""
Storage service for employee profiles and documents (PostgreSQL).
"""

import json
import logging
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime, timezone
import asyncpg

from employee_conversation_service.core.database import get_db_pool
from employee_conversation_service.models.schemas import (
    EmployeeProfile,
    EmployeeProfileCreate,
    EmployeeProfileUpdate,
    EmployeeDocument,
    EmployeeDocumentCreate,
)
from employee_conversation_service.core.exceptions import (
    DocumentNotFoundError,
    EmployeeProfileNotFoundError,
    StorageError,
    ConversationNotFoundError,
)

logger = logging.getLogger(__name__)


def _serialize_jsonb(value) -> Optional[str]:
    """Serialize value to JSON string for JSONB columns."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value)


def _doc_from_row(row: asyncpg.Record) -> EmployeeDocument:
    """Build EmployeeDocument from DB row."""
    return EmployeeDocument(
        id=row["id"],
        file_name=row["file_name"],
        mime_type=row["mime_type"],
        raw_text=row["raw_text"],
        source=row["source"],
        employee_profile_id=row["employee_profile_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _profile_from_row(row: asyncpg.Record) -> EmployeeProfile:
    """Build EmployeeProfile from DB row; parse JSONB fields."""
    data = dict(row)
    for key in (
        "skills",
        "certifications",
        "education",
        "experience",
        "preferred_roles",
    ):
        if key in data and isinstance(data[key], str):
            try:
                data[key] = json.loads(data[key]) if data[key] else None
            except (json.JSONDecodeError, TypeError):
                data[key] = None
    return EmployeeProfile(**data)


class StorageService:
    """Storage for employee profiles and documents using PostgreSQL."""

    def __init__(self) -> None:
        self.pool: Optional[asyncpg.Pool] = None

    async def _get_pool(self) -> asyncpg.Pool:
        if self.pool is None:
            self.pool = await get_db_pool()
        return self.pool

    async def check_health(self) -> bool:
        """Check if database connection is healthy."""
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error("Database health check failed: %s", e)
            return False

    async def get_document(self, document_id: UUID) -> Optional[EmployeeDocument]:
        """Get an employee document by ID."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, file_name, mime_type, raw_text, source,
                       employee_profile_id, created_at, updated_at
                FROM employee_documents WHERE id = $1
                """,
                document_id,
            )
        if row is None:
            return None
        return _doc_from_row(row)

    async def get_employee_profile(self, profile_id: UUID) -> Optional[EmployeeProfile]:
        """Get an employee profile by ID."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, document_id, full_name, email, phone, summary,
                       experience_years, skills, certifications, education,
                       experience, preferred_roles, profile_completeness_score,
                       created_at, updated_at
                FROM employee_profiles WHERE id = $1
                """,
                profile_id,
            )
        if row is None:
            return None
        return _profile_from_row(row)

    async def create_document(self, data: EmployeeDocumentCreate) -> EmployeeDocument:
        """Create an employee document."""
        pool = await self._get_pool()
        doc_id = uuid4()
        now = datetime.now(timezone.utc)
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO employee_documents
                (id, file_name, mime_type, raw_text, source, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                doc_id,
                data.file_name,
                data.mime_type,
                data.raw_text,
                data.source or "upload",
                now,
                now,
            )
        logger.info("Created document: %s", doc_id)
        return EmployeeDocument(
            id=doc_id,
            file_name=data.file_name,
            mime_type=data.mime_type,
            raw_text=data.raw_text,
            source=data.source,
            employee_profile_id=None,
            created_at=now,
            updated_at=now,
        )

    async def create_employee_profile(
        self, data: EmployeeProfileCreate
    ) -> EmployeeProfile:
        """Create an employee profile."""
        pool = await self._get_pool()
        profile_id = uuid4()
        now = datetime.now(timezone.utc)
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO employee_profiles
                (id, document_id, full_name, email, phone, summary, experience_years,
                 skills, certifications, education, experience, preferred_roles,
                 profile_completeness_score, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                """,
                profile_id,
                data.document_id,
                data.full_name,
                data.email,
                data.phone,
                data.summary,
                data.experience_years,
                _serialize_jsonb(data.skills),
                _serialize_jsonb(data.certifications),
                _serialize_jsonb(data.education),
                _serialize_jsonb(data.experience),
                _serialize_jsonb(data.preferred_roles),
                data.profile_completeness_score or 0,
                now,
                now,
            )
        logger.info("Created employee profile: %s", profile_id)
        return EmployeeProfile(
            id=profile_id,
            document_id=data.document_id,
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            summary=data.summary,
            experience_years=data.experience_years,
            skills=data.skills,
            certifications=data.certifications,
            education=data.education,
            experience=data.experience,
            preferred_roles=data.preferred_roles,
            profile_completeness_score=data.profile_completeness_score or 0,
            created_at=now,
            updated_at=now,
        )

    async def update_employee_profile(
        self, profile_id: UUID, data: EmployeeProfileUpdate
    ) -> EmployeeProfile:
        """Update an employee profile."""
        profile = await self.get_employee_profile(profile_id)
        if not profile:
            raise EmployeeProfileNotFoundError(str(profile_id))
        update = data.model_dump(exclude_none=True)
        if not update:
            return profile

        # Build dynamic UPDATE; only set provided fields
        set_parts = []
        args: list = []
        for key, value in update.items():
            if key in (
                "skills",
                "certifications",
                "education",
                "experience",
                "preferred_roles",
            ):
                value = _serialize_jsonb(value)
            set_parts.append(f"{key} = ${len(args) + 1}")
            args.append(value)
        set_parts.append("updated_at = NOW()")
        args.append(profile_id)
        where_id = len(args)

        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                f"""
                UPDATE employee_profiles
                SET {", ".join(set_parts)}
                WHERE id = ${where_id}
                """,
                *args,
            )
        return (await self.get_employee_profile(profile_id)) or profile

    async def link_document_to_profile(
        self, document_id: UUID, profile_id: UUID
    ) -> None:
        """Link a document to an employee profile."""
        doc = await self.get_document(document_id)
        if not doc:
            raise DocumentNotFoundError(str(document_id))
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE employee_documents
                SET employee_profile_id = $1, updated_at = NOW()
                WHERE id = $2
                """,
                profile_id,
                document_id,
            )
        logger.info("Linked document %s to profile %s", document_id, profile_id)

    async def list_profiles(
        self, limit: int = 20, offset: int = 0
    ) -> List[EmployeeProfile]:
        """List employee profiles (paginated)."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, document_id, full_name, email, phone, summary,
                       experience_years, skills, certifications, education,
                       experience, preferred_roles, profile_completeness_score,
                       created_at, updated_at
                FROM employee_profiles
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
                """,
                limit,
                offset,
            )
        return [_profile_from_row(r) for r in rows]

    # --- Employee conversations ---

    async def create_employee_conversation(
        self,
        conversation_id: UUID,
        employee_profile_id: Optional[UUID] = None,
        source_channel: str = "web",
    ) -> None:
        """Create an employee conversation row."""
        pool = await self._get_pool()
        now = datetime.now(timezone.utc)
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO employee_conversations
                (conversation_id, employee_profile_id, conversation_status, total_messages,
                 conversation_started_at, source_channel, created_at, updated_at)
                VALUES ($1, $2, 'in_progress', 0, $3, $4, $3, $3)
                """,
                conversation_id,
                employee_profile_id,
                now,
                source_channel,
            )
        logger.info("Created employee conversation: %s", conversation_id)

    async def get_employee_conversation_by_conversation_id(
        self, conversation_id: UUID
    ) -> Optional[asyncpg.Record]:
        """Get conversation row by conversation_id."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, conversation_id, employee_profile_id, conversation_status,
                       total_messages, conversation_started_at, conversation_completed_at,
                       source_channel, created_at, updated_at
                FROM employee_conversations WHERE conversation_id = $1
                """,
                conversation_id,
            )
        return row

    async def save_employee_message(
        self, conversation_id: UUID, role: str, content: str, message_type: str = "text"
    ) -> UUID:
        """Save a message and increment total_messages. Returns message id."""
        pool = await self._get_pool()
        msg_id = uuid4()
        now = datetime.now(timezone.utc)
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO employee_conversation_messages
                (id, conversation_id, role, content, message_type, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                msg_id,
                conversation_id,
                role,
                content,
                message_type,
                now,
            )
            await conn.execute(
                """
                UPDATE employee_conversations
                SET total_messages = total_messages + 1, updated_at = $1
                WHERE conversation_id = $2
                """,
                now,
                conversation_id,
            )
        return msg_id

    async def get_employee_messages(
        self, conversation_id: UUID
    ) -> List[asyncpg.Record]:
        """Get all messages for a conversation, ordered by created_at."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, conversation_id, role, content, message_type, created_at
                FROM employee_conversation_messages
                WHERE conversation_id = $1
                ORDER BY created_at ASC
                """,
                conversation_id,
            )
        return list(rows)

    async def update_employee_conversation_status(
        self,
        conversation_id: UUID,
        status: str,
        employee_profile_id: Optional[UUID] = None,
    ) -> None:
        """Update conversation status and optionally link profile."""
        pool = await self._get_pool()
        now = datetime.now(timezone.utc)
        async with pool.acquire() as conn:
            if status == "completed":
                await conn.execute(
                    """
                    UPDATE employee_conversations
                    SET conversation_status = $1, conversation_completed_at = $2,
                        updated_at = $2
                    WHERE conversation_id = $3
                    """,
                    status,
                    now,
                    conversation_id,
                )
            else:
                await conn.execute(
                    """
                    UPDATE employee_conversations
                    SET conversation_status = $1, updated_at = $2
                    WHERE conversation_id = $3
                    """,
                    status,
                    now,
                    conversation_id,
                )
            if employee_profile_id is not None:
                await conn.execute(
                    """
                    UPDATE employee_conversations
                    SET employee_profile_id = $1, updated_at = $2
                    WHERE conversation_id = $3
                    """,
                    employee_profile_id,
                    now,
                    conversation_id,
                )
