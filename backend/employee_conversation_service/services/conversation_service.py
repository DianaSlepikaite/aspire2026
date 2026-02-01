"""
Conversation service (optional).
If the agent drives a conversation to fill gaps, send/receive messages and merge transcript into extraction.
"""

import logging
from typing import Optional, List, Dict, Any
from uuid import UUID

from employee_conversation_service.core.exceptions import ServiceError

logger = logging.getLogger(__name__)


class ConversationService:
    """Manage conversation with employee; optionally merge transcript into extraction."""

    async def get_conversation_transcript(self, conversation_id: UUID) -> Optional[str]:
        """Get full transcript for a conversation (for merging into extraction)."""
        logger.warning(
            "ConversationService stub: get_conversation_transcript not implemented"
        )
        return None

    async def send_message(
        self, conversation_id: UUID, role: str, content: str
    ) -> Dict[str, Any]:
        """Send a message in the conversation (stub)."""
        logger.warning("ConversationService stub: send_message not implemented")
        return {"role": role, "content": content}
