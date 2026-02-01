"""
Speech endpoints (transcribe, synthesize, voices) for employee service.
"""

import logging
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import Response

from employee_conversation_service.config import get_settings
from employee_conversation_service.models.schemas import (
    TranscriptionResponse,
    SynthesisRequest,
    VoicesResponse,
    Voice,
)
from employee_conversation_service.services.speech_service import (
    SpeechService,
    validate_audio_input,
)
from employee_conversation_service.core.exceptions import (
    SpeechServiceError,
    AudioProcessingError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _audio_format_from_filename(filename: Optional[str]) -> str:
    if not filename or "." not in filename:
        return "wav"
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext if ext in ("wav", "mp3", "ogg", "m4a") else "wav"


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Transcribe audio to text",
    description="Convert audio file to text. Allowed: WAV, MP3, OGG, M4A.",
    tags=["speech"],
)
async def transcribe_audio(
    audio_file: UploadFile = File(..., description="Audio file (WAV, MP3, OGG, M4A)"),
):
    """Transcribe audio to text."""
    try:
        settings = get_settings()
        max_bytes = settings.get_max_audio_size_bytes()
        if audio_file.size is not None and audio_file.size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": f"Audio file exceeds maximum size of {settings.MAX_AUDIO_FILE_SIZE_MB} MB",
                    "error_code": "file_too_large",
                },
            )
        audio_data = await audio_file.read()
        if len(audio_data) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={"error": "File too large", "error_code": "file_too_large"},
            )
        audio_format = _audio_format_from_filename(audio_file.filename)
        content_type = audio_file.content_type or ""
        validate_audio_input(
            audio_data, audio_format, audio_file.filename, content_type
        )
        speech_service = SpeechService()
        result = await speech_service.transcribe_audio(audio_data, audio_format)
        return TranscriptionResponse(
            transcription=result["transcription"],
            confidence=result["confidence"],
            duration_seconds=result["duration_seconds"],
        )
    except HTTPException:
        raise
    except AudioProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": e.message,
                "error_code": e.details.get("error_code", "audio_processing_error"),
            },
        )
    except SpeechServiceError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except Exception as e:
        logger.exception("Transcribe failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to transcribe", "message": str(e)},
        )


@router.post(
    "/synthesize",
    status_code=status.HTTP_200_OK,
    summary="Synthesize text to speech",
    description="Convert text to speech audio (MP3)",
    tags=["speech"],
)
async def synthesize_speech(request: SynthesisRequest):
    """Synthesize text to speech."""
    try:
        speech_service = SpeechService()
        audio_bytes = await speech_service.synthesize_speech(
            request.text, voice_name=request.voice_name, output_format="mp3"
        )
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=speech.mp3"},
        )
    except SpeechServiceError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except Exception as e:
        logger.exception("Synthesize failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to synthesize", "message": str(e)},
        )


@router.get(
    "/voices",
    response_model=VoicesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get available voices",
    description="List available TTS voices",
    tags=["speech"],
)
async def get_voices():
    """Get available TTS voices."""
    try:
        speech_service = SpeechService()
        voices_data = await speech_service.get_available_voices()
        voices = [
            Voice(
                name=v["name"],
                language=v["language"],
                gender=v["gender"],
                locale=v["locale"],
            )
            for v in voices_data
        ]
        return VoicesResponse(voices=voices)
    except Exception as e:
        logger.exception("Get voices failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get voices", "message": str(e)},
        )
