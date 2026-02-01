"""
Azure Speech SDK service for speech-to-text and text-to-speech (employee conversation).
"""

import logging
import asyncio
from typing import Optional, List, Dict, Any

try:
    import azure.cognitiveservices.speech as speechsdk

    SPEECH_SDK_AVAILABLE = True
except ImportError:
    SPEECH_SDK_AVAILABLE = False
    speechsdk = None

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import (
    SpeechServiceError,
    ConfigurationError,
    AudioProcessingError,
)

logger = logging.getLogger(__name__)


def validate_audio_input(
    audio_data: bytes,
    audio_format: str,
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
) -> None:
    """Validate audio file size and format. Raises AudioProcessingError on failure."""
    settings = get_settings()
    max_bytes = settings.get_max_audio_size_bytes()
    min_bytes = settings.MIN_AUDIO_FILE_SIZE_BYTES
    allowed_ext = [e.lower() for e in settings.ALLOWED_AUDIO_EXTENSIONS]
    allowed_mimes = [m.lower() for m in settings.ALLOWED_AUDIO_MIME_TYPES]

    if len(audio_data) > max_bytes:
        raise AudioProcessingError(
            f"Audio file exceeds maximum size of {settings.MAX_AUDIO_FILE_SIZE_MB} MB",
            details={"error_code": "file_too_large", "max_bytes": max_bytes},
        )
    if len(audio_data) < min_bytes:
        raise AudioProcessingError(
            "Audio file is empty or too small to process",
            details={"error_code": "file_too_small", "min_bytes": min_bytes},
        )
    fmt = audio_format.lower().lstrip(".")
    if fmt not in allowed_ext:
        raise AudioProcessingError(
            f"Unsupported audio format: {audio_format}. Allowed: {allowed_ext}",
            details={"error_code": "unsupported_format", "allowed": allowed_ext},
        )
    if content_type and content_type.lower().split(";")[0].strip() not in allowed_mimes:
        raise AudioProcessingError(
            f"Unsupported audio MIME type: {content_type}",
            details={
                "error_code": "unsupported_format",
                "allowed_mime_types": allowed_mimes,
            },
        )


class SpeechService:
    """Speech-to-text and text-to-speech for employee conversation."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._speech_config: Optional[Any] = None
        self._initialize_config()

    def _initialize_config(self) -> None:
        if not SPEECH_SDK_AVAILABLE:
            logger.warning("Azure Speech SDK not installed")
            return
        if not self.settings.has_azure_speech_credentials():
            logger.warning("Azure Speech credentials not configured")
            return
        try:
            self._speech_config = speechsdk.SpeechConfig(
                subscription=self.settings.AZURE_SPEECH_KEY,
                region=self.settings.AZURE_SPEECH_REGION,
            )
            self._speech_config.speech_recognition_language = (
                self.settings.AZURE_SPEECH_LANGUAGE
            )
            self._speech_config.speech_synthesis_voice_name = (
                self.settings.AZURE_SPEECH_VOICE_NAME
            )
            logger.info("Azure Speech config initialized (employee)")
        except Exception as e:
            logger.error("Failed to init Azure Speech: %s", e)

    def _ensure_config(self) -> None:
        if self._speech_config is None:
            raise ConfigurationError(
                "Azure Speech not configured. Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION."
            )

    async def transcribe_audio(
        self,
        audio_data: bytes,
        audio_format: str = "wav",
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Transcribe audio to text."""
        self._ensure_config()
        if not getattr(self.settings, "ENABLE_SPEECH_TO_TEXT", True):
            raise SpeechServiceError(
                "Speech-to-text is disabled",
                details={"error_code": "transcription_disabled"},
            )
        validate_audio_input(audio_data, audio_format)

        try:
            audio_stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)
            speech_config = self._speech_config
            if language:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.settings.AZURE_SPEECH_KEY,
                    region=self.settings.AZURE_SPEECH_REGION,
                )
                speech_config.speech_recognition_language = language
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, audio_config=audio_config
            )
            audio_stream.write(audio_data)
            audio_stream.close()

            result = await asyncio.get_event_loop().run_in_executor(
                None, recognizer.recognize_once
            )

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return {
                    "transcription": result.text,
                    "confidence": 0.95,
                    "duration_seconds": 0.0,
                    "language": language or self.settings.AZURE_SPEECH_LANGUAGE,
                }
            if result.reason == speechsdk.ResultReason.NoMatch:
                raise AudioProcessingError(
                    "No speech could be recognized in the audio",
                    details={"error_code": "no_speech_detected"},
                )
            raise SpeechServiceError(
                f"Recognition failed: {result.reason}",
                details={"error_code": "transcription_service_error"},
            )
        except (SpeechServiceError, AudioProcessingError):
            raise
        except Exception as e:
            logger.exception("Transcribe failed: %s", e)
            raise SpeechServiceError(
                f"Failed to transcribe: {str(e)}",
                details={"error_code": "transcription_service_error", "error": str(e)},
            )

    async def synthesize_speech(
        self, text: str, voice_name: Optional[str] = None, output_format: str = "mp3"
    ) -> bytes:
        """Synthesize text to speech."""
        self._ensure_config()
        if not getattr(self.settings, "ENABLE_TEXT_TO_SPEECH", True):
            raise SpeechServiceError("Text-to-speech is disabled")

        try:
            speech_config = self._speech_config
            if voice_name:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.settings.AZURE_SPEECH_KEY,
                    region=self.settings.AZURE_SPEECH_REGION,
                )
                speech_config.speech_synthesis_voice_name = voice_name
            if output_format == "mp3":
                speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
                )
            else:
                speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Audio16Khz16BitMonoPcm
                )
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=None
            )
            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: synthesizer.speak_text(text)
            )
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            raise SpeechServiceError(
                f"Synthesis failed: {result.reason}",
                details={"error": str(result.reason)},
            )
        except SpeechServiceError:
            raise
        except Exception as e:
            logger.exception("Synthesize failed: %s", e)
            raise SpeechServiceError(
                f"Failed to synthesize: {str(e)}",
                details={"error": str(e)},
            )

    async def get_available_voices(self) -> List[Dict[str, str]]:
        """Get list of available TTS voices."""
        self._ensure_config()
        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self._speech_config, audio_config=None
            )
            result = await asyncio.get_event_loop().run_in_executor(
                None, synthesizer.get_voices_async().get
            )
            return [
                {
                    "name": v.short_name,
                    "language": v.locale,
                    "gender": getattr(v.gender, "name", "Unknown"),
                    "locale": v.locale,
                }
                for v in result.voices
            ]
        except Exception as e:
            logger.warning("Failed to get voices: %s; returning default", e)
            return [
                {
                    "name": self.settings.AZURE_SPEECH_VOICE_NAME,
                    "language": self.settings.AZURE_SPEECH_LANGUAGE,
                    "gender": "Female",
                    "locale": self.settings.AZURE_SPEECH_LANGUAGE,
                }
            ]
