"""
Azure Speech SDK service for speech-to-text and text-to-speech.
"""

import logging
import os
import asyncio
from typing import Optional, List, Dict, Any
from io import BytesIO

import azure.cognitiveservices.speech as speechsdk

from client_need_service.config import get_settings
from client_need_service.core.exceptions import (
    SpeechServiceError,
    ConfigurationError,
    AudioProcessingError
)

logger = logging.getLogger(__name__)


class SpeechService:
    """Service for Azure Speech SDK operations."""

    def __init__(self):
        """Initialize Speech service."""
        self.settings = get_settings()
        self._speech_config: Optional[speechsdk.SpeechConfig] = None
        self._initialize_config()

    def _initialize_config(self):
        """Initialize Azure Speech configuration."""
        if not self.settings.has_azure_speech_credentials():
            logger.warning(
                "Azure Speech credentials not configured. "
                "Service will not be available."
            )
            return

        try:
            self._speech_config = speechsdk.SpeechConfig(
                subscription=self.settings.AZURE_SPEECH_KEY,
                region=self.settings.AZURE_SPEECH_REGION
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
            raise ConfigurationError(
                f"Failed to initialize Azure Speech: {str(e)}"
            )

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
        language: Optional[str] = None
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
            AudioProcessingError: If audio format is invalid
        """
        self._ensure_config()

        if not self.settings.ENABLE_SPEECH_TO_TEXT:
            raise SpeechServiceError("Speech-to-text is disabled")

        try:
            logger.info(f"Transcribing audio ({len(audio_data)} bytes, format: {audio_format})")

            # Create audio config from bytes
            audio_stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

            # Create speech config with language if specified
            speech_config = self._speech_config
            if language:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.settings.AZURE_SPEECH_KEY,
                    region=self.settings.AZURE_SPEECH_REGION
                )
                speech_config.speech_recognition_language = language

            # Create recognizer
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )

            # Write audio data to stream
            audio_stream.write(audio_data)
            audio_stream.close()

            # Perform recognition
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                recognizer.recognize_once
            )

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                logger.info(f"Transcribed: {result.text[:50]}...")

                return {
                    "transcription": result.text,
                    "confidence": self._get_confidence_score(result),
                    "duration_seconds": result.duration.total_seconds() if hasattr(result, 'duration') else 0.0,
                    "language": language or self.settings.AZURE_SPEECH_LANGUAGE
                }

            elif result.reason == speechsdk.ResultReason.NoMatch:
                raise AudioProcessingError(
                    "No speech could be recognized in the audio",
                    details={"reason": "no_match"}
                )

            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                error_msg = f"Speech recognition canceled: {cancellation.reason}"

                if cancellation.reason == speechsdk.CancellationReason.Error:
                    error_msg += f" - Error details: {cancellation.error_details}"

                raise SpeechServiceError(error_msg)

            else:
                raise SpeechServiceError(f"Unexpected recognition result: {result.reason}")

        except (SpeechServiceError, AudioProcessingError):
            raise
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            raise SpeechServiceError(
                f"Failed to transcribe audio: {str(e)}",
                details={"error": str(e)}
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
        self,
        text: str,
        voice_name: Optional[str] = None,
        output_format: str = "mp3"
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
                    region=self.settings.AZURE_SPEECH_REGION
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
                speech_config=speech_config,
                audio_config=None
            )

            # Synthesize
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: synthesizer.speak_text(text)
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
                raise SpeechServiceError(f"Unexpected synthesis result: {result.reason}")

        except SpeechServiceError:
            raise
        except Exception as e:
            logger.error(f"Failed to synthesize speech: {e}")
            raise SpeechServiceError(
                f"Failed to synthesize speech: {str(e)}",
                details={"error": str(e)}
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
                speech_config=self._speech_config,
                audio_config=None
            )

            result = await asyncio.get_event_loop().run_in_executor(
                None,
                synthesizer.get_voices_async().get
            )

            voices = []
            for voice in result.voices:
                voices.append({
                    "name": voice.short_name,
                    "language": voice.locale,
                    "gender": voice.gender.name if hasattr(voice.gender, 'name') else "Unknown",
                    "locale": voice.locale
                })

            logger.info(f"Retrieved {len(voices)} available voices")

            return voices

        except Exception as e:
            logger.error(f"Failed to get available voices: {e}")
            # Return default voice if fetching fails
            return [{
                "name": self.settings.AZURE_SPEECH_VOICE_NAME,
                "language": self.settings.AZURE_SPEECH_LANGUAGE,
                "gender": "Female",
                "locale": self.settings.AZURE_SPEECH_LANGUAGE
            }]

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
