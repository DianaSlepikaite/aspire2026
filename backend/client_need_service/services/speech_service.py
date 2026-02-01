"""
Azure Speech SDK service for speech-to-text and text-to-speech.
"""

import logging
import os
import asyncio
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from io import BytesIO

try:
    import azure.cognitiveservices.speech as speechsdk

    SPEECH_SDK_AVAILABLE = True
except ImportError:
    SPEECH_SDK_AVAILABLE = False
    speechsdk = None

from client_need_service.config import get_settings
from client_need_service.core.exceptions import (
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
    """
    Validate audio file size, minimum length, and format for upload/transcribe.
    Raises AudioProcessingError with error_code in details on failure.
    """
    settings = get_settings()
    max_bytes = settings.get_max_audio_size_bytes()
    min_bytes = settings.MIN_AUDIO_FILE_SIZE_BYTES
    allowed_extensions = [e.lower() for e in settings.ALLOWED_AUDIO_EXTENSIONS]
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
    if fmt not in allowed_extensions:
        raise AudioProcessingError(
            f"Unsupported audio format: {audio_format}. Allowed: {allowed_extensions}",
            details={"error_code": "unsupported_format", "allowed": allowed_extensions},
        )
    if content_type and content_type.lower().split(";")[0].strip() not in allowed_mimes:
        raise AudioProcessingError(
            f"Unsupported audio MIME type: {content_type}. Allowed: {allowed_mimes}",
            details={
                "error_code": "unsupported_format",
                "allowed_mime_types": allowed_mimes,
            },
        )


class SpeechService:
    """Service for Azure Speech SDK operations."""

    def __init__(self):
        """Initialize Speech service."""
        self.settings = get_settings()
        self._speech_config: Optional[speechsdk.SpeechConfig] = None
        self._initialize_config()

    def _initialize_config(self):
        """Initialize Azure Speech configuration."""
        if not SPEECH_SDK_AVAILABLE:
            logger.warning(
                "Azure Speech SDK not installed. Speech service will not be available."
            )
            return

        if not self.settings.has_azure_speech_credentials():
            logger.warning(
                "Azure Speech credentials not configured. "
                "Service will not be available."
            )
            return

        try:
            self._speech_config = speechsdk.SpeechConfig(
                subscription=self.settings.AZURE_SPEECH_KEY,
                region=self.settings.AZURE_SPEECH_REGION,
            )

            # Set recognition language
            self._speech_config.speech_recognition_language = (
                self.settings.AZURE_SPEECH_LANGUAGE
            )

            # Set synthesis voice
            self._speech_config.speech_synthesis_voice_name = (
                self.settings.AZURE_SPEECH_VOICE_NAME
            )

            logger.info("Azure Speech config initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Azure Speech config: {e}")
            raise ConfigurationError(f"Failed to initialize Azure Speech: {str(e)}")

    def _ensure_config(self):
        """Ensure speech config is initialized."""
        if self._speech_config is None:
            raise ConfigurationError(
                "Azure Speech not configured. "
                "Please set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION."
            )

    async def transcribe_audio(
        self,
        audio_data: bytes,
        audio_format: str = "wav",
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using speech-to-text.

        Args:
            audio_data: Audio file bytes
            audio_format: Audio format (wav, mp3, ogg)
            language: Optional language override

        Returns:
            Dictionary with transcription, confidence, and duration

        Raises:
            SpeechServiceError: If transcription fails
            AudioProcessingError: If audio format is invalid or validation fails
        """
        self._ensure_config()

        if not self.settings.ENABLE_SPEECH_TO_TEXT:
            raise SpeechServiceError(
                "Speech-to-text is disabled",
                details={"error_code": "transcription_disabled"},
            )

        validate_audio_input(audio_data, audio_format)

        try:
            logger.info(
                f"Transcribing audio ({len(audio_data)} bytes, format: {audio_format})"
            )

            # Create audio config from bytes
            audio_stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

            # Create speech config with language if specified
            speech_config = self._speech_config
            if language:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.settings.AZURE_SPEECH_KEY,
                    region=self.settings.AZURE_SPEECH_REGION,
                )
                speech_config.speech_recognition_language = language

            # Create recognizer
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, audio_config=audio_config
            )

            # Write audio data to stream
            audio_stream.write(audio_data)
            audio_stream.close()

            # Use continuous recognition for longer audio
            # This will transcribe the entire audio file, not just until the first pause
            done = asyncio.Event()
            all_results = []

            def recognized_callback(evt):
                """Callback for each recognized segment."""
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    all_results.append(evt.result.text)
                    logger.debug(f"Recognized segment: {evt.result.text[:50]}...")

            def stopped_callback(evt):
                """Callback when recognition stops."""
                asyncio.get_event_loop().call_soon_threadsafe(done.set)

            # Connect callbacks
            recognizer.recognized.connect(recognized_callback)
            recognizer.session_stopped.connect(stopped_callback)
            recognizer.canceled.connect(stopped_callback)

            # Start continuous recognition
            recognizer.start_continuous_recognition()

            # Wait for completion (with timeout)
            try:
                await asyncio.wait_for(done.wait(), timeout=120.0)
            except asyncio.TimeoutError:
                logger.warning("Recognition timeout - using partial results")
            finally:
                recognizer.stop_continuous_recognition()

            # Combine all recognized segments
            full_transcription = " ".join(all_results).strip()

            if not full_transcription:
                raise AudioProcessingError(
                    "No speech could be recognized in the audio",
                    details={"error_code": "no_speech_detected", "reason": "no_match"},
                )

            logger.info(f"Transcribed: {full_transcription[:50]}... ({len(full_transcription)} chars)")

            # Create a result-like object for compatibility
            return {
                "transcription": full_transcription,
                "confidence": 0.95,  # Azure doesn't provide confidence for continuous recognition
                "duration_seconds": 0.0,  # Duration not available in continuous mode
                "language": language or self.settings.AZURE_SPEECH_LANGUAGE,
            }

            # OLD CODE USING recognize_once() - keeping for reference but won't be reached
            result = await asyncio.get_event_loop().run_in_executor(
                None, recognizer.recognize_once
            )

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                logger.info(f"Transcribed: {result.text[:50]}...")

                # Extract duration - Azure returns it as ticks (100 nanosecond units)
                duration_seconds = 0.0
                if hasattr(result, "duration") and result.duration:
                    if hasattr(result.duration, "total_seconds"):
                        # Duration is a timedelta object
                        duration_seconds = result.duration.total_seconds()
                    elif isinstance(result.duration, (int, float)):
                        # Duration is in ticks (100 nanosecond units)
                        duration_seconds = result.duration / 10_000_000.0
                    else:
                        duration_seconds = 0.0

                return {
                    "transcription": result.text,
                    "confidence": self._get_confidence_score(result),
                    "duration_seconds": duration_seconds,
                    "language": language or self.settings.AZURE_SPEECH_LANGUAGE,
                }

            elif result.reason == speechsdk.ResultReason.NoMatch:
                raise AudioProcessingError(
                    "No speech could be recognized in the audio",
                    details={"error_code": "no_speech_detected", "reason": "no_match"},
                )

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg = f"Speech recognition canceled: {cancellation.reason}"

                if cancellation.reason == speechsdk.CancellationReason.Error:
                    error_msg += f" - Error details: {cancellation.error_details}"

                raise SpeechServiceError(
                    error_msg,
                    details={
                        "error_code": "transcription_service_error",
                        "error": str(cancellation.error_details)
                        if hasattr(cancellation, "error_details")
                        else None,
                    },
                )

            else:
                raise SpeechServiceError(
                    f"Unexpected recognition result: {result.reason}",
                    details={"error_code": "transcription_service_error"},
                )

        except (SpeechServiceError, AudioProcessingError):
            raise
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            raise SpeechServiceError(
                f"Failed to transcribe audio: {str(e)}",
                details={"error_code": "transcription_service_error", "error": str(e)},
            )

    def _get_confidence_score(self, result: Any) -> float:
        """
        Extract confidence score from recognition result.

        Args:
            result: Speech recognition result

        Returns:
            Confidence score between 0 and 1
        """
        try:
            # Azure Speech SDK doesn't always provide confidence in basic tier
            # Return a default high confidence for successful recognition
            return 0.95
        except Exception:
            return 0.9

    async def synthesize_speech(
        self, text: str, voice_name: Optional[str] = None, output_format: str = "mp3"
    ) -> bytes:
        """
        Synthesize text to speech audio.

        Args:
            text: Text to convert to speech
            voice_name: Optional voice name override
            output_format: Audio output format (wav or mp3)

        Returns:
            Audio bytes

        Raises:
            SpeechServiceError: If synthesis fails
        """
        self._ensure_config()

        if not self.settings.ENABLE_TEXT_TO_SPEECH:
            raise SpeechServiceError("Text-to-speech is disabled")

        try:
            logger.info(f"Synthesizing speech for text ({len(text)} chars)")

            # Create speech config with voice if specified
            speech_config = self._speech_config
            if voice_name:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.settings.AZURE_SPEECH_KEY,
                    region=self.settings.AZURE_SPEECH_REGION,
                )
                speech_config.speech_synthesis_voice_name = voice_name

            # Set output format
            if output_format == "mp3":
                speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
                )
            else:
                speech_config.set_speech_synthesis_output_format(
                    speechsdk.SpeechSynthesisOutputFormat.Audio16Khz16BitMonoPcm
                )

            # Create synthesizer with no audio output (we'll get bytes)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=None
            )

            # Synthesize
            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: synthesizer.speak_text(text)
            )

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(f"Synthesized audio ({len(result.audio_data)} bytes)")
                return result.audio_data

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg = f"Speech synthesis canceled: {cancellation.reason}"

                if cancellation.reason == speechsdk.CancellationReason.Error:
                    error_msg += f" - Error details: {cancellation.error_details}"

                raise SpeechServiceError(error_msg)

            else:
                raise SpeechServiceError(
                    f"Unexpected synthesis result: {result.reason}"
                )

        except SpeechServiceError:
            raise
        except Exception as e:
            logger.error(f"Failed to synthesize speech: {e}")
            raise SpeechServiceError(
                f"Failed to synthesize speech: {str(e)}", details={"error": str(e)}
            )

    async def get_available_voices(self) -> List[Dict[str, str]]:
        """
        Get list of available TTS voices.

        Returns:
            List of voice dictionaries with name, language, gender

        Raises:
            SpeechServiceError: If fetching voices fails
        """
        self._ensure_config()

        try:
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self._speech_config, audio_config=None
            )

            result = await asyncio.get_event_loop().run_in_executor(
                None, synthesizer.get_voices_async().get
            )

            voices = []
            for voice in result.voices:
                voices.append(
                    {
                        "name": voice.short_name,
                        "language": voice.locale,
                        "gender": voice.gender.name
                        if hasattr(voice.gender, "name")
                        else "Unknown",
                        "locale": voice.locale,
                    }
                )

            logger.info(f"Retrieved {len(voices)} available voices")

            return voices

        except Exception as e:
            logger.error(f"Failed to get available voices: {e}")
            # Return default voice if fetching fails
            return [
                {
                    "name": self.settings.AZURE_SPEECH_VOICE_NAME,
                    "language": self.settings.AZURE_SPEECH_LANGUAGE,
                    "gender": "Female",
                    "locale": self.settings.AZURE_SPEECH_LANGUAGE,
                }
            ]

    async def check_health(self) -> bool:
        """
        Check if Azure Speech service is available.

        Returns:
            True if service is healthy, False otherwise
        """
        if self._speech_config is None:
            return False

        try:
            # Simple test synthesis
            await self.synthesize_speech("test", output_format="wav")
            return True
        except Exception as e:
            logger.error(f"Azure Speech health check failed: {e}")
            return False
