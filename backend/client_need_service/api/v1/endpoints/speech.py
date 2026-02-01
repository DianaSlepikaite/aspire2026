"""
Speech service endpoints for STT and TTS.
"""

import logging
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, status, Depends
from fastapi.responses import Response

from client_need_service.config import get_settings
from client_need_service.models.schemas import (
    TranscriptionResponse,
    SynthesisRequest,
    VoicesResponse,
    Voice,
)
from client_need_service.services.speech_service import (
    SpeechService,
    validate_audio_input,
)
from client_need_service.core.exceptions import SpeechServiceError, AudioProcessingError

logger = logging.getLogger(__name__)

router = APIRouter()


def _audio_format_from_filename(filename: Optional[str]) -> str:
    """Derive audio format from filename extension."""
    if not filename or "." not in filename:
        return "wav"
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext if ext in ("wav", "mp3", "ogg", "m4a") else "wav"


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Transcribe audio to text",
    description="Convert audio file to text using speech-to-text. Allowed: WAV, MP3, OGG, M4A. Max size from config.",
)
async def transcribe_audio(
    audio_file: UploadFile = File(..., description="Audio file (WAV, MP3, OGG, M4A)"),
    settings=Depends(get_settings),
):
    """
    Transcribe audio to text.

    Validates file size, non-empty, and format (WAV, MP3, OGG, M4A).
    Returns error_code in detail on validation/transcription errors.
    """
    try:
        # Enforce max size before reading (Content-Length if present)
        max_bytes = settings.get_max_audio_size_bytes()
        if audio_file.size is not None and audio_file.size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": f"Audio file exceeds maximum size of {settings.MAX_AUDIO_FILE_SIZE_MB} MB",
                    "error_code": "file_too_large",
                    "details": {"max_bytes": max_bytes},
                },
            )

        audio_data = await audio_file.read()

        if len(audio_data) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": f"Audio file exceeds maximum size of {settings.MAX_AUDIO_FILE_SIZE_MB} MB",
                    "error_code": "file_too_large",
                    "details": {"max_bytes": max_bytes},
                },
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
                "details": e.details,
            },
        )
    except SpeechServiceError as e:
        logger.error("Failed to transcribe audio: %s", e)
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error": e.message,
                "error_code": e.details.get(
                    "error_code", "transcription_service_error"
                ),
                "details": e.details,
            },
        )
    except Exception as e:
        logger.exception("Unexpected error transcribing audio: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to transcribe audio",
                "error_code": "transcription_service_error",
                "details": {"error": str(e)},
            },
        )


@router.post(
    "/synthesize",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Synthesize text to speech",
    description="Convert text to speech audio using text-to-speech",
    responses={
        200: {"content": {"audio/mpeg": {}}, "description": "Audio file (MP3 format)"}
    },
)
async def synthesize_speech(request: SynthesisRequest):
    """
    Synthesize text to speech.

    Returns audio in MP3 format.
    """
    try:
        speech_service = SpeechService()

        audio_data = await speech_service.synthesize_speech(
            text=request.text, voice_name=request.voice_name, output_format="mp3"
        )

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=speech.mp3"},
        )

    except SpeechServiceError as e:
        logger.error(f"Failed to synthesize speech: {e}")
        raise HTTPException(
            status_code=e.status_code, detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error synthesizing speech: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to synthesize speech"},
        )


@router.get(
    "/voices",
    response_model=VoicesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get available voices",
    description="Get list of available text-to-speech voices",
)
async def get_voices():
    """
    Get available TTS voices.

    Returns a list of available voice options for text-to-speech.
    """
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

    except SpeechServiceError as e:
        logger.error(f"Failed to get voices: {e}")
        raise HTTPException(status_code=e.status_code, detail={"error": e.message})
    except Exception as e:
        logger.error(f"Unexpected error getting voices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get voices"},
        )
