"""
Azure OpenAI service for conversation, summaries, and clarifying questions.
"""

import logging
from typing import List, Dict, Any, Optional

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import (
    ServiceError,
    ConfigurationError,
)

logger = logging.getLogger(__name__)

try:
    from openai import AsyncAzureOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncAzureOpenAI = None

EMPLOYEE_GREETING = (
    "Hello! I'm here to help build your employee profile. "
    "You can tell me about your skills, experience, education, and what roles you're looking for. "
    "What would you like to share first?"
)

EMPLOYEE_SYSTEM_PROMPT = (
    "You are a helpful HR assistant conducting a conversation to build and update an employee profile. "
    "You can confirm updates the user asks for and request any missing details needed to apply them. "
    "Ask clarifying questions about skills, experience, education, certifications, and preferred roles. "
    "Avoid refusing or mentioning file access limitations; focus on capturing profile data. "
    "Be concise and professional. Keep responses to 2-4 sentences unless summarizing."
)


class AzureOpenAIService:
    """Azure OpenAI for conversation, summary, and clarifying questions."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client: Optional[Any] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI not installed; Azure OpenAI unavailable")
            return
        if (
            not self.settings.AZURE_OPENAI_KEY
            or not self.settings.AZURE_OPENAI_ENDPOINT
        ):
            logger.warning("Azure OpenAI credentials not set; using stub")
            return
        try:
            self._client = AsyncAzureOpenAI(
                api_key=self.settings.AZURE_OPENAI_KEY,
                api_version=getattr(
                    self.settings, "AZURE_OPENAI_API_VERSION", "2024-02-01"
                ),
                azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT.rstrip("/"),
            )
            logger.info("Azure OpenAI client initialized")
        except Exception as e:
            logger.error("Failed to init Azure OpenAI: %s", e)

    def _ensure_client(self) -> None:
        if self._client is None:
            raise ConfigurationError(
                "Azure OpenAI not configured. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY."
            )

    async def generate_greeting(self) -> str:
        """Return greeting for employee conversation."""
        return EMPLOYEE_GREETING

    def build_conversation_history(
        self,
        messages: List[Any],
        max_messages: Optional[int] = None,
    ) -> List[Dict[str, str]]:
        """Build list of {role, content} for API from message rows/objects."""
        max_msg = max_messages or getattr(
            self.settings, "MAX_CONVERSATION_MESSAGES", 50
        )
        recent = messages[-max_msg:] if len(messages) > max_msg else messages
        out = []
        for msg in recent:
            role = (
                msg.get("role")
                if isinstance(msg, dict)
                else (
                    getattr(msg, "role", None)
                    or (msg["role"] if hasattr(msg, "__getitem__") else None)
                )
            )
            content = (
                msg.get("content")
                if isinstance(msg, dict)
                else (
                    getattr(msg, "content", None)
                    or (msg["content"] if hasattr(msg, "__getitem__") else "")
                )
            )
            if role and str(role).lower() == "system":
                continue
            out.append(
                {
                    "role": str(role).lower() if role else "user",
                    "content": content or "",
                }
            )
        return out

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        use_functions: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate chat response. Returns dict with "content" key.
        """
        if not OPENAI_AVAILABLE or self._client is None:
            logger.warning("Azure OpenAI not configured; stub response")
            return {
                "content": "[Azure OpenAI not configured - configure AZURE_OPENAI_* to enable conversation.]"
            }
        self._ensure_client()
        try:
            full = [{"role": "system", "content": EMPLOYEE_SYSTEM_PROMPT}] + messages
            response = await self._client.chat.completions.create(
                model=self.settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=full,
                temperature=0.7,
                max_tokens=1024,
            )
            content = (response.choices[0].message.content or "").strip()
            return {"content": content}
        except Exception as e:
            logger.exception("Azure OpenAI generate_response failed: %s", e)
            raise ServiceError(
                f"OpenAI request failed: {str(e)}",
                details={"error": str(e)},
                status_code=502,
            )
