"""
Conversation service for orchestrating employee profile conversations.
"""

import logging
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta

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

    async def start_conversation(
        self,
        request: ConversationStartRequest
    ) -> ConversationStartResponse:
        """
        Start a new conversation session.

        Args:
            request: Conversation start request

        Returns:
            Conversation start response with greeting

        Raises:
            ConversationError: If conversation creation fails
        """
        try:
            logger.info("Starting new employee conversation")

            # Generate conversation ID
            conversation_id = uuid4()

            # Create employee profile
            profile_data = EmployeeProfileCreate(
                conversation_id=conversation_id,
                employee_id=request.employee_id,
                employee_email=request.employee_email,
                source_channel=request.source_channel
            )

            employee_profile = await self.storage_service.create_employee_profile(profile_data)

            # Generate greeting message
            greeting_text = await self.openai_service.generate_greeting()

            # Save greeting message
            greeting_msg = ConversationMessageCreate(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content=greeting_text,
                message_type=MessageType.TEXT
            )
            await self.storage_service.save_message(greeting_msg)

            # Optionally generate speech for greeting
            audio_url = None
            if self.settings.ENABLE_TEXT_TO_SPEECH:
                try:
                    audio_data = await self.speech_service.synthesize_speech(greeting_text)
                    # In production, you would upload to storage and return URL
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

        except Exception as e:
            logger.error(f"Failed to start conversation: {e}")
            raise ConversationError(
                f"Failed to start conversation: {str(e)}",
                details={"error": str(e)}
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
            duration = datetime.utcnow() - employee_profile.conversation_started_at
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
                    conversation_completed_at=datetime.utcnow()
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
        elapsed = datetime.utcnow() - employee_profile.conversation_started_at

        if elapsed > timeout_delta:
            raise ConversationTimeoutError(
                str(employee_profile.conversation_id),
                self.settings.CONVERSATION_TIMEOUT_MINUTES
            )
