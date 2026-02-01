"""
Document parsing service.
Parses uploaded documents (e.g. PDF resume) to raw text so extraction can run.
"""

import logging
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
        # Stub: real impl would use pypdf for PDF, etc.
        logger.warning("parse_content stub: no extraction implemented")
        return ""
