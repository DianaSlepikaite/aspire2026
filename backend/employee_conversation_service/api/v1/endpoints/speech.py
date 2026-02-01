"""
Speech service endpoints for STT and TTS.
"""

import logging
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import Response

from employee_conversation_service.models.schemas import (
    TranscriptionResponse,
    SynthesisRequest,
    VoicesResponse,
    Voice
)
from employee_conversation_service.services.speech_service import SpeechService
from employee_conversation_service.core.exceptions import SpeechServiceError, AudioProcessingError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Transcribe audio to text",
    description="Convert audio file to text using speech-to-text"
)
async def transcribe_audio(
    audio_file: UploadFile = File(..., description="Audio file (WAV, MP3, OGG)")
):
    """
    Transcribe audio to text.

    Supports WAV, MP3, and OGG audio formats.
    """
    try:
        # Read audio data
        audio_data = await audio_file.read()

        # Detect audio format from filename
        audio_format = "wav"
        if audio_file.filename:
            if audio_file.filename.endswith(".mp3"):
                audio_format = "mp3"
            elif audio_file.filename.endswith(".ogg"):
                audio_format = "ogg"

        # Transcribe
        speech_service = SpeechService()
        result = await speech_service.transcribe_audio(audio_data, audio_format)

        return TranscriptionResponse(
            transcription=result["transcription"],
            confidence=result["confidence"],
            duration_seconds=result["duration_seconds"]
        )

    except AudioProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": e.message, "details": e.details}
        )
    except SpeechServiceError as e:
        logger.error(f"Failed to transcribe audio: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error transcribing audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to transcribe audio"}
        )


@router.post(
    "/synthesize",
    response_class=Response,
    status_code=status.HTTP_200_OK,
    summary="Synthesize text to speech",
    description="Convert text to speech audio using text-to-speech",
    responses={
        200: {
            "content": {"audio/mpeg": {}},
            "description": "Audio file (MP3 format)"
        }
    }
)
async def synthesize_speech(request: SynthesisRequest):
    """
    Synthesize text to speech.

    Returns audio in MP3 format.
    """
    try:
        speech_service = SpeechService()

        audio_data = await speech_service.synthesize_speech(
            text=request.text,
            voice_name=request.voice_name,
            output_format="mp3"
        )

        return Response(
            content=audio_data,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )

    except SpeechServiceError as e:
        logger.error(f"Failed to synthesize speech: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error synthesizing speech: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to synthesize speech"}
        )


@router.get(
    "/voices",
    response_model=VoicesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get available voices",
    description="Get list of available text-to-speech voices"
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
                locale=v["locale"]
            )
            for v in voices_data
        ]

        return VoicesResponse(voices=voices)

    except SpeechServiceError as e:
        logger.error(f"Failed to get voices: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message}
        )
    except Exception as e:
        logger.error(f"Unexpected error getting voices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get voices"}
        )
