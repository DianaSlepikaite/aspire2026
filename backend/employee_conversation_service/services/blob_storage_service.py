"""
Blob storage service (optional).
Store/retrieve document binaries (e.g. resume PDF) in blob storage.
"""

import logging
from typing import Optional
from uuid import UUID

from employee_conversation_service.core.exceptions import ServiceError

logger = logging.getLogger(__name__)


class BlobStorageService:
    """Store and retrieve document binaries in blob storage (optional)."""

    async def store_document(
        self, document_id: UUID, content: bytes, content_type: Optional[str] = None
    ) -> str:
        """Store document binary; return blob URL or key."""
        logger.warning("BlobStorageService stub: store_document not implemented")
        return f"blob://stub/{document_id}"

    async def get_document(self, document_id: UUID) -> Optional[bytes]:
        """Retrieve document binary by ID."""
        logger.warning("BlobStorageService stub: get_document not implemented")
        return None
