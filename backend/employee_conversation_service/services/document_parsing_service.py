"""
Service for parsing uploaded documents (PDF, DOCX) and extracting raw text.
"""

import io
import logging
from typing import Set

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import (
    DocumentUploadError,
    DocumentParsingError,
)

logger = logging.getLogger(__name__)

# Allowed MIME types and their corresponding extensions
ALLOWED_CONTENT_TYPES: Set[str] = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".docx"}

# Maximum text length to send to GPT-4 (roughly ~25k tokens)
MAX_TEXT_LENGTH = 100_000


class DocumentParsingService:
    """Service for validating and extracting text from PDF/DOCX documents."""

    def __init__(self):
        self.settings = get_settings()

    def validate_file(
        self,
        filename: str,
        content_type: str,
        file_size: int,
    ) -> None:
        """
        Validate an uploaded file's type, extension, and size.

        Raises:
            DocumentUploadError: If validation fails.
        """
        # Check extension
        ext = ""
        if "." in filename:
            ext = "." + filename.rsplit(".", 1)[-1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            raise DocumentUploadError(
                f"Unsupported file extension '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
                details={"filename": filename, "extension": ext},
            )

        # Check content type
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise DocumentUploadError(
                f"Unsupported content type '{content_type}'. Allowed: PDF, DOCX",
                details={"filename": filename, "content_type": content_type},
            )

        # Check file size
        max_bytes = self.settings.MAX_DOCUMENT_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise DocumentUploadError(
                f"File too large ({file_size / 1024 / 1024:.1f} MB). "
                f"Maximum allowed: {self.settings.MAX_DOCUMENT_FILE_SIZE_MB} MB",
                details={
                    "filename": filename,
                    "file_size_bytes": file_size,
                    "max_size_mb": self.settings.MAX_DOCUMENT_FILE_SIZE_MB,
                },
            )

    def extract_text(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> str:
        """
        Extract text from a PDF or DOCX file.

        Args:
            file_bytes: Raw file bytes.
            filename: Original filename.
            content_type: MIME type of the file.

        Returns:
            Extracted text (truncated to MAX_TEXT_LENGTH).

        Raises:
            DocumentParsingError: If text extraction fails or yields no text.
        """
        ext = ""
        if "." in filename:
            ext = "." + filename.rsplit(".", 1)[-1].lower()

        try:
            if ext == ".pdf" or content_type == "application/pdf":
                text = self._extract_from_pdf(file_bytes)
            elif (
                ext == ".docx"
                or content_type
                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ):
                text = self._extract_from_docx(file_bytes)
            else:
                raise DocumentParsingError(
                    f"Cannot extract text from file type: {ext or content_type}",
                    details={"filename": filename},
                )
        except DocumentParsingError:
            raise
        except Exception as e:
            logger.error(f"Failed to extract text from {filename}: {e}")
            raise DocumentParsingError(
                f"Failed to extract text from document: {str(e)}",
                details={"filename": filename, "error": str(e)},
            )

        if not text or not text.strip():
            raise DocumentParsingError(
                "No text could be extracted from the document. "
                "The file may be image-based or empty.",
                details={"filename": filename},
            )

        # Truncate to stay within GPT-4 token limits
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning(
                f"Document text truncated from {len(text)} to {MAX_TEXT_LENGTH} chars"
            )
            text = text[:MAX_TEXT_LENGTH]

        logger.info(f"Extracted {len(text)} characters from {filename}")
        return text

    def _extract_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF bytes using PyPDF2."""
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            raise DocumentParsingError(
                "PyPDF2 is not installed. Install it with: pip install PyPDF2"
            )

        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            pages_text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
            return "\n\n".join(pages_text)
        except Exception as e:
            raise DocumentParsingError(
                f"Failed to parse PDF: {str(e)}",
                details={"error": str(e)},
            )

    def _extract_from_docx(self, file_bytes: bytes) -> str:
        """Extract text from DOCX bytes using python-docx."""
        try:
            from docx import Document
        except ImportError:
            raise DocumentParsingError(
                "python-docx is not installed. Install it with: pip install python-docx"
            )

        try:
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            raise DocumentParsingError(
                f"Failed to parse DOCX: {str(e)}",
                details={"error": str(e)},
            )
