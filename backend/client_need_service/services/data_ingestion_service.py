"""
Data Ingestion Service for reliable collection, normalization, and preservation
of client inputs as a trustworthy source of truth.

This service is deterministic and auditable - it transforms data mechanically
without interpreting or deciding meaning.
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from client_need_service.models.schemas import (
    IntakeSourceType,
    IntakeStatus,
    ClientIntakePackageCreate,
    ClientIntakePackage,
    IntakeMetadata,
    NormalizedContent
)
from client_need_service.utils.document_processor import DocumentProcessor
from client_need_service.services.speech_service import SpeechService
from client_need_service.core.exceptions import ServiceError

logger = logging.getLogger(__name__)


class DataIngestionService:
    """
    Service for deterministic, auditable data ingestion.

    Responsibilities:
    1. Accept any client-provided material
    2. Normalize to canonical format (mechanical, not interpretive)
    3. Output ClientIntakePackage with provenance and compliance
    """

    def __init__(self):
        """Initialize data ingestion service."""
        self.document_processor = DocumentProcessor()
        self.speech_service = SpeechService()

    async def ingest_pdf(
        self,
        pdf_content: bytes,
        metadata: Optional[IntakeMetadata] = None,
        client_name: Optional[str] = None,
        client_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest PDF document.

        Args:
            pdf_content: PDF file bytes
            metadata: Optional metadata
            client_name: Optional client name
            client_email: Optional client email

        Returns:
            Dictionary ready for ClientIntakePackage creation

        Raises:
            ServiceError: If ingestion fails
        """
        try:
            logger.info("Starting PDF ingestion")

            audit_trail = []
            audit_trail.append({
                "step": "intake",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "received_pdf",
                "size_bytes": len(pdf_content)
            })

            # Extract text from PDF
            try:
                processed = self.document_processor.process_document(
                    content=pdf_content,
                    content_type='application/pdf',
                    extract_sections=True
                )

                audit_trail.append({
                    "step": "extraction",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": "extracted_text_from_pdf",
                    "word_count": processed.get("word_count"),
                    "num_pages": processed.get("num_pages")
                })

            except Exception as e:
                audit_trail.append({
                    "step": "extraction",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": "extraction_failed",
                    "error": str(e)
                })
                raise

            # Create normalized content
            normalized_content = NormalizedContent(
                text=processed["text"],
                sections=processed.get("sections"),
                word_count=processed.get("word_count"),
                language=processed.get("language")
            )

            # Update metadata if provided
            if metadata is None:
                metadata = IntakeMetadata()

            if not metadata.mime_type:
                metadata.mime_type = "application/pdf"

            audit_trail.append({
                "step": "normalization",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "created_normalized_content",
                "sections_count": len(processed.get("sections", []))
            })

            logger.info(f"Successfully ingested PDF: {processed.get('word_count')} words")

            return {
                "source_type": IntakeSourceType.PDF,
                "raw_content": processed["text"],  # Store extracted text as raw
                "normalized_content": normalized_content.model_dump(),
                "metadata": metadata.model_dump() if metadata else None,
                "client_name": client_name,
                "client_email": client_email,
                "audit_trail": audit_trail,
                "status": IntakeStatus.COMPLETED
            }

        except Exception as e:
            logger.error(f"PDF ingestion failed: {e}")
            raise ServiceError(
                f"Failed to ingest PDF: {str(e)}",
                details={"error": str(e), "audit_trail": audit_trail}
            )

    async def ingest_text(
        self,
        text_content: str,
        metadata: Optional[IntakeMetadata] = None,
        client_name: Optional[str] = None,
        client_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest plain text content.

        Args:
            text_content: Text content
            metadata: Optional metadata
            client_name: Optional client name
            client_email: Optional client email

        Returns:
            Dictionary ready for ClientIntakePackage creation

        Raises:
            ServiceError: If ingestion fails
        """
        try:
            logger.info("Starting text ingestion")

            audit_trail = []
            audit_trail.append({
                "step": "intake",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "received_text",
                "size_chars": len(text_content)
            })

            # Normalize text
            normalized_text = self.document_processor.normalize_text(text_content)

            # Extract sections
            sections = self.document_processor.extract_sections(normalized_text)

            # Calculate metadata
            word_count = self.document_processor.calculate_word_count(normalized_text)
            language = self.document_processor.detect_language(normalized_text)

            audit_trail.append({
                "step": "normalization",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "normalized_text",
                "word_count": word_count,
                "sections_count": len(sections)
            })

            # Create normalized content
            normalized_content = NormalizedContent(
                text=normalized_text,
                sections=sections,
                word_count=word_count,
                language=language
            )

            # Update metadata
            if metadata is None:
                metadata = IntakeMetadata()

            if not metadata.mime_type:
                metadata.mime_type = "text/plain"

            logger.info(f"Successfully ingested text: {word_count} words")

            return {
                "source_type": IntakeSourceType.TEXT,
                "raw_content": text_content,
                "normalized_content": normalized_content.model_dump(),
                "metadata": metadata.model_dump() if metadata else None,
                "client_name": client_name,
                "client_email": client_email,
                "audit_trail": audit_trail,
                "status": IntakeStatus.COMPLETED
            }

        except Exception as e:
            logger.error(f"Text ingestion failed: {e}")
            raise ServiceError(
                f"Failed to ingest text: {str(e)}",
                details={"error": str(e)}
            )

    async def ingest_audio(
        self,
        audio_content: bytes,
        metadata: Optional[IntakeMetadata] = None,
        client_name: Optional[str] = None,
        client_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest audio file (transcribe to text).

        Args:
            audio_content: Audio file bytes
            metadata: Optional metadata
            client_name: Optional client name
            client_email: Optional client email

        Returns:
            Dictionary ready for ClientIntakePackage creation

        Raises:
            ServiceError: If ingestion fails
        """
        try:
            logger.info("Starting audio ingestion")

            audit_trail = []
            audit_trail.append({
                "step": "intake",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "received_audio",
                "size_bytes": len(audio_content)
            })

            # Transcribe audio to text
            try:
                transcription_result = await self.speech_service.transcribe_audio(
                    audio_content
                )

                transcript_text = transcription_result.get("text", "")

                audit_trail.append({
                    "step": "transcription",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": "transcribed_audio",
                    "confidence": transcription_result.get("confidence"),
                    "duration": transcription_result.get("duration")
                })

            except Exception as e:
                audit_trail.append({
                    "step": "transcription",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "action": "transcription_failed",
                    "error": str(e)
                })
                raise ServiceError(
                    f"Audio transcription failed: {str(e)}",
                    details={"error": str(e), "audit_trail": audit_trail}
                )

            # Normalize transcribed text
            normalized_text = self.document_processor.normalize_text(transcript_text)
            sections = self.document_processor.extract_sections(normalized_text)
            word_count = self.document_processor.calculate_word_count(normalized_text)
            language = self.document_processor.detect_language(normalized_text)

            audit_trail.append({
                "step": "normalization",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action": "normalized_transcript",
                "word_count": word_count
            })

            # Create normalized content
            normalized_content = NormalizedContent(
                text=normalized_text,
                sections=sections,
                word_count=word_count,
                language=language
            )

            # Update metadata
            if metadata is None:
                metadata = IntakeMetadata()

            if not metadata.mime_type:
                metadata.mime_type = "audio/wav"  # Default, should be provided

            logger.info(f"Successfully ingested audio: {word_count} words from transcript")

            return {
                "source_type": IntakeSourceType.AUDIO,
                "raw_content": transcript_text,  # Store transcript as raw
                "normalized_content": normalized_content.model_dump(),
                "metadata": metadata.model_dump() if metadata else None,
                "client_name": client_name,
                "client_email": client_email,
                "audit_trail": audit_trail,
                "status": IntakeStatus.COMPLETED
            }

        except ServiceError:
            raise
        except Exception as e:
            logger.error(f"Audio ingestion failed: {e}")
            raise ServiceError(
                f"Failed to ingest audio: {str(e)}",
                details={"error": str(e)}
            )

    def create_audit_entry(
        self,
        step: str,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create standardized audit trail entry.

        Args:
            step: Processing step name
            action: Action taken
            **kwargs: Additional metadata

        Returns:
            Audit entry dictionary
        """
        return {
            "step": step,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            **kwargs
        }
