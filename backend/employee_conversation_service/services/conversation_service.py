"""
Conversation service for employee profile building via chat.
"""

import logging
import re
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import (
    ConversationError,
    ConversationNotFoundError,
)
from employee_conversation_service.models.schemas import (
    ConversationStartRequest,
    ConversationStartResponse,
    MessageRequest,
    MessageResponse,
    ConversationStatusResponse,
    ConversationCompleteResponse,
    ConversationHistory,
    ConversationMessage,
    ConversationStatus,
    MessageType,
    ExtractionUpdate,
    EmployeeProfileCreate,
    EmployeeProfileUpdate,
)
from employee_conversation_service.services.azure_openai_service import (
    AzureOpenAIService,
)
from employee_conversation_service.services.storage_service import StorageService
from employee_conversation_service.services.speech_service import SpeechService
from employee_conversation_service.services.skill_extraction_service import SkillExtractionService

logger = logging.getLogger(__name__)


class ConversationService:
    """Manage employee conversations (start, message, status, complete, history)."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.openai_service = AzureOpenAIService()
        self.storage_service = StorageService()
        self.speech_service = SpeechService()
        self.extraction_service = SkillExtractionService()

    async def start_conversation(
        self, request: ConversationStartRequest
    ) -> ConversationStartResponse:
        """Start a new employee conversation."""
        try:
            conversation_id = uuid4()
            profile_data = EmployeeProfileCreate(
                full_name=request.employee_name,
                email=request.employee_email,
                phone=request.employee_phone,
                profile_completeness_score=0,
            )
            profile = await self.storage_service.create_employee_profile(profile_data)
            employee_profile_id = profile.id

            await self.storage_service.create_employee_conversation(
                conversation_id=conversation_id,
                employee_profile_id=employee_profile_id,
                source_channel=request.source_channel or "web",
            )

            greeting_text = await self.openai_service.generate_greeting()
            await self.storage_service.save_employee_message(
                conversation_id=conversation_id,
                role="assistant",
                content=greeting_text,
                message_type=MessageType.TEXT.value,
            )

            audio_url: Optional[str] = None
            if getattr(self.settings, "ENABLE_TEXT_TO_SPEECH", True):
                try:
                    await self.speech_service.synthesize_speech(greeting_text)
                except Exception as e:
                    logger.warning("Failed to synthesize greeting: %s", e)

            return ConversationStartResponse(
                conversation_id=conversation_id,
                employee_profile_id=employee_profile_id,
                greeting_message=greeting_text,
                audio_url=audio_url,
            )
        except Exception as e:
            logger.exception("Failed to start conversation: %s", e)
            raise ConversationError(
                f"Failed to start conversation: {str(e)}",
                details={"error": str(e)},
            )

    async def send_message(
        self, conversation_id: UUID, request: MessageRequest
    ) -> MessageResponse:
        """Process a message and return assistant reply."""
        row = await self.storage_service.get_employee_conversation_by_conversation_id(
            conversation_id
        )
        if not row:
            raise ConversationNotFoundError(str(conversation_id))

        if not row["employee_profile_id"]:
            profile_data = EmployeeProfileCreate(profile_completeness_score=0)
            profile = await self.storage_service.create_employee_profile(profile_data)
            await self.storage_service.update_employee_conversation_status(
                conversation_id=conversation_id,
                status="in_progress",
                employee_profile_id=profile.id,
            )
            row = await self.storage_service.get_employee_conversation_by_conversation_id(
                conversation_id
            )

        await self.storage_service.save_employee_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            message_type=request.message_type.value,
        )

        explicit_updates = self._extract_explicit_updates(request.message)

        if explicit_updates and row["employee_profile_id"]:
            profile = await self.storage_service.get_employee_profile(
                row["employee_profile_id"]
            )
            update_data = {}
            extraction_updates: List[ExtractionUpdate] = []
            if profile:
                for field, value in explicit_updates.items():
                    if value and value != profile.__dict__.get(field):
                        update_data[field] = value
                        extraction_updates.append(
                            ExtractionUpdate(
                                field_name=field,
                                field_value=value,
                                confidence=1.0,
                            )
                        )
                if update_data:
                    merged_data = {**profile.__dict__, **update_data}
                    update_data["profile_completeness_score"] = (
                        self.extraction_service.calculate_completeness(merged_data)
                    )
                    await self.storage_service.update_employee_profile(
                        row["employee_profile_id"], EmployeeProfileUpdate(**update_data)
                    )

                updated_profile = await self.storage_service.get_employee_profile(
                    row["employee_profile_id"]
                )
                profile_completeness = (
                    updated_profile.profile_completeness_score if updated_profile else 0
                )
                missing_fields = (
                    self.extraction_service.get_missing_fields(updated_profile.__dict__)
                    if updated_profile
                    else []
                )
            else:
                profile_completeness = 0
                missing_fields = []

            fields = ", ".join(explicit_updates.keys())
            assistant_message = (
                f"Got it — I’ve updated your {fields}. "
                "Let me know if you want to change anything else."
            )

            msg_id = await self.storage_service.save_employee_message(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_message,
                message_type=MessageType.TEXT.value,
            )

            return MessageResponse(
                conversation_id=conversation_id,
                message_id=msg_id,
                employee_profile_id=row["employee_profile_id"],
                assistant_message=assistant_message,
                audio_url=None,
                extraction_updates=extraction_updates if extraction_updates else None,
                profile_completeness=profile_completeness,
                missing_fields=missing_fields,
                can_complete=profile_completeness
                >= getattr(self.settings, "MIN_PROFILE_COMPLETENESS_FOR_COMPLETION", 70),
            )

        messages = await self.storage_service.get_employee_messages(conversation_id)
        api_messages = self.openai_service.build_conversation_history(messages)
        openai_response = await self.openai_service.generate_response(
            messages=api_messages, use_functions=False
        )
        assistant_message = openai_response.get("content", "")

        msg_id = await self.storage_service.save_employee_message(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_message,
            message_type=MessageType.TEXT.value,
        )

        # Extract profile information from conversation
        profile_completeness = 0
        missing_fields: List[str] = []
        extraction_updates: List[ExtractionUpdate] = []

        if row["employee_profile_id"]:
            try:
                # Get all messages and extract profile information
                all_messages = await self.storage_service.get_employee_messages(conversation_id)
                message_dicts = self.openai_service.build_conversation_history(all_messages)

                # Extract profile data from conversation
                extracted_data = await self.extraction_service.extract_from_conversation(message_dicts)

                if extracted_data:
                    # Get current profile
                    profile = await self.storage_service.get_employee_profile(
                        row["employee_profile_id"]
                    )

                    # Build update data
                    update_data = {}

                    for field, value in extracted_data.items():
                        if value and value != profile.__dict__.get(field):
                            update_data[field] = value
                            extraction_updates.append(
                                ExtractionUpdate(
                                    field_name=field,
                                    field_value=value,
                                    confidence=0.85
                                )
                            )

                    merged_data = {**profile.__dict__, **update_data}
                    profile_completeness = self.extraction_service.calculate_completeness(merged_data)
                    missing_fields = self.extraction_service.get_missing_fields(merged_data)

                    # Update profile if there are changes
                    if update_data:
                        update_data["profile_completeness_score"] = profile_completeness
                        profile_update = EmployeeProfileUpdate(**update_data)
                        await self.storage_service.update_employee_profile(
                            row["employee_profile_id"],
                            profile_update
                        )

                    # Get updated profile
                    updated_profile = await self.storage_service.get_employee_profile(
                        row["employee_profile_id"]
                    )
                    if updated_profile:
                        profile_completeness = updated_profile.profile_completeness_score or profile_completeness
                        if not missing_fields:
                            missing_fields = self.extraction_service.get_missing_fields(
                                updated_profile.__dict__
                            )

            except Exception as e:
                logger.exception(f"Extraction failed: {e}")
                # Continue without extraction if it fails
                profile = await self.storage_service.get_employee_profile(
                    row["employee_profile_id"]
                )
                if profile:
                    profile_completeness = profile.profile_completeness_score or 0
                    missing_fields = self.extraction_service.get_missing_fields(profile.__dict__)

        return MessageResponse(
            conversation_id=conversation_id,
            message_id=msg_id,
            employee_profile_id=row["employee_profile_id"],
            assistant_message=assistant_message,
            audio_url=None,
            extraction_updates=extraction_updates if extraction_updates else None,
            profile_completeness=profile_completeness,
            missing_fields=missing_fields,
            can_complete=profile_completeness
            >= getattr(self.settings, "MIN_PROFILE_COMPLETENESS_FOR_COMPLETION", 70),
        )

    def _extract_explicit_updates(self, message: str) -> Dict[str, Any]:
        updates: Dict[str, Any] = {}
        text = (message or "").strip()
        if not text:
            return updates

        email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.IGNORECASE)
        if email_match:
            updates["email"] = email_match.group(0)

        phone_match = re.search(r"(\+\d[\d\s().-]{6,}\d)", text)
        if phone_match:
            updates["phone"] = phone_match.group(1).strip()

        role_match = re.search(
            r"(?:my\s+)?(?:role|title|position)\s*(?:is|to be|as)\s*([^,.\\n]+)",
            text,
            re.IGNORECASE,
        )
        if role_match:
            updates["preferred_roles"] = [role_match.group(1).strip()]

        skills_match = re.search(
            r"(?:skills|skill set)\s*(?:are|include|:)\s*([^\\n]+)",
            text,
            re.IGNORECASE,
        )
        if skills_match:
            skills = [s.strip() for s in skills_match.group(1).split(",") if s.strip()]
            if skills:
                updates["skills"] = skills

        return updates

    async def get_conversation_status(
        self, conversation_id: UUID
    ) -> ConversationStatusResponse:
        """Get conversation status."""
        row = await self.storage_service.get_employee_conversation_by_conversation_id(
            conversation_id
        )
        if not row:
            raise ConversationNotFoundError(str(conversation_id))

        profile_completeness = 0
        if row["employee_profile_id"]:
            profile = await self.storage_service.get_employee_profile(
                row["employee_profile_id"]
            )
            if profile:
                profile_completeness = profile.profile_completeness_score or 0

        started = row["conversation_started_at"] or datetime.now(timezone.utc)
        if isinstance(started, datetime) and started.tzinfo is None:
            started = started.replace(tzinfo=timezone.utc)
        duration_minutes = int(
            (datetime.now(timezone.utc) - started).total_seconds() / 60
        )

        return ConversationStatusResponse(
            conversation_id=conversation_id,
            status=ConversationStatus(row["conversation_status"] or "in_progress"),
            total_messages=row["total_messages"] or 0,
            profile_completeness=profile_completeness,
            missing_fields=[],
            duration_minutes=duration_minutes,
            can_complete=profile_completeness
            >= getattr(self.settings, "MIN_PROFILE_COMPLETENESS_FOR_COMPLETION", 70),
            conversation_started_at=started,
            last_message_at=None,
        )

    async def complete_conversation(
        self, conversation_id: UUID
    ) -> ConversationCompleteResponse:
        """Mark conversation complete and return summary."""
        row = await self.storage_service.get_employee_conversation_by_conversation_id(
            conversation_id
        )
        if not row:
            raise ConversationNotFoundError(str(conversation_id))

        await self.storage_service.update_employee_conversation_status(
            conversation_id=conversation_id, status="completed"
        )

        profile_completeness = 0
        if row["employee_profile_id"]:
            profile = await self.storage_service.get_employee_profile(
                row["employee_profile_id"]
            )
            if profile:
                profile_completeness = profile.profile_completeness_score or 0

        summary = (
            f"Conversation completed. Profile completeness: {profile_completeness}%."
        )

        return ConversationCompleteResponse(
            conversation_id=conversation_id,
            employee_profile_id=row["employee_profile_id"],
            status=ConversationStatus.COMPLETED,
            profile_completeness=profile_completeness,
            summary=summary,
        )

    async def get_conversation_history(
        self, conversation_id: UUID
    ) -> ConversationHistory:
        """Get full message history."""
        row = await self.storage_service.get_employee_conversation_by_conversation_id(
            conversation_id
        )
        if not row:
            raise ConversationNotFoundError(str(conversation_id))

        rows = await self.storage_service.get_employee_messages(conversation_id)
        messages = [
            ConversationMessage(
                id=r["id"],
                role=r["role"],
                content=r["content"],
                message_type=r.get("message_type") or "text",
                created_at=r["created_at"],
            )
            for r in rows
        ]
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=messages,
        )
