"""
Document parsing service.
Parses uploaded documents (e.g. PDF resume) to raw text so extraction can run.
"""

import logging
from io import BytesIO
from zipfile import BadZipFile
from typing import Optional
from uuid import UUID

from employee_conversation_service.services.storage_service import StorageService
from employee_conversation_service.core.exceptions import (
    DocumentNotFoundError,
    ServiceError,
)

logger = logging.getLogger(__name__)


class DocumentParsingService:
    """Parse documents (PDF, etc.) to raw text."""

    def __init__(self) -> None:
        self.storage_service = StorageService()

    async def parse_document(self, document_id: UUID) -> str:
        """
        Parse document to raw text.
        Fetches document (and binary from BlobStorageService if needed), extracts text, updates document.raw_text.
        """
        doc = await self.storage_service.get_document(document_id)
        if not doc:
            raise DocumentNotFoundError(str(document_id))
        # Stub: if raw_text already set (e.g. from upload path), return it
        if doc.raw_text:
            return doc.raw_text
        # Stub: no PDF parsing yet; in real impl use pypdf or similar
        logger.warning(
            "Document parsing stub: no text extraction for document %s", document_id
        )
        return ""

    async def parse_content(
        self, file_content: bytes, mime_type: Optional[str] = None
    ) -> str:
        """Parse raw bytes to text (e.g. PDF bytes -> text). Used when content is in memory."""
        if not file_content:
            return ""
        mime = (mime_type or "").lower()
        is_pdf = mime == "application/pdf" or file_content[:4] == b"%PDF"
        is_docx = mime in (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
        ) or file_content[:2] == b"PK"

        if is_pdf:
            try:
                from pypdf import PdfReader

                reader = PdfReader(BytesIO(file_content))
                parts = []
                for page in reader.pages:
                    text = page.extract_text() or ""
                    if text.strip():
                        parts.append(text)
                return "\n".join(parts).strip()
            except Exception as exc:
                logger.exception("parse_content (pdf) failed: %s", exc)
                return ""

        if is_docx:
            try:
                from docx import Document

                document = Document(BytesIO(file_content))
                parts = [p.text for p in document.paragraphs if p.text and p.text.strip()]
                for table in document.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            cell_text = cell.text.strip()
                            if cell_text:
                                parts.append(cell_text)
                return "\n".join(parts).strip()
            except BadZipFile as exc:
                logger.exception("parse_content (docx) failed: %s", exc)
                return ""
            except Exception as exc:
                logger.exception("parse_content (docx) failed: %s", exc)
                return ""

        logger.warning("parse_content: unsupported mime_type=%s", mime_type)
        return ""
