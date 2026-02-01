"""
Real-time speech streaming service using Azure Speech SDK (employee service).
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

try:
    import azure.cognitiveservices.speech as speechsdk
    from azure.cognitiveservices.speech.audio import (
        AudioStreamFormat,
        PushAudioInputStream,
    )

    SPEECH_SDK_AVAILABLE = True
except ImportError:
    SPEECH_SDK_AVAILABLE = False
    speechsdk = None
    AudioStreamFormat = None
    PushAudioInputStream = None

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import (
    SpeechServiceError,
    ConfigurationError,
    ConversationError,
)

logger = logging.getLogger(__name__)

_streaming_service_instance: Optional["SpeechStreamingService"] = None


def get_speech_streaming_service() -> "SpeechStreamingService":
    """Return the shared SpeechStreamingService instance."""
    global _streaming_service_instance
    if _streaming_service_instance is None:
        _streaming_service_instance = SpeechStreamingService()
    return _streaming_service_instance


@dataclass
class TranscriptEvent:
    """Represents a transcript event from speech recognition."""

    session_id: str
    conversation_id: Optional[str]
    text: str
    is_final: bool
    confidence: float
    language: str
    timestamp: str
    offset_ms: int
    duration_ms: int


@dataclass
class StreamSession:
    """Manages a streaming speech recognition session."""

    session_id: str
    conversation_id: Optional[str]
    language: str
    created_at: datetime
    last_activity: datetime
    is_active: bool = True
    recognizer: Any = None
    audio_stream: Any = None
    transcript_callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None

    def update_activity(self) -> None:
        self.last_activity = datetime.now(timezone.utc)

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        return datetime.now(timezone.utc) - self.last_activity > timedelta(
            minutes=timeout_minutes
        )


class SpeechStreamingService:
    """Service for real-time speech streaming with Azure Speech SDK."""

    def __init__(self) -> None:
        self.sessions: Dict[str, StreamSession] = {}
        self.settings = get_settings()
        self.speech_config: Optional[Any] = None
        self.cleanup_task: Optional[asyncio.Task] = None
        if SPEECH_SDK_AVAILABLE:
            self.speech_config = self._create_speech_config()

    def _create_speech_config(self) -> Any:
        if not SPEECH_SDK_AVAILABLE or speechsdk is None:
            raise ConfigurationError(
                "Azure Speech SDK not installed",
                details={"hint": "pip install azure-cognitiveservices-speech"},
            )
        if not self.settings.has_azure_speech_credentials():
            raise ConfigurationError(
                "Azure Speech service configuration missing",
                details={"missing": "AZURE_SPEECH_KEY and AZURE_SPEECH_REGION"},
            )
        speech_config = speechsdk.SpeechConfig(
            subscription=self.settings.AZURE_SPEECH_KEY,
            region=self.settings.AZURE_SPEECH_REGION,
        )
        speech_config.speech_recognition_language = self.settings.AZURE_SPEECH_LANGUAGE
        speech_config.enable_dictation()
        speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_EnableAudioLogging, "false"
        )
        logger.info("Azure Speech streaming config initialized (employee)")
        return speech_config

    def _ensure_config(self) -> None:
        if self.speech_config is None:
            raise ConfigurationError(
                "Azure Speech not configured. Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION."
            )

    async def create_session(
        self, conversation_id: Optional[str] = None, language: str = "en-US"
    ) -> str:
        self._ensure_config()
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        session = StreamSession(
            session_id=session_id,
            conversation_id=conversation_id,
            language=language,
            created_at=now,
            last_activity=now,
        )
        self.sessions[session_id] = session
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        logger.info("Created streaming session: %s", session_id)
        return session_id

    async def start_recognition(
        self,
        session_id: str,
        transcript_callback: Callable[[TranscriptEvent], Any],
        error_callback: Optional[Callable[[Exception], Any]] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._ensure_config()
        if (
            not SPEECH_SDK_AVAILABLE
            or speechsdk is None
            or AudioStreamFormat is None
            or PushAudioInputStream is None
        ):
            raise ConfigurationError("Azure Speech SDK not available")

        session = self.sessions.get(session_id)
        if not session:
            raise ConversationError(
                f"Session not found: {session_id}", details={"session_id": session_id}
            )

        event_loop = loop or asyncio.get_event_loop()

        def schedule_async(coro: Any) -> None:
            asyncio.run_coroutine_threadsafe(coro, event_loop)

        try:
            audio_format = AudioStreamFormat(
                samples_per_second=16000, bits_per_sample=16, channels=1
            )
            audio_stream = PushAudioInputStream(audio_format)
            audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

            config = speechsdk.SpeechConfig(
                subscription=self.settings.AZURE_SPEECH_KEY,
                region=self.settings.AZURE_SPEECH_REGION,
            )
            config.speech_recognition_language = session.language

            recognizer = speechsdk.SpeechRecognizer(
                speech_config=config, audio_config=audio_config
            )

            session.audio_stream = audio_stream
            session.recognizer = recognizer
            session.transcript_callback = transcript_callback
            session.error_callback = error_callback

            def on_recognizing(evt: Any) -> None:
                if evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
                    event = TranscriptEvent(
                        session_id=session_id,
                        conversation_id=session.conversation_id,
                        text=evt.result.text,
                        is_final=False,
                        confidence=0.0,
                        language=session.language,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        offset_ms=int(evt.result.offset / 10000),
                        duration_ms=int(evt.result.duration / 10000),
                    )
                    session.update_activity()
                    schedule_async(transcript_callback(event))

            def on_recognized(evt: Any) -> None:
                if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    confidence = 0.0
                    if hasattr(evt.result, "confidence") and evt.result.confidence:
                        confidence = float(evt.result.confidence)
                    event = TranscriptEvent(
                        session_id=session_id,
                        conversation_id=session.conversation_id,
                        text=evt.result.text,
                        is_final=True,
                        confidence=confidence,
                        language=session.language,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        offset_ms=int(evt.result.offset / 10000),
                        duration_ms=int(evt.result.duration / 10000),
                    )
                    session.update_activity()
                    schedule_async(transcript_callback(event))

            def on_canceled(evt: Any) -> None:
                if evt.reason == speechsdk.CancellationReason.Error:
                    error_msg = f"Speech recognition error: {getattr(evt, 'error_details', str(evt.reason))}"
                    logger.error(error_msg)
                    if error_callback:
                        schedule_async(error_callback(SpeechServiceError(error_msg)))
                else:
                    logger.info("Recognition canceled: %s", evt.reason)

            recognizer.recognizing.connect(on_recognizing)
            recognizer.recognized.connect(on_recognized)
            recognizer.canceled.connect(on_canceled)

            future = recognizer.start_continuous_recognition_async()
            await asyncio.get_event_loop().run_in_executor(None, future.get)
            logger.info("Started recognition for session: %s", session_id)

        except Exception as e:
            logger.exception("Failed to start recognition: %s", e)
            if error_callback:
                schedule_async(error_callback(e))
            raise SpeechServiceError(
                f"Failed to start speech recognition: {str(e)}",
                details={"session_id": session_id},
            )

    async def add_audio_chunk(self, session_id: str, audio_data: bytes) -> None:
        session = self.sessions.get(session_id)
        if not session:
            raise ConversationError(
                f"Session not found: {session_id}", details={"session_id": session_id}
            )
        if not session.is_active or not session.audio_stream:
            raise ConversationError(
                f"Session not active: {session_id}",
                details={"session_id": session_id, "is_active": session.is_active},
            )
        try:
            session.audio_stream.write(audio_data)
            session.update_activity()
        except Exception as e:
            logger.error("Failed to write audio chunk: %s", e)
            raise SpeechServiceError(
                f"Failed to process audio chunk: {str(e)}",
                details={"session_id": session_id},
            )

    async def stop_session(self, session_id: str) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            raise ConversationError(
                f"Session not found: {session_id}", details={"session_id": session_id}
            )
        try:
            if session.recognizer:
                future = session.recognizer.stop_continuous_recognition_async()
                await asyncio.get_event_loop().run_in_executor(None, future.get)
            if session.audio_stream:
                session.audio_stream.close()
            session.is_active = False

            summary = {
                "session_id": session_id,
                "conversation_id": session.conversation_id,
                "language": session.language,
                "created_at": session.created_at.isoformat(),
                "duration_seconds": (
                    session.last_activity - session.created_at
                ).total_seconds(),
                "stopped_at": datetime.now(timezone.utc).isoformat(),
            }
            del self.sessions[session_id]
            logger.info("Stopped session: %s", session_id)
            return summary
        except Exception as e:
            logger.error("Error stopping session: %s", e)
            raise SpeechServiceError(
                f"Failed to stop session: {str(e)}", details={"session_id": session_id}
            )

    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            raise ConversationError(
                f"Session not found: {session_id}", details={"session_id": session_id}
            )
        timeout_min = self.settings.SPEECH_STREAM_SESSION_TIMEOUT_MINUTES
        return {
            "session_id": session_id,
            "conversation_id": session.conversation_id,
            "language": session.language,
            "is_active": session.is_active,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "duration_seconds": (
                session.last_activity - session.created_at
            ).total_seconds(),
            "timeout_minutes": timeout_min,
        }

    async def _cleanup_expired_sessions(self) -> None:
        timeout_min = self.settings.SPEECH_STREAM_SESSION_TIMEOUT_MINUTES
        while True:
            try:
                expired = [
                    sid
                    for sid, s in self.sessions.items()
                    if s.is_expired(timeout_minutes=timeout_min)
                ]
                for session_id in expired:
                    try:
                        await self.stop_session(session_id)
                        logger.info("Cleaned up expired session: %s", session_id)
                    except Exception as e:
                        logger.error("Error cleaning up session %s: %s", session_id, e)
                await asyncio.sleep(300)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in cleanup task: %s", e)
                await asyncio.sleep(60)
