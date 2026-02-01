"""
Document upload service.
Receives uploaded documents (e.g. resume/CV), optionally stores in blob, creates document record.
"""

import logging
from typing import Optional, Dict, Any

from employee_conversation_service.models.schemas import EmployeeDocumentCreate
from employee_conversation_service.services.storage_service import StorageService
from employee_conversation_service.core.exceptions import ServiceError

logger = logging.getLogger(__name__)


class DocumentUploadService:
    """Handles document upload: receive file, optionally store in blob, create document record."""

    def __init__(self) -> None:
        self.storage_service = StorageService()

    async def upload_document(
        self,
        file_content: bytes,
        file_name: Optional[str] = None,
        mime_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Any":
        """
        Receive uploaded document, create document record.
        Optionally uses BlobStorageService to store binary; always creates record via StorageService.
        """
        try:
            # In a full impl: call BlobStorageService to store file_content, get blob_url
            create = EmployeeDocumentCreate(
                file_name=file_name,
                mime_type=mime_type or "application/octet-stream",
                raw_text=None,  # Filled after parsing
                source="upload",
            )
            doc = await self.storage_service.create_document(create)
            logger.info("Uploaded document: %s", doc.id)
            return doc
        except Exception as e:
            logger.exception("Document upload failed: %s", e)
            raise ServiceError(
                f"Failed to upload document: {str(e)}",
                details={"error": str(e)},
            )
