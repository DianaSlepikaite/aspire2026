"""
Orchestrator service for document upload workflows.
Coordinates parsing, extraction, blob storage, and DB operations.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.database import get_db_pool
from employee_conversation_service.core.exceptions import (
    ConversationNotFoundError,
    StorageError,
)
from employee_conversation_service.models.schemas import (
    DocumentSource,
    DocumentUploadResponse,
    ConversationDocumentUploadResponse,
    EmployeeProfileUpdate,
    ConversationMessageCreate,
    MessageRole,
    MessageType,
)
from employee_conversation_service.services.document_parsing_service import (
    DocumentParsingService,
)
from employee_conversation_service.services.document_extraction_service import (
    DocumentExtractionService,
)
from employee_conversation_service.services.blob_storage_service import (
    BlobStorageService,
)
from employee_conversation_service.services.storage_service import StorageService
from employee_conversation_service.services.skill_extraction_service import (
    SkillExtractionService,
)

logger = logging.getLogger(__name__)

DOCUMENTS_TABLE = "employee_agent.employee_documents"


class DocumentUploadService:
    """Orchestrator for document upload, extraction, and profile merge."""

    def __init__(self):
        self.settings = get_settings()
        self.parsing_service = DocumentParsingService()
        self.extraction_service = DocumentExtractionService()
        self.blob_service = BlobStorageService()
        self.storage_service = StorageService()
        self.skill_extraction = SkillExtractionService()

    async def upload_standalone(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        employee_id: Optional[str] = None,
        employee_email: Optional[str] = None,
    ) -> DocumentUploadResponse:
        """
        Handle a standalone document upload (before/without a conversation).

        Steps:
        1. Validate file (type, size)
        2. Extract text from PDF/DOCX
        3. Send text to GPT-4 for structured extraction
        4. Upload original to blob storage (best-effort)
        5. Save record to employee_documents table
        6. Return DocumentUploadResponse
        """
        document_id = uuid4()
        warnings = []

        # 1. Validate
        self.parsing_service.validate_file(filename, content_type, len(file_bytes))

        # 2. Extract text
        document_text = self.parsing_service.extract_text(
            file_bytes, filename, content_type
        )

        # 3. GPT-4 extraction
        extracted_data, summary, fields_extracted = (
            await self.extraction_service.extract_profile_from_text(
                document_text, filename
            )
        )

        # 4. Blob upload (best-effort)
        blob_url = None
        try:
            if self.settings.has_azure_blob_credentials():
                blob_url = await self.blob_service.upload_document(
                    file_bytes=file_bytes,
                    document_id=str(document_id),
                    filename=filename,
                    content_type=content_type,
                    metadata={
                        "employee_id": employee_id or "",
                        "employee_email": employee_email or "",
                        "upload_source": "standalone",
                    },
                )
        except Exception as e:
            logger.warning(f"Blob upload failed (non-fatal): {e}")
            warnings.append("Document could not be uploaded to blob storage")

        # 5. Save to employee_documents table
        try:
            await self._save_document_record(
                document_id=document_id,
                employee_id=employee_id,
                employee_email=employee_email,
                conversation_id=None,
                profile_id=None,
                filename=filename,
                content_type=content_type,
                file_size_bytes=len(file_bytes),
                blob_url=blob_url,
                blob_path=f"documents/{document_id}/{filename}" if blob_url else None,
                upload_source=DocumentSource.STANDALONE.value,
                extraction_status="completed",
                extracted_fields=fields_extracted,
                extracted_data=extracted_data.model_dump(exclude_none=True),
                raw_text_length=len(document_text),
            )
        except Exception as e:
            logger.warning(f"Failed to save document record (non-fatal): {e}")
            warnings.append("Document metadata could not be saved to database")

        return DocumentUploadResponse(
            document_id=document_id,
            filename=filename,
            blob_url=blob_url,
            extracted_data=extracted_data,
            extraction_summary=summary,
            fields_extracted=fields_extracted,
            warnings=warnings,
        )

    async def upload_for_conversation(
        self,
        conversation_id: UUID,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> ConversationDocumentUploadResponse:
        """
        Handle a document upload within an existing conversation.

        Steps:
        1. Validate file
        2. Fetch existing profile by conversation_id
        3. Extract text from PDF/DOCX
        4. Send text to GPT-4 for structured extraction
        5. Merge into existing profile (document fills gaps)
        6. Update profile in DB
        7. Recalculate completeness
        8. Upload to blob storage (best-effort)
        9. Save record to employee_documents
        10. Save system message noting the upload
        11. Return ConversationDocumentUploadResponse
        """
        document_id = uuid4()
        warnings = []

        # 1. Validate
        self.parsing_service.validate_file(filename, content_type, len(file_bytes))

        # 2. Fetch existing profile
        employee_profile = await self.storage_service.get_by_conversation_id(
            conversation_id
        )
        if not employee_profile:
            raise ConversationNotFoundError(str(conversation_id))

        # 3. Extract text
        document_text = self.parsing_service.extract_text(
            file_bytes, filename, content_type
        )

        # 4. GPT-4 extraction
        extracted_data, summary, fields_extracted = (
            await self.extraction_service.extract_profile_from_text(
                document_text, filename
            )
        )

        # 5. Merge into existing profile
        existing_dict = employee_profile.model_dump(exclude_none=True)
        merged_update, merged_fields, skipped_fields = (
            self.extraction_service.merge_document_into_profile(
                existing_dict, extracted_data
            )
        )

        # 6. Update profile in DB with merged data
        if merged_fields:
            # Also append to uploaded_documents JSONB
            doc_metadata = {
                "document_id": str(document_id),
                "filename": filename,
                "uploaded_at": datetime.utcnow().isoformat(),
                "fields_merged": merged_fields,
                "extraction_status": "completed",
            }

            existing_docs = existing_dict.get("uploaded_documents") or []
            existing_docs.append(doc_metadata)

            merged_dict = merged_update.model_dump(exclude_none=True)
            merged_dict["uploaded_documents"] = existing_docs

            update = EmployeeProfileUpdate(**merged_dict)
            employee_profile = await self.storage_service.update_employee_profile(
                employee_profile.id, update
            )

        # 7. Recalculate completeness
        profile_dict = employee_profile.model_dump(exclude_none=True)
        completeness = self.skill_extraction.calculate_completeness_score(profile_dict)
        missing_fields = self.skill_extraction.identify_missing_fields(profile_dict)
        can_complete = self.skill_extraction.can_complete_conversation(
            profile_dict,
            self.settings.MIN_PROFILE_COMPLETENESS_FOR_COMPLETION,
        )

        if completeness != employee_profile.profile_completeness_score:
            await self.storage_service.update_employee_profile(
                employee_profile.id,
                EmployeeProfileUpdate(profile_completeness_score=completeness),
            )

        # 8. Blob upload (best-effort)
        blob_url = None
        try:
            if self.settings.has_azure_blob_credentials():
                blob_url = await self.blob_service.upload_document(
                    file_bytes=file_bytes,
                    document_id=str(document_id),
                    filename=filename,
                    content_type=content_type,
                    metadata={
                        "conversation_id": str(conversation_id),
                        "employee_id": employee_profile.employee_id or "",
                        "upload_source": "conversation",
                    },
                )
        except Exception as e:
            logger.warning(f"Blob upload failed (non-fatal): {e}")
            warnings.append("Document could not be uploaded to blob storage")

        # 9. Save to employee_documents table
        try:
            await self._save_document_record(
                document_id=document_id,
                employee_id=employee_profile.employee_id,
                employee_email=employee_profile.employee_email,
                conversation_id=conversation_id,
                profile_id=employee_profile.id,
                filename=filename,
                content_type=content_type,
                file_size_bytes=len(file_bytes),
                blob_url=blob_url,
                blob_path=f"documents/{document_id}/{filename}" if blob_url else None,
                upload_source=DocumentSource.CONVERSATION.value,
                extraction_status="completed",
                extracted_fields=fields_extracted,
                extracted_data=extracted_data.model_dump(exclude_none=True),
                raw_text_length=len(document_text),
            )
        except Exception as e:
            logger.warning(f"Failed to save document record (non-fatal): {e}")
            warnings.append("Document metadata could not be saved to database")

        # 10. Save system message noting the upload
        try:
            system_msg = ConversationMessageCreate(
                conversation_id=conversation_id,
                role=MessageRole.SYSTEM,
                content=(
                    f"[Document uploaded: {filename}] "
                    f"Extracted {len(fields_extracted)} fields. "
                    f"Merged {len(merged_fields)} fields into profile. "
                    f"Skipped {len(skipped_fields)} fields (already filled)."
                ),
                message_type=MessageType.SYSTEM,
            )
            await self.storage_service.save_message(system_msg)
        except Exception as e:
            logger.warning(f"Failed to save system message (non-fatal): {e}")

        return ConversationDocumentUploadResponse(
            document_id=document_id,
            filename=filename,
            blob_url=blob_url,
            extracted_data=extracted_data,
            extraction_summary=summary,
            fields_extracted=fields_extracted,
            fields_merged=merged_fields,
            fields_skipped=skipped_fields,
            profile_completeness=completeness,
            missing_fields=missing_fields,
            can_complete=can_complete,
            warnings=warnings,
        )

    async def _save_document_record(
        self,
        document_id: UUID,
        employee_id: Optional[str],
        employee_email: Optional[str],
        conversation_id: Optional[UUID],
        profile_id: Optional[UUID],
        filename: str,
        content_type: str,
        file_size_bytes: int,
        blob_url: Optional[str],
        blob_path: Optional[str],
        upload_source: str,
        extraction_status: str,
        extracted_fields: Any,
        extracted_data: Any,
        raw_text_length: int,
    ) -> None:
        """Save a document record to the employee_documents table."""
        try:
            pool = await get_db_pool()

            now = datetime.utcnow()

            query = f"""
                INSERT INTO {DOCUMENTS_TABLE} (
                    id, employee_id, employee_email, conversation_id, profile_id,
                    filename, content_type, file_size_bytes, blob_url, blob_path,
                    upload_source, extraction_status, extracted_fields, extracted_data,
                    raw_text_length, uploaded_at, processed_at
                ) VALUES (
                    $1, $2, $3, $4, $5,
                    $6, $7, $8, $9, $10,
                    $11, $12, $13, $14,
                    $15, $16, $17
                )
            """

            async with pool.acquire() as conn:
                await conn.execute(
                    query,
                    document_id,
                    employee_id,
                    employee_email,
                    conversation_id,
                    profile_id,
                    filename,
                    content_type,
                    file_size_bytes,
                    blob_url,
                    blob_path,
                    upload_source,
                    extraction_status,
                    extracted_fields,
                    extracted_data,
                    raw_text_length,
                    now,
                    now,
                )

            logger.info(f"Saved document record: {document_id}")

        except Exception as e:
            logger.error(f"Failed to save document record: {e}")
            raise StorageError(
                f"Failed to save document record: {str(e)}",
                details={"document_id": str(document_id), "error": str(e)},
            )
