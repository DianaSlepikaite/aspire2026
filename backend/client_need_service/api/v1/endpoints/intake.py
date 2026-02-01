"""
Intake endpoints for client data ingestion.
Handles file uploads, text submissions, and audio transcription.
"""

import logging
from uuid import UUID
from typing import Optional
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    HTTPException,
    Query,
    status,
    Depends,
)

from client_need_service.config import get_settings
from client_need_service.models.schemas import (
    ClientIntakePackage,
    ClientIntakePackageList,
    IntakeMetadata,
    IntakeSourceType,
)
from client_need_service.services.data_ingestion_service import DataIngestionService
from client_need_service.services.storage_service import StorageService
from client_need_service.services.speech_service import validate_audio_input
from client_need_service.core.exceptions import (
    ServiceError,
    StorageError,
    AudioProcessingError,
    SpeechServiceError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _audio_format_from_filename(filename: Optional[str]) -> str:
    """Derive audio format from filename extension."""
    if not filename or "." not in filename:
        return "wav"
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext if ext in ("wav", "mp3", "ogg", "m4a") else "wav"


@router.post(
    "/upload/pdf",
    response_model=ClientIntakePackage,
    status_code=status.HTTP_201_CREATED,
    summary="Upload PDF document",
    description="Upload a PDF document for ingestion and normalization",
)
async def upload_pdf(
    file: UploadFile = File(..., description="PDF file to upload"),
    client_name: Optional[str] = Form(None),
    client_email: Optional[str] = Form(None),
    tags: Optional[str] = Form(None, description="Comma-separated tags"),
):
    """
    Upload and ingest a PDF document.

    The PDF will be:
    1. Text extracted
    2. Normalized
    3. Sectioned
    4. Stored with audit trail
    """
    try:
        logger.info(f"Received PDF upload: {file.filename}")

        # Validate file type
        if not file.content_type == "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Invalid file type. Only PDF files are accepted."},
            )

        # Read file content
        pdf_content = await file.read()

        # Create metadata
        metadata = IntakeMetadata(
            file_name=file.filename,
            file_size_bytes=len(pdf_content),
            mime_type=file.content_type,
            tags=tags.split(",") if tags else None,
        )

        # Ingest PDF
        ingestion_service = DataIngestionService()
        intake_data = await ingestion_service.ingest_pdf(
            pdf_content=pdf_content,
            metadata=metadata,
            client_name=client_name,
            client_email=client_email,
        )

        # Save to database
        storage_service = StorageService()
        intake_package = await storage_service.create_intake_package(intake_data)

        logger.info(f"Successfully created intake package: {intake_package.id}")

        return intake_package

    except HTTPException:
        raise
    except ServiceError as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "details": e.details},
        )
    except Exception as e:
        logger.error(f"Unexpected error during PDF upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to process PDF upload"},
        )


@router.post(
    "/upload/text",
    response_model=ClientIntakePackage,
    status_code=status.HTTP_201_CREATED,
    summary="Submit text content",
    description="Submit raw text content for ingestion and normalization",
)
async def upload_text(
    text_content: str = Form(..., description="Text content to ingest"),
    client_name: Optional[str] = Form(None),
    client_email: Optional[str] = Form(None),
    source_label: Optional[str] = Form(
        None, description="Label for text source (e.g., 'email', 'chat')"
    ),
    tags: Optional[str] = Form(None, description="Comma-separated tags"),
):
    """
    Ingest plain text content.

    The text will be:
    1. Normalized
    2. Sectioned
    3. Analyzed
    4. Stored with audit trail
    """
    try:
        logger.info("Received text submission")

        # Create metadata
        metadata = IntakeMetadata(
            file_name=source_label or "text_submission",
            file_size_bytes=len(text_content.encode("utf-8")),
            mime_type="text/plain",
            tags=tags.split(",") if tags else None,
        )

        # Ingest text
        ingestion_service = DataIngestionService()
        intake_data = await ingestion_service.ingest_text(
            text_content=text_content,
            metadata=metadata,
            client_name=client_name,
            client_email=client_email,
        )

        # Save to database
        storage_service = StorageService()
        intake_package = await storage_service.create_intake_package(intake_data)

        logger.info(f"Successfully created intake package: {intake_package.id}")

        return intake_package

    except ServiceError as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "details": e.details},
        )
    except Exception as e:
        logger.error(f"Unexpected error during text submission: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to process text submission"},
        )


