"""
Conversation service for orchestrating employee profile conversations.
"""

import logging
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import (
    ConversationError,
    ConversationNotFoundError,
    ConversationTimeoutError
)
from employee_conversation_service.models.schemas import (
    ConversationStartRequest,
    ConversationStartResponse,
    MessageRequest,
    MessageResponse,
    ConversationStatusResponse,
    ConversationCompleteResponse,
    ConversationHistory,
    EmployeeProfileCreate,
    EmployeeProfileUpdate,
    EmployeeProfile,
    EmployeeLookupResponse,
    ConversationSummaryItem,
    ConversationMessageCreate,
    MessageRole,
    MessageType,
    ConversationStatus,
    ExtractionUpdate
)
from employee_conversation_service.services.azure_openai_service import AzureOpenAIService
from employee_conversation_service.services.storage_service import StorageService
from employee_conversation_service.services.skill_extraction_service import SkillExtractionService
from employee_conversation_service.services.speech_service import SpeechService

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations with employees."""

    def __init__(self):
        """Initialize conversation service."""
        self.settings = get_settings()
        self.openai_service = AzureOpenAIService()
        self.storage_service = StorageService()
        self.extraction_service = SkillExtractionService()
        self.speech_service = SpeechService()

    # ── Carry-forward field list ──
    # All fields from EmployeeProfileBase that should be copied to a new profile
    CARRY_FORWARD_FIELDS = [
        "employee_id", "employee_name", "employee_email",
        "location", "career_track", "experience_level",
        "years_at_ps", "years_total_experience",
        "bench_status", "current_assignment", "availability_date",
        "technical_skills", "soft_skills", "domain_expertise",
        "methodologies", "tools_platforms",
        "project_history", "notable_achievements",
        "training_certifications", "current_learning",
        "career_goals", "professional_summary",
        "strengths", "areas_for_growth", "notes",
    ]

    async def start_conversation(
        self,
        request: ConversationStartRequest
    ) -> ConversationStartResponse:
        """
        Start a new conversation session (dispatcher).

        Handles three branches:
        1. Resume an in-progress conversation
        2. Returning identified user with previous data
        3. Brand-new anonymous conversation

        Args:
            request: Conversation start request

        Returns:
            Conversation start response with greeting

        Raises:
            ConversationError: If conversation creation fails
        """
        try:
            # Branch 1: Resume existing conversation
            if request.resume_conversation_id:
                return await self.resume_conversation(request.resume_conversation_id)

            # Branch 2: Identified user — check for existing data
            if request.employee_id or request.employee_email:
                # Check for an existing in-progress conversation
                in_progress = await self.storage_service.get_in_progress_conversation(
                    employee_id=request.employee_id,
                    employee_email=request.employee_email
                )
                if in_progress:
                    await self._abandon_conversation(in_progress)

                # Check for a completed profile to carry forward
                latest = await self.storage_service.get_latest_completed_profile(
                    employee_id=request.employee_id,
                    employee_email=request.employee_email
                )

                # Prefer completed; fallback to abandoned in-progress
                carry_from = latest or in_progress

                if carry_from:
                    return await self._start_returning_user_conversation(request, carry_from)

            # Branch 3: New anonymous user (existing behaviour)
            return await self._start_new_conversation(request)

        except ConversationError:
            raise
        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            raise ConversationError(
                f"Failed to start conversation: {str(e)}",
                details={"error": str(e)}
            )

    async def _start_new_conversation(
        self,
        request: ConversationStartRequest
    ) -> ConversationStartResponse:
        """
        Start a brand-new conversation (original behaviour).

        Args:
            request: Conversation start request

        Returns:
            Conversation start response with greeting
        """
        logger.info("Starting new employee conversation")

        conversation_id = uuid4()

        profile_data = EmployeeProfileCreate(
            conversation_id=conversation_id,
            employee_id=request.employee_id,
            employee_email=request.employee_email,
            source_channel=request.source_channel
        )

        employee_profile = await self.storage_service.create_employee_profile(profile_data)

        greeting_text = await self.openai_service.generate_greeting()

        greeting_msg = ConversationMessageCreate(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=greeting_text,
            message_type=MessageType.TEXT
        )
        await self.storage_service.save_message(greeting_msg)

        audio_url = None
        if self.settings.ENABLE_TEXT_TO_SPEECH:
            try:
                await self.speech_service.synthesize_speech(greeting_text)
                audio_url = None
            except Exception as e:
                logger.warning(f"Failed to synthesize greeting speech: {e}")

        logger.info(f"Started conversation: {conversation_id}")

        return ConversationStartResponse(
            conversation_id=conversation_id,
            employee_profile_id=employee_profile.id,
            greeting_message=greeting_text,
            audio_url=audio_url
        )

    async def _start_returning_user_conversation(
        self,
        request: ConversationStartRequest,
        previous_profile: EmployeeProfile
    ) -> ConversationStartResponse:
        """
        Start a new conversation for a returning user, carrying forward profile data.

        Args:
            request: Conversation start request
            previous_profile: Previous profile to carry data from

        Returns:
            Conversation start response with personalized greeting
        """
        logger.info(
            f"Starting returning-user conversation (carrying from profile {previous_profile.id})"
        )

        conversation_id = uuid4()

        # Build carried-forward data
        prev_data = previous_profile.model_dump(exclude_none=True)
        carry_forward = {
            field: prev_data[field]
            for field in self.CARRY_FORWARD_FIELDS
            if field in prev_data
        }

        # Override identity fields from request if provided
        if request.employee_id:
            carry_forward["employee_id"] = request.employee_id
        if request.employee_email:
            carry_forward["employee_email"] = request.employee_email

        profile_data = EmployeeProfileCreate(
            conversation_id=conversation_id,
            source_channel=request.source_channel,
            **carry_forward
        )

        employee_profile = await self.storage_service.create_employee_profile(profile_data)

        # Calculate initial completeness from carried-forward data
        profile_dict = employee_profile.model_dump(exclude_none=True)
        completeness = self.extraction_service.calculate_completeness_score(profile_dict)

        if completeness > 0:
            await self.storage_service.update_employee_profile(
                employee_profile.id,
                EmployeeProfileUpdate(profile_completeness_score=completeness)
            )

        # Generate personalized greeting
        greeting_text = await self.openai_service.generate_returning_user_greeting(
            profile_dict
        )

        greeting_msg = ConversationMessageCreate(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=greeting_text,
            message_type=MessageType.TEXT
        )
        await self.storage_service.save_message(greeting_msg)

        # Count previous completed conversations
        counts = await self.storage_service.get_conversation_count_for_employee(
            employee_id=request.employee_id,
            employee_email=request.employee_email
        )
        previous_completed = counts.get("completed", 0)

        audio_url = None
        if self.settings.ENABLE_TEXT_TO_SPEECH:
            try:
                await self.speech_service.synthesize_speech(greeting_text)
                audio_url = None
            except Exception as e:
                logger.warning(f"Failed to synthesize greeting speech: {e}")

        logger.info(f"Started returning-user conversation: {conversation_id}")

        return ConversationStartResponse(
            conversation_id=conversation_id,
            employee_profile_id=employee_profile.id,
            greeting_message=greeting_text,
            audio_url=audio_url,
            is_returning_user=True,
            previous_conversation_count=previous_completed,
            profile_completeness=completeness,
        )

    async def resume_conversation(
        self,
        conversation_id: UUID
    ) -> ConversationStartResponse:
        """
        Resume an in-progress conversation.

        Args:
            conversation_id: Conversation ID to resume

        Returns:
            Conversation start response with resume greeting

        Raises:
            ConversationNotFoundError: If conversation not found
            ConversationError: If conversation cannot be resumed
        """
        logger.info(f"Resuming conversation: {conversation_id}")

        employee_profile = await self.storage_service.get_by_conversation_id(conversation_id)
        if not employee_profile:
            raise ConversationNotFoundError(str(conversation_id))

        # Validate status
        if employee_profile.conversation_status != ConversationStatus.IN_PROGRESS:
            raise ConversationError(
                f"Cannot resume conversation with status '{employee_profile.conversation_status.value}'. "
                f"Only in-progress conversations can be resumed.",
                details={
                    "conversation_id": str(conversation_id),
                    "current_status": employee_profile.conversation_status.value
                }
            )

        # Reset timeout by updating conversation_started_at
        await self.storage_service.update_employee_profile(
            employee_profile.id,
            EmployeeProfileUpdate(conversation_started_at=datetime.now(timezone.utc))
        )

        # Fetch recent messages for context
        messages = await self.storage_service.get_conversation_history(
            conversation_id, limit=5
        )
        api_messages = self.openai_service.build_conversation_history(messages)

        # Generate resume greeting
        profile_dict = employee_profile.model_dump(exclude_none=True)
        greeting_text = await self.openai_service.generate_resume_greeting(
            profile_dict, api_messages
        )

        # Save greeting as assistant message
        greeting_msg = ConversationMessageCreate(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=greeting_text,
            message_type=MessageType.TEXT
        )
        await self.storage_service.save_message(greeting_msg)

        logger.info(f"Resumed conversation: {conversation_id}")

        return ConversationStartResponse(
            conversation_id=conversation_id,
            employee_profile_id=employee_profile.id,
            greeting_message=greeting_text,
            is_resumed=True,
            profile_completeness=employee_profile.profile_completeness_score,
        )

    async def _abandon_conversation(self, profile: EmployeeProfile) -> None:
        """
        Mark an in-progress conversation as abandoned.

        Args:
            profile: The employee profile to abandon
        """
        logger.info(f"Abandoning conversation: {profile.conversation_id}")

        await self.storage_service.update_employee_profile(
            profile.id,
            EmployeeProfileUpdate(
                conversation_status=ConversationStatus.ABANDONED,
                conversation_completed_at=datetime.now(timezone.utc)
            )
        )

    async def lookup_employee(
        self,
        employee_id: Optional[str] = None,
        employee_email: Optional[str] = None
    ) -> EmployeeLookupResponse:
        """
        Look up an employee's conversation history.

        Args:
            employee_id: PS Employee ID
            employee_email: Employee email

        Returns:
            EmployeeLookupResponse with conversation history
        """
        profiles, total = await self.storage_service.find_employee_profiles_by_identifier(
            employee_id=employee_id,
            employee_email=employee_email
        )

        if not profiles:
            return EmployeeLookupResponse(
                found=False,
                employee_id=employee_id,
                employee_email=employee_email
            )

        latest_completed = await self.storage_service.get_latest_completed_profile(
            employee_id=employee_id,
            employee_email=employee_email
        )

        in_progress = await self.storage_service.get_in_progress_conversation(
            employee_id=employee_id,
            employee_email=employee_email
        )

        counts = await self.storage_service.get_conversation_count_for_employee(
            employee_id=employee_id,
            employee_email=employee_email
        )

        # Build conversation summaries
        conversations = [
            ConversationSummaryItem(
                conversation_id=p.conversation_id,
                profile_id=p.id,
                conversation_status=p.conversation_status,
                profile_completeness_score=p.profile_completeness_score,
                conversation_started_at=p.conversation_started_at,
                conversation_completed_at=p.conversation_completed_at,
                total_messages=p.total_messages,
            )
            for p in profiles
        ]

        # Use the first profile (most recent) for employee name
        first = profiles[0]

        return EmployeeLookupResponse(
            found=True,
            employee_id=first.employee_id,
            employee_email=first.employee_email,
            employee_name=first.employee_name,
            latest_profile=latest_completed,
            conversation_counts=counts,
            conversations=conversations,
            has_in_progress=in_progress is not None,
            in_progress_conversation_id=(
                in_progress.conversation_id if in_progress else None
            ),
        )

    async def send_message(
        self,
        conversation_id: UUID,
        request: MessageRequest
    ) -> MessageResponse:
        """
        Process a user message in the conversation.

        Args:
            conversation_id: Conversation ID
            request: Message request

        Returns:
            Message response with assistant reply

        Raises:
            ConversationNotFoundError: If conversation not found
            ConversationError: If message processing fails
        """
        try:
            logger.info(f"Processing message for conversation: {conversation_id}")

            # Get employee profile
            employee_profile = await self.storage_service.get_by_conversation_id(conversation_id)
            if not employee_profile:
                raise ConversationNotFoundError(str(conversation_id))

            # Check conversation timeout
            await self._check_timeout(employee_profile)

            # Save user message
            user_msg = ConversationMessageCreate(
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=request.message,
                message_type=request.message_type
            )
            saved_user_msg = await self.storage_service.save_message(user_msg)

            # Get conversation history
            messages = await self.storage_service.get_conversation_history(
                conversation_id,
                limit=self.settings.MAX_CONVERSATION_MESSAGES
            )

            # Build conversation history for OpenAI
            api_messages = self.openai_service.build_conversation_history(messages)

            # Get current extracted data for context
            extracted_data = employee_profile.model_dump(exclude_none=True)

            # Generate response from OpenAI
            openai_response = await self.openai_service.generate_response(
                messages=api_messages,
                use_functions=True,
                extracted_data=extracted_data
            )

            assistant_message = openai_response["content"]
            function_calls = openai_response["function_calls"]

            # Process function calls to extract information
            extraction_updates = []
            if function_calls:
                updates = await self.extraction_service.extract_from_function_calls(
                    function_calls
                )

                # Strip out fields the user has manually edited
                user_edited = employee_profile.user_edited_fields or []
                if user_edited:
                    updates_dict = updates.model_dump(exclude_none=True)
                    filtered = {
                        k: v for k, v in updates_dict.items()
                        if k not in user_edited
                    }
                    updates = EmployeeProfileUpdate(**filtered)

                # Update employee profile
                updated_profile = await self.storage_service.update_employee_profile(
                    employee_profile.id,
                    updates
                )

                # Track extraction updates
                for key, value in updates.model_dump(exclude_none=True).items():
                    extraction_updates.append(ExtractionUpdate(
                        field_name=key,
                        field_value=value,
                        confidence=0.9
                    ))

                employee_profile = updated_profile

            # Calculate profile completeness
            profile_dict = employee_profile.model_dump(exclude_none=True)
            completeness = self.extraction_service.calculate_completeness_score(profile_dict)
            missing_fields = self.extraction_service.identify_missing_fields(profile_dict)

            # Update completeness score
            if completeness != employee_profile.profile_completeness_score:
                await self.storage_service.update_employee_profile(
                    employee_profile.id,
                    EmployeeProfileUpdate(profile_completeness_score=completeness)
                )

            # Check if conversation can be completed
            can_complete = self.extraction_service.can_complete_conversation(
                profile_dict,
                self.settings.MIN_PROFILE_COMPLETENESS_FOR_COMPLETION
            )

            # Save assistant message
            assistant_msg = ConversationMessageCreate(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=assistant_message,
                message_type=MessageType.TEXT,
                tokens_used=openai_response.get("tokens_used")
            )
            saved_assistant_msg = await self.storage_service.save_message(assistant_msg)

            # Optionally generate speech
            audio_url = None
            if self.settings.ENABLE_TEXT_TO_SPEECH:
                try:
                    audio_data = await self.speech_service.synthesize_speech(assistant_message)
                    # Would upload to storage in production
                    audio_url = None
                except Exception as e:
                    logger.warning(f"Failed to synthesize speech: {e}")

            logger.info(
                f"Processed message. Completeness: {completeness}%, "
                f"Can complete: {can_complete}"
            )

            return MessageResponse(
                conversation_id=conversation_id,
                message_id=saved_assistant_msg.id,
                assistant_message=assistant_message,
                audio_url=audio_url,
                extraction_updates=extraction_updates if extraction_updates else None,
                profile_completeness=completeness,
                missing_fields=missing_fields,
                can_complete=can_complete
            )

        except (ConversationNotFoundError, ConversationTimeoutError):
            raise
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            raise ConversationError(
                f"Failed to process message: {str(e)}",
                details={"error": str(e)}
            )

    async def process_speech_input(
        self,
        conversation_id: UUID,
        audio_data: bytes,
        audio_format: str = "wav"
    ) -> MessageResponse:
        """
        Process speech input from user.

        Args:
            conversation_id: Conversation ID
            audio_data: Audio file bytes
            audio_format: Audio format

        Returns:
            Message response

        Raises:
            ConversationError: If processing fails
        """
        try:
            logger.info(f"Processing speech input for conversation: {conversation_id}")

            # Transcribe audio
            transcription_result = await self.speech_service.transcribe_audio(
                audio_data,
                audio_format
            )

            # Process as text message
            message_request = MessageRequest(
                message=transcription_result["transcription"],
                message_type=MessageType.SPEECH
            )

            return await self.send_message(conversation_id, message_request)

        except Exception as e:
            logger.error(f"Failed to process speech input: {e}")
            raise ConversationError(
                f"Failed to process speech input: {str(e)}",
                details={"error": str(e)}
            )

    async def get_conversation_status(
        self,
        conversation_id: UUID
    ) -> ConversationStatusResponse:
        """
        Get current conversation status and progress.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation status response

        Raises:
            ConversationNotFoundError: If conversation not found
        """
        try:
            employee_profile = await self.storage_service.get_by_conversation_id(conversation_id)
            if not employee_profile:
                raise ConversationNotFoundError(str(conversation_id))

            # Calculate duration
            duration = datetime.now(timezone.utc) - employee_profile.conversation_started_at
            duration_minutes = int(duration.total_seconds() / 60)

            # Get missing fields
            profile_dict = employee_profile.model_dump(exclude_none=True)
            missing_fields = self.extraction_service.identify_missing_fields(profile_dict)

            # Check if can complete
            can_complete = self.extraction_service.can_complete_conversation(
                profile_dict,
                self.settings.MIN_PROFILE_COMPLETENESS_FOR_COMPLETION
            )

            # Get last message time
            messages = await self.storage_service.get_conversation_history(
                conversation_id,
                limit=1
            )
            last_message_at = messages[-1].created_at if messages else None

            return ConversationStatusResponse(
                conversation_id=conversation_id,
                status=employee_profile.conversation_status,
                total_messages=employee_profile.total_messages,
                profile_completeness=employee_profile.profile_completeness_score,
                missing_fields=missing_fields,
                duration_minutes=duration_minutes,
                can_complete=can_complete,
                conversation_started_at=employee_profile.conversation_started_at,
                last_message_at=last_message_at
            )

        except ConversationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get conversation status: {e}")
            raise ConversationError(
                f"Failed to get conversation status: {str(e)}",
                details={"error": str(e)}
            )

    async def complete_conversation(
        self,
        conversation_id: UUID
    ) -> ConversationCompleteResponse:
        """
        Complete a conversation and finalize the profile.

        Args:
            conversation_id: Conversation ID

        Returns:
            Completion response with summary

        Raises:
            ConversationNotFoundError: If conversation not found
            ConversationError: If completion fails
        """
        try:
            logger.info(f"Completing conversation: {conversation_id}")

            employee_profile = await self.storage_service.get_by_conversation_id(conversation_id)
            if not employee_profile:
                raise ConversationNotFoundError(str(conversation_id))

            # Get conversation history
            messages = await self.storage_service.get_conversation_history(conversation_id)

            # Generate summary
            api_messages = self.openai_service.build_conversation_history(messages)
            profile_dict = employee_profile.model_dump(exclude_none=True)

            summary = await self.openai_service.generate_summary(
                api_messages,
                profile_dict
            )

            # Update profile with summary and status
            await self.storage_service.update_employee_profile(
                employee_profile.id,
                EmployeeProfileUpdate(
                    conversation_status=ConversationStatus.COMPLETED,
                    professional_summary=summary,
                    conversation_completed_at=datetime.now(timezone.utc)
                )
            )

            logger.info(f"Completed conversation: {conversation_id}")

            return ConversationCompleteResponse(
                conversation_id=conversation_id,
                employee_profile_id=employee_profile.id,
                status=ConversationStatus.COMPLETED,
                profile_completeness=employee_profile.profile_completeness_score,
                summary=summary
            )

        except ConversationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to complete conversation: {e}")
            raise ConversationError(
                f"Failed to complete conversation: {str(e)}",
                details={"error": str(e)}
            )

    async def get_conversation_history(
        self,
        conversation_id: UUID
    ) -> ConversationHistory:
        """
        Get full conversation history.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation history

        Raises:
            ConversationNotFoundError: If conversation not found
        """
        try:
            employee_profile = await self.storage_service.get_by_conversation_id(conversation_id)
            if not employee_profile:
                raise ConversationNotFoundError(str(conversation_id))

            messages = await self.storage_service.get_conversation_history(conversation_id)

            return ConversationHistory(
                conversation_id=conversation_id,
                messages=messages,
                total_messages=len(messages)
            )

        except ConversationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            raise ConversationError(
                f"Failed to get conversation history: {str(e)}",
                details={"error": str(e)}
            )

    async def _check_timeout(self, employee_profile):
        """Check if conversation has timed out."""
        timeout_delta = timedelta(minutes=self.settings.CONVERSATION_TIMEOUT_MINUTES)
        elapsed = datetime.now(timezone.utc) - employee_profile.conversation_started_at

        if elapsed > timeout_delta:
            raise ConversationTimeoutError(
                str(employee_profile.conversation_id),
                self.settings.CONVERSATION_TIMEOUT_MINUTES
            )
