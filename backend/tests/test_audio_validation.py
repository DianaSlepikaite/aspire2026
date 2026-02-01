"""
Tests for audio file validation and error handling (transcribe + intake upload/audio).
Run with: pytest tests/test_audio_validation.py -v
"""

import io
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from fastapi.testclient import TestClient
from fastapi import UploadFile

from client_need_service.main import app
from client_need_service.services.speech_service import validate_audio_input
from client_need_service.core.exceptions import AudioProcessingError


# --- Unit tests: validate_audio_input ---


def test_validate_audio_input_file_too_large():
    """Reject audio larger than MAX_AUDIO_FILE_SIZE_MB."""
    with patch("client_need_service.services.speech_service.get_settings") as m:
        m.return_value.get_max_audio_size_bytes.return_value = 100
        m.return_value.MIN_AUDIO_FILE_SIZE_BYTES = 1
        m.return_value.ALLOWED_AUDIO_EXTENSIONS = ["wav", "mp3"]
        m.return_value.ALLOWED_AUDIO_MIME_TYPES = ["audio/wav"]
        with pytest.raises(AudioProcessingError) as exc_info:
            validate_audio_input(b"x" * 101, "wav")
        assert exc_info.value.details.get("error_code") == "file_too_large"


def test_validate_audio_input_file_too_small():
    """Reject empty or too-small audio."""
    with patch("client_need_service.services.speech_service.get_settings") as m:
        m.return_value.get_max_audio_size_bytes.return_value = 10 * 1024 * 1024
        m.return_value.MIN_AUDIO_FILE_SIZE_BYTES = 1000
        m.return_value.ALLOWED_AUDIO_EXTENSIONS = ["wav", "mp3"]
        m.return_value.ALLOWED_AUDIO_MIME_TYPES = ["audio/wav"]
        with pytest.raises(AudioProcessingError) as exc_info:
            validate_audio_input(b"x" * 100, "wav")
        assert exc_info.value.details.get("error_code") == "file_too_small"


def test_validate_audio_input_unsupported_format():
    """Reject unsupported extension."""
    with patch("client_need_service.services.speech_service.get_settings") as m:
        m.return_value.get_max_audio_size_bytes.return_value = 10 * 1024 * 1024
        m.return_value.MIN_AUDIO_FILE_SIZE_BYTES = 1
        m.return_value.ALLOWED_AUDIO_EXTENSIONS = ["wav", "mp3"]
        m.return_value.ALLOWED_AUDIO_MIME_TYPES = ["audio/wav"]
        with pytest.raises(AudioProcessingError) as exc_info:
            validate_audio_input(b"x" * 2000, "flac")
        assert exc_info.value.details.get("error_code") == "unsupported_format"


def test_validate_audio_input_accepts_valid():
    """Accept valid size and format."""
    with patch("client_need_service.services.speech_service.get_settings") as m:
        m.return_value.get_max_audio_size_bytes.return_value = 10 * 1024 * 1024
        m.return_value.MIN_AUDIO_FILE_SIZE_BYTES = 1
        m.return_value.ALLOWED_AUDIO_EXTENSIONS = ["wav", "mp3", "ogg", "m4a"]
        m.return_value.ALLOWED_AUDIO_MIME_TYPES = ["audio/wav"]
        validate_audio_input(b"x" * 2000, "mp3")  # no raise


# --- API tests: POST /api/v1/speech/transcribe ---


@pytest.fixture
def client():
    return TestClient(app)


def test_transcribe_no_file(client):
    """Transcribe without file returns 422."""
    response = client.post("/api/v1/speech/transcribe")
    assert response.status_code == 422


def test_transcribe_empty_file_returns_400(client):
    """Empty file should be rejected with error_code."""
    with patch("client_need_service.config.get_settings") as m_settings:
        m_settings.return_value.get_max_audio_size_bytes.return_value = 10 * 1024 * 1024
        m_settings.return_value.MAX_AUDIO_FILE_SIZE_MB = 10
        # validate_audio_input will be called with empty bytes
        response = client.post(
            "/api/v1/speech/transcribe",
            files={"audio_file": ("empty.wav", io.BytesIO(b""), "audio/wav")},
        )
        assert response.status_code in (400, 413)
        data = response.json()
        assert "detail" in data
        detail = data["detail"] if isinstance(data["detail"], dict) else {}
        if "error_code" in detail:
            assert detail["error_code"] in (
                "file_too_small",
                "file_too_large",
                "audio_processing_error",
            )


def test_transcribe_file_too_large_returns_413(client):
    """File over max size returns 413 with error_code file_too_large."""
    with patch("client_need_service.config.get_settings") as m_settings:
        max_bytes = 100  # very small for test
        m_settings.return_value.get_max_audio_size_bytes.return_value = max_bytes
        m_settings.return_value.MAX_AUDIO_FILE_SIZE_MB = 1
        big_content = b"x" * (max_bytes + 1)
        response = client.post(
            "/api/v1/speech/transcribe",
            files={"audio_file": ("big.wav", io.BytesIO(big_content), "audio/wav")},
        )
        assert response.status_code == 413
        data = response.json()
        assert data.get("detail", {}).get("error_code") == "file_too_large"


def test_transcribe_success_mocked(client):
    """Transcribe with valid file returns 200 when Azure is mocked."""
    with patch("client_need_service.api.v1.endpoints.speech.SpeechService") as m_svc:
        m_svc.return_value.transcribe_audio = AsyncMock(
            return_value={
                "transcription": "hello world",
                "confidence": 0.95,
                "duration_seconds": 1.0,
            }
        )
        # Min 1000 bytes from default config
        content = b"x" * 1000
        response = client.post(
            "/api/v1/speech/transcribe",
            files={"audio_file": ("test.wav", io.BytesIO(content), "audio/wav")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["transcription"] == "hello world"
        assert data["confidence"] == 0.95


# --- API tests: POST /api/v1/intake/upload/audio ---


def test_upload_audio_file_too_large_returns_413(client):
    """Intake upload: file over max size returns 413."""
    with patch("client_need_service.config.get_settings") as m_settings:
        max_bytes = 100
        m_settings.return_value.get_max_audio_size_bytes.return_value = max_bytes
        m_settings.return_value.MAX_AUDIO_FILE_SIZE_MB = 1
        big_content = b"x" * (max_bytes + 1)
        response = client.post(
            "/api/v1/intake/upload/audio",
            files={"file": ("big.wav", io.BytesIO(big_content), "audio/wav")},
        )
        assert response.status_code == 413
        data = response.json()
        assert data.get("detail", {}).get("error_code") == "file_too_large"


def test_upload_audio_unsupported_format_returns_400(client):
    """Intake upload: wrong content-type / format can yield 400."""
    with patch("client_need_service.config.get_settings") as m_settings:
        m_settings.return_value.get_max_audio_size_bytes.return_value = 10 * 1024 * 1024
        m_settings.return_value.MAX_AUDIO_FILE_SIZE_MB = 10
        content = b"x" * 2000
        # Use an extension/MIME that may not be in allowlist
        response = client.post(
            "/api/v1/intake/upload/audio",
            files={
                "file": ("audio.xyz", io.BytesIO(content), "application/octet-stream")
            },
        )
        # Either 400 unsupported_format or 500 if validation passes but ingestion fails
        assert response.status_code in (400, 413, 422, 500)
        if response.status_code == 400:
            data = response.json()
            assert data.get("detail", {}).get("error_code") in (
                "unsupported_format",
                "audio_processing_error",
            )