@router.post(
    "/upload/audio",
    response_model=ClientIntakePackage,
    status_code=status.HTTP_201_CREATED,
    summary="Upload audio file",
    description="Upload audio file for transcription and ingestion. Allowed: WAV, MP3, OGG, M4A. Max size from config.",
)
async def upload_audio(
    file: UploadFile = File(
        ..., description="Audio file to upload (WAV, MP3, OGG, M4A)"
    ),
    client_name: Optional[str] = Form(None),
    client_email: Optional[str] = Form(None),
    tags: Optional[str] = Form(None, description="Comma-separated tags"),
    settings=Depends(get_settings),
):
    """
    Upload and ingest an audio file.

    Validates file size, non-empty, and format (WAV, MP3, OGG, M4A).
    Returns error_code in detail on validation/transcription errors.
    The audio will be transcribed, normalized, sectioned, and stored with audit trail.
    """
    try:
        logger.info("Received audio upload: %s", file.filename)

        max_bytes = settings.get_max_audio_size_bytes()
        if file.size is not None and file.size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": f"Audio file exceeds maximum size of {settings.MAX_AUDIO_FILE_SIZE_MB} MB",
                    "error_code": "file_too_large",
                    "details": {"max_bytes": max_bytes},
                },
            )

        audio_content = await file.read()

        if len(audio_content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": f"Audio file exceeds maximum size of {settings.MAX_AUDIO_FILE_SIZE_MB} MB",
                    "error_code": "file_too_large",
                    "details": {"max_bytes": max_bytes},
                },
            )

        audio_format = _audio_format_from_filename(file.filename)
        content_type = file.content_type or ""
        validate_audio_input(audio_content, audio_format, file.filename, content_type)

        metadata = IntakeMetadata(
            file_name=file.filename,
            file_size_bytes=len(audio_content),
            mime_type=file.content_type,
            tags=tags.split(",") if tags else None,
        )

        ingestion_service = DataIngestionService()
        intake_data = await ingestion_service.ingest_audio(
            audio_content=audio_content,
            metadata=metadata,
            client_name=client_name,
            client_email=client_email,
        )

        storage_service = StorageService()
        intake_package = await storage_service.create_intake_package(intake_data)

        logger.info("Successfully created intake package: %s", intake_package.id)

        return intake_package

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
        logger.error("Audio transcription failed: %s", e)
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
    except ServiceError as e:
        logger.error("Ingestion failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": e.message,
                "error_code": "ingestion_error",
                "details": e.details,
            },
        )
    except Exception as e:
        logger.exception("Unexpected error during audio upload: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to process audio upload",
                "error_code": "transcription_service_error",
                "details": {"error": str(e)},
            },
        )


@router.get(
    "",
    response_model=ClientIntakePackageList,
    status_code=status.HTTP_200_OK,
    summary="List intake packages",
    description="Get a paginated list of intake packages with optional filters",
)
async def list_intake_packages(
    status_filter: Optional[str] = Query(
        None, alias="status", description="Filter by status"
    ),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    client_email: Optional[str] = Query(None, description="Filter by client email"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """
    List intake packages with optional filters.

    Supports filtering by:
    - Status (pending, processing, completed, failed)
    - Source type (pdf, text, audio, etc.)
    - Client email
    """
    try:
        storage_service = StorageService()

        # Build filters
        filters = {}
        if status_filter:
            filters["status"] = status_filter
        if source_type:
            filters["source_type"] = source_type
        if client_email:
            filters["client_email"] = client_email

        # Get intake packages
        packages, total = await storage_service.list_intake_packages(
            filters=filters, limit=limit, offset=offset
        )

        return ClientIntakePackageList(
            items=packages, total=total, limit=limit, offset=offset
        )

    except StorageError as e:
        logger.error(f"Failed to list intake packages: {e}")
        raise HTTPException(
            status_code=e.status_code, detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error listing intake packages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to list intake packages"},
        )


@router.get(
    "/{id}",
    response_model=ClientIntakePackage,
    status_code=status.HTTP_200_OK,
    summary="Get intake package",
    description="Get a specific intake package by ID",
)
async def get_intake_package(id: UUID):
    """
    Get an intake package by ID.

    Returns the complete package including:
    - Raw content
    - Normalized content
    - Metadata
    - Audit trail
    """
    try:
        storage_service = StorageService()

        intake_package = await storage_service.get_intake_package(id)

        if not intake_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": f"Intake package not found: {id}"},
            )

        return intake_package

    except HTTPException:
        raise
    except StorageError as e:
        logger.error(f"Failed to get intake package: {e}")
        raise HTTPException(
            status_code=e.status_code, detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error getting intake package: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to get intake package"},
        )
