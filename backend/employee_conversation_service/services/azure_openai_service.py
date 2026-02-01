"""
Azure OpenAI service for summaries and clarifying questions.
"""

import logging
from typing import List, Dict, Any, Optional

from employee_conversation_service.core.exceptions import ServiceError

logger = logging.getLogger(__name__)

try:
    from openai import AsyncAzureOpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncAzureOpenAI = None


class AzureOpenAIService:
    """Generate summary of extracted profile and clarifying questions using Azure OpenAI."""

    def __init__(self) -> None:
        self._client: Optional[Any] = None
        # Stub: real impl would load config (AZURE_OPENAI_KEY, etc.) and init client

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        use_functions: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate response from Azure OpenAI.
        Returns dict with "content" key (and optionally "function_calls").
        """
        if not OPENAI_AVAILABLE or self._client is None:
            # Stub: return a placeholder so agent can run without Azure
            logger.warning("Azure OpenAI not configured; returning stub response")
            return {"content": "[Azure OpenAI not configured - stub response]"}
        # Real impl: call self._client.chat.completions.create(...)
        return {"content": "[Stub response]"}
