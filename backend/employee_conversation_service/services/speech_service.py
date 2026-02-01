"""
Speech service (optional).
If the employee side supports voice, transcribe/synthesize for conversation.
"""

import logging
from typing import Optional, Dict, Any

from employee_conversation_service.core.exceptions import ServiceError

logger = logging.getLogger(__name__)


class SpeechService:
    """Speech-to-text and text-to-speech for employee conversation (optional)."""

    async def transcribe_audio(
        self, audio_data: bytes, audio_format: str = "wav"
    ) -> Dict[str, Any]:
        """Transcribe audio to text (stub)."""
        logger.warning("SpeechService stub: transcribe_audio not implemented")
        return {"transcription": "", "confidence": 0.0}

    async def synthesize_speech(
        self, text: str, voice_name: Optional[str] = None
    ) -> bytes:
        """Synthesize text to speech (stub)."""
        logger.warning("SpeechService stub: synthesize_speech not implemented")
        return b""
