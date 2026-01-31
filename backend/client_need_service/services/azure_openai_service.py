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

from client_need_service.config import get_settings
from client_need_service.core.exceptions import AzureOpenAIError, ConfigurationError
from client_need_service.models.schemas import MessageRole
from client_need_service.prompts.system_prompts import (
    SYSTEM_PROMPT,
    EXTRACTION_FUNCTIONS,
    GREETING_MESSAGE,
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

    async def generate_summary(
        self,
        messages: List[Dict[str, str]],
        extracted_data: Dict[str, Any]
    ) -> str:
        """
        Generate a comprehensive summary of the conversation and extracted needs.

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
                        "Please provide a comprehensive summary of the client's needs "
                        "based on our conversation. Include project overview, key requirements, "
                        "skills needed, timeline, budget, and any special considerations."
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
