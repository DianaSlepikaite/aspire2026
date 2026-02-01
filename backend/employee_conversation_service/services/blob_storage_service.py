"""
Azure Blob Storage service for uploading and managing documents.
"""

import logging
from typing import Optional, Dict, Any

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import BlobStorageError

logger = logging.getLogger(__name__)


class BlobStorageService:
    """Service for interacting with Azure Blob Storage."""

    def __init__(self):
        self.settings = get_settings()
        self._client = None
        self._container_client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Azure Blob Storage client."""
        if not self.settings.has_azure_blob_credentials():
            logger.warning(
                "Azure Blob Storage credentials not configured. "
                "Document uploads will not be persisted to blob storage."
            )
            return

        try:
            from azure.storage.blob.aio import BlobServiceClient

            self._client = BlobServiceClient.from_connection_string(
                self.settings.AZURE_BLOB_CONNECTION_STRING
            )
            logger.info("Azure Blob Storage client initialized")
        except ImportError:
            logger.warning(
                "azure-storage-blob not installed. "
                "Install with: pip install azure-storage-blob"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Blob Storage client: {e}")

    def _ensure_client(self):
        """Ensure the blob storage client is available."""
        if self._client is None:
            raise BlobStorageError(
                "Azure Blob Storage client not initialized. "
                "Configure AZURE_BLOB_CONNECTION_STRING in environment."
            )

    async def upload_document(
        self,
        file_bytes: bytes,
        document_id: str,
        filename: str,
        content_type: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Upload a document to Azure Blob Storage.

        Args:
            file_bytes: Raw file content.
            document_id: Unique document identifier.
            filename: Original filename.
            content_type: MIME type of the file.
            metadata: Optional metadata to attach to the blob.

        Returns:
            Blob URL of the uploaded document.

        Raises:
            BlobStorageError: If upload fails.
        """
        self._ensure_client()

        blob_path = f"documents/{document_id}/{filename}"

        try:
            container_client = self._client.get_container_client(
                self.settings.AZURE_BLOB_CONTAINER_NAME
            )

            # Ensure container exists
            try:
                await container_client.create_container()
            except Exception:
                # Container may already exist
                pass

            blob_client = container_client.get_blob_client(blob_path)

            await blob_client.upload_blob(
                file_bytes,
                content_settings={
                    "content_type": content_type,
                },
                metadata=metadata or {},
                overwrite=True,
            )

            blob_url = blob_client.url
            logger.info(f"Uploaded document to blob: {blob_path}")
            return blob_url

        except BlobStorageError:
            raise
        except Exception as e:
            logger.error(f"Failed to upload document to blob storage: {e}")
            raise BlobStorageError(
                f"Failed to upload document: {str(e)}",
                details={"blob_path": blob_path, "error": str(e)},
            )

    async def check_health(self) -> bool:
        """
        Check if Azure Blob Storage is available.

        Returns:
            True if healthy, False otherwise.
        """
        if self._client is None:
            return False

        try:
            # List containers as a health check
            async for _ in self._client.list_containers(max_results=1):
                break
            return True
        except Exception as e:
            logger.error(f"Blob Storage health check failed: {e}")
            return False
