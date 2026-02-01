"""
Azure OpenAI service for conversational AI capabilities.
"""

import logging
from typing import List, Dict, Any, Optional
from uuid import UUID

from openai import AsyncAzureOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import AzureOpenAIError, ConfigurationError
from employee_conversation_service.models.schemas import MessageRole
from employee_conversation_service.prompts.system_prompts import (
    SYSTEM_PROMPT,
    EXTRACTION_FUNCTIONS,
    GREETING_MESSAGE,
    RETURNING_USER_GREETING_PROMPT,
    RESUME_GREETING_PROMPT,
    get_conversation_context
)

logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """Service for interacting with Azure OpenAI."""

    def __init__(self):
        """Initialize Azure OpenAI service."""
        self.settings = get_settings()
        self._client: Optional[AsyncAzureOpenAI] = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Azure OpenAI client."""
        if not self.settings.has_azure_openai_credentials():
            logger.warning(
                "Azure OpenAI credentials not configured. "
                "Service will not be available."
            )
            return

        try:
            self._client = AsyncAzureOpenAI(
                api_key=self.settings.AZURE_OPENAI_KEY,
                api_version=self.settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT
            )
            logger.info("Azure OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise ConfigurationError(
                f"Failed to initialize Azure OpenAI: {str(e)}"
            )

    def _ensure_client(self):
        """Ensure client is initialized."""
        if self._client is None:
            raise ConfigurationError(
                "Azure OpenAI client not initialized. "
                "Please configure AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY."
            )

    @retry(
        retry=retry_if_exception_type((AzureOpenAIError,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_functions: bool = True,
        extracted_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from Azure OpenAI.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response
            use_functions: Whether to use function calling for extraction
            extracted_data: Currently extracted data for context

        Returns:
            Dictionary containing response and function calls

        Raises:
            AzureOpenAIError: If the API call fails
        """
        self._ensure_client()

        try:
            # Build messages with system prompt
            full_messages = self._build_messages(messages, extracted_data)

            # Prepare API call parameters
            api_params = {
                "model": self.settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                "messages": full_messages,
                "temperature": temperature or self.settings.AZURE_OPENAI_TEMPERATURE,
                "max_tokens": max_tokens or self.settings.AZURE_OPENAI_MAX_TOKENS,
            }

            # Add function calling if enabled
            if use_functions:
                api_params["tools"] = EXTRACTION_FUNCTIONS
                api_params["tool_choice"] = "auto"

            logger.info(f"Calling Azure OpenAI with {len(full_messages)} messages")

            # Make API call
            response = await self._client.chat.completions.create(**api_params)

            # Extract response data
            result = self._parse_response(response)

            logger.info(
                f"Azure OpenAI response generated. "
                f"Tokens used: {result.get('tokens_used', 0)}"
            )

            return result

        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
            raise AzureOpenAIError(
                f"Failed to generate response: {str(e)}",
                details={"error": str(e)}
            )

    def _build_messages(
        self,
        messages: List[Dict[str, str]],
        extracted_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """
        Build full message list with system prompt and context.

        Args:
            messages: Conversation messages
            extracted_data: Currently extracted data

        Returns:
            Full message list including system prompt
        """
        # Start with system prompt
        system_content = SYSTEM_PROMPT

        # Add extraction context if available
        if extracted_data:
            context = get_conversation_context(extracted_data)
            system_content += f"\n\n{context}"

        full_messages = [
            {"role": "system", "content": system_content}
        ]

        # Add conversation messages
        full_messages.extend(messages)

        return full_messages

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """
        Parse Azure OpenAI API response.

        Args:
            response: API response object

        Returns:
            Parsed response dictionary
        """
        choice = response.choices[0]
        message = choice.message

        result = {
            "content": message.content or "",
            "role": message.role,
            "function_calls": [],
            "tokens_used": response.usage.total_tokens if response.usage else 0,
            "finish_reason": choice.finish_reason
        }

        # Extract function calls if present
        if message.tool_calls:
            for tool_call in message.tool_calls:
                if tool_call.type == "function":
                    result["function_calls"].append({
                        "id": tool_call.id,
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    })

        return result

    async def generate_greeting(self) -> str:
        """
        Generate initial greeting message.

        Returns:
            Greeting message string
        """
        return GREETING_MESSAGE

    async def generate_returning_user_greeting(
        self,
        profile_data: Dict[str, Any]
    ) -> str:
        """
        Generate a personalized greeting for a returning user.

        Args:
            profile_data: Carried-forward profile data dictionary

        Returns:
            Personalized greeting message
        """
        try:
            self._ensure_client()

            profile_context = get_conversation_context(profile_data, is_returning_user=True)
            prompt = RETURNING_USER_GREETING_PROMPT.format(profile_context=profile_context)

            response = await self._client.chat.completions.create(
                model=self.settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Generate the welcome-back greeting."}
                ],
                temperature=0.6,
                max_tokens=300
            )

            greeting = response.choices[0].message.content or ""
            logger.info("Generated returning user greeting")
            return greeting

        except Exception as e:
            logger.warning(f"Failed to generate returning user greeting, using fallback: {e}")
            return GREETING_MESSAGE

    async def generate_resume_greeting(
        self,
        profile_data: Dict[str, Any],
        recent_messages: List[Dict[str, str]]
    ) -> str:
        """
        Generate a greeting for resuming an in-progress conversation.

        Args:
            profile_data: Current profile data dictionary
            recent_messages: Last few messages from the conversation

        Returns:
            Resume greeting message
        """
        try:
            self._ensure_client()

            profile_context = get_conversation_context(profile_data)

            last_messages_text = ""
            for msg in recent_messages[-3:]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                last_messages_text += f"{role}: {content}\n"

            prompt = RESUME_GREETING_PROMPT.format(
                profile_context=profile_context,
                last_messages=last_messages_text.strip()
            )

            response = await self._client.chat.completions.create(
                model=self.settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Generate the resume greeting."}
                ],
                temperature=0.6,
                max_tokens=300
            )

            greeting = response.choices[0].message.content or ""
            logger.info("Generated resume greeting")
            return greeting

        except Exception as e:
            logger.warning(f"Failed to generate resume greeting, using fallback: {e}")
            return "Welcome back! Let's continue where we left off."

    async def generate_summary(
        self,
        messages: List[Dict[str, str]],
        extracted_data: Dict[str, Any]
    ) -> str:
        """
        Generate a comprehensive summary of the conversation and extracted profile.

        Args:
            messages: Full conversation history
            extracted_data: All extracted information

        Returns:
            Summary text

        Raises:
            AzureOpenAIError: If summary generation fails
        """
        self._ensure_client()

        try:
            summary_messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages,
                {
                    "role": "user",
                    "content": (
                        "Please provide a comprehensive summary of my professional profile "
                        "based on our conversation. Include my skills, experience, career goals, "
                        "availability, and any other relevant details."
                    )
                }
            ]

            response = await self._client.chat.completions.create(
                model=self.settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=summary_messages,
                temperature=0.5,
                max_tokens=1000
            )

            summary = response.choices[0].message.content or ""
            logger.info("Generated conversation summary")

            return summary

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            raise AzureOpenAIError(
                f"Failed to generate summary: {str(e)}",
                details={"error": str(e)}
            )

    def build_conversation_history(
        self,
        messages: List[Any],
        max_messages: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Build conversation history for API call from message objects.

        Args:
            messages: List of ConversationMessage objects
            max_messages: Maximum number of messages to include

        Returns:
            List of message dictionaries for API
        """
        max_msg = max_messages or self.settings.MAX_CONVERSATION_MESSAGES

        # Take most recent messages
        recent_messages = messages[-max_msg:] if len(messages) > max_msg else messages

        # Convert to API format
        api_messages = []
        for msg in recent_messages:
            # Skip system messages
            if msg.role == MessageRole.SYSTEM:
                continue

            api_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })

        return api_messages

    async def check_health(self) -> bool:
        """
        Check if Azure OpenAI service is available.

        Returns:
            True if service is healthy, False otherwise
        """
        if self._client is None:
            return False

        try:
            # Simple test call
            await self._client.chat.completions.create(
                model=self.settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"Azure OpenAI health check failed: {e}")
            return False
