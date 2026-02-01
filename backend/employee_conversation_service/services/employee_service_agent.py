"""
Employee Service Agent - Orchestrator for employee profile extraction.

This agent coordinates between document upload, parsing, extraction, and skill extraction
services, reasons about completeness, and asks clarifying questions when needed.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timezone

from employee_conversation_service.services.storage_service import StorageService
from employee_conversation_service.services.document_upload_service import (
    DocumentUploadService,
)
from employee_conversation_service.services.document_parsing_service import (
    DocumentParsingService,
)
from employee_conversation_service.services.skill_extraction_service import (
    SkillExtractionService,
)
from employee_conversation_service.services.azure_openai_service import (
    AzureOpenAIService,
)
from employee_conversation_service.services.blob_storage_service import (
    BlobStorageService,
)
from employee_conversation_service.services.conversation_service import (
    ConversationService,
)
from employee_conversation_service.services.speech_service import SpeechService
from employee_conversation_service.services.resume_generation_service import (
    generate_resume_pdf,
)
from employee_conversation_service.models.schemas import (
    EmployeeProfileCreate,
    EmployeeProfileUpdate,
)
from employee_conversation_service.core.exceptions import (
    ServiceError,
    DocumentNotFoundError,
    EmployeeProfileNotFoundError,
)

logger = logging.getLogger(__name__)


class EmployeeServiceAgent:
    """
    Orchestrator for employee profile extraction.

    Invokes:
    - StorageService: get document/profile, create/update profile, link document
    - DocumentUploadService: receive uploaded document
    - DocumentParsingService: parse document to raw text
    - SkillExtractionService: extract structured fields, skills, certifications
    - AzureOpenAIService: summary, clarifying questions
    - BlobStorageService (optional): store/retrieve document binary
    - ConversationService (optional): merge conversation transcript
    - SpeechService (optional): transcribe/synthesize for voice
    """

    def __init__(self) -> None:
        """Initialize the Employee Service Agent and all services it invokes."""
        self.storage_service = StorageService()
        self.document_upload_service = DocumentUploadService()
        self.document_parsing_service = DocumentParsingService()
        self.skill_extraction_service = SkillExtractionService()
        self.azure_openai_service = AzureOpenAIService()
        self.blob_storage_service = BlobStorageService()
        self.conversation_service = ConversationService()
        self.speech_service = SpeechService()

    async def process_uploaded_document(
        self,
        file_content: bytes,
        file_name: Optional[str] = None,
        mime_type: Optional[str] = None,
        user_query: Optional[str] = None,
        employee_profile_id: Optional[UUID] = None,
        conversation_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Process an uploaded document (e.g. resume) through the agent workflow.

        1. DocumentUploadService: create document record (optionally BlobStorageService)
        2. DocumentParsingService: parse to raw text
        3. SkillExtractionService: extract structured profile fields
        4. SkillExtractionService: extract skills/certifications
        5. StorageService: create/update employee profile, link document
        6. AzureOpenAIService: generate summary and suggest clarifying questions
        """
        try:
            logger.info("Processing uploaded document: %s", file_name)
            steps: List[Dict[str, Any]] = []

            # Step 1: Upload document (DocumentUploadService; optionally BlobStorageService)
            logger.info("Step 1: Uploading document")
            doc = await self.document_upload_service.upload_document(
                file_content=file_content,
                file_name=file_name,
                mime_type=mime_type,
            )
            steps.append(
                {
                    "step": "upload_document",
                    "action": "Created document record",
                    "details": {"document_id": str(doc.id), "file_name": file_name},
                }
            )

            # Step 2: Parse document to text (DocumentParsingService)
            logger.info("Step 2: Parsing document")
            raw_text = await self.document_parsing_service.parse_document(doc.id)
            if not raw_text and file_content:
                raw_text = await self.document_parsing_service.parse_content(
                    file_content, mime_type
                )
            if raw_text:
                await self.storage_service.update_document_raw_text(doc.id, raw_text)
            steps.append(
                {
                    "step": "parse_document",
                    "action": "Parsed document to text",
                    "details": {"word_count": len(raw_text.split()) if raw_text else 0},
                }
            )

            # Step 3: Extract structured profile (SkillExtractionService)
            logger.info("Step 3: Extracting profile from document")
            extracted_data: Dict[str, Any] = {}
            extract_meta = {
                "completeness_score": 0,
                "extraction_method": "document_unavailable",
            }
            if (raw_text or "").strip():
                extracted_data = await self.skill_extraction_service.extract_from_conversation(
                    [{"role": "user", "content": raw_text or ""}]
                )
                if not extracted_data:
                    extracted_data = {
                        "summary": raw_text[:500] if len(raw_text) > 500 else raw_text
                    }
                extract_meta = {
                    "completeness_score": self.skill_extraction_service.calculate_completeness(
                        extracted_data
                    ),
                    "extraction_method": "document_openai",
                }
            steps.append(
                {
                    "step": "extract_profile",
                    "action": "Extracted structured profile",
                    "details": {
                        "completeness_score": extract_meta.get("completeness_score", 0),
                    },
                }
            )

            # Step 4: Extract skills (SkillExtractionService)
            logger.info("Step 4: Extracting skills")
            skills_data = await self.skill_extraction_service.extract_skills_from_text(
                raw_text or ""
            )
            profile_data = self.skill_extraction_service.merge_skills_into_profile(
                extracted_data, skills_data
            )
            steps.append(
                {
                    "step": "extract_skills",
                    "action": "Extracted skills and certifications",
                    "details": {
                        "skills_count": len(profile_data.get("skills") or []),
                    },
                }
            )

            # Step 5: Create or update employee profile (StorageService)
            logger.info("Step 5: Saving employee profile")
            existing_profile_id = employee_profile_id
            if not existing_profile_id and conversation_id:
                convo = await self.storage_service.get_employee_conversation_by_conversation_id(
                    conversation_id
                )
                if convo and convo.get("employee_profile_id"):
                    existing_profile_id = convo["employee_profile_id"]

            profile = None
            if existing_profile_id:
                profile = await self.storage_service.get_employee_profile(
                    existing_profile_id
                )

            if not profile:
                score = extract_meta.get("completeness_score", 0)
                create_data = EmployeeProfileCreate(
                    document_id=doc.id,
                    profile_completeness_score=score,
                    full_name=profile_data.get("full_name"),
                    email=profile_data.get("email"),
                    phone=profile_data.get("phone"),
                    summary=profile_data.get("summary"),
                    experience_years=profile_data.get("experience_years"),
                    skills=profile_data.get("skills"),
                    certifications=profile_data.get("certifications"),
                    education=profile_data.get("education"),
                    experience=profile_data.get("experience"),
                    preferred_roles=profile_data.get("preferred_roles"),
                )
                profile = await self.storage_service.create_employee_profile(create_data)
                if conversation_id:
                    await self.storage_service.update_employee_conversation_status(
                        conversation_id=conversation_id,
                        status="in_progress",
                        employee_profile_id=profile.id,
                    )
            else:
                merged_profile = self._merge_profile_data(profile, profile_data)
                merged_profile["profile_completeness_score"] = (
                    self.skill_extraction_service.calculate_completeness(merged_profile)
                )
                update_data = self._build_profile_update_payload(merged_profile)
                await self.storage_service.update_employee_profile(
                    profile.id, EmployeeProfileUpdate(**update_data)
                )
                profile = await self.storage_service.get_employee_profile(profile.id)

            await self.storage_service.link_document_to_profile(doc.id, profile.id)
            steps.append(
                {
                    "step": "save_profile",
                    "action": "Saved employee profile",
                    "details": {"employee_profile_id": str(profile.id)},
                }
            )

            # Step 6: Generate summary (AzureOpenAIService)
            logger.info("Step 6: Generating summary")
            summary = await self._generate_summary(
                profile=profile,
                completeness_score=profile.profile_completeness_score or 0,
                missing_fields=[],
            )
            logger.info("Employee Service Agent processing completed successfully")

            return {
                "output": summary,
                "intermediate_steps": steps,
                "employee_profile_id": str(profile.id),
                "document_id": str(doc.id),
                "completeness_score": profile.profile_completeness_score or 0,
            }
        except (DocumentNotFoundError, EmployeeProfileNotFoundError):
            raise
        except Exception as e:
            logger.exception("Employee Service Agent processing failed: %s", e)
            raise ServiceError(
                f"Failed to process document: {str(e)}",
                details={"error": str(e)},
            )

    async def process_document_by_id(
        self,
        document_id: UUID,
        user_query: Optional[str] = None,
        employee_profile_id: Optional[UUID] = None,
        conversation_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Process an existing document (by ID) through extraction and create/update profile.
        Use when document was already uploaded; agent retrieves, parses, extracts, saves profile.
        """
        doc = await self.storage_service.get_document(document_id)
        if not doc:
            raise DocumentNotFoundError(str(document_id))
        # If document has raw_text, use it; else parse
        raw_text = doc.raw_text
        if not raw_text:
            raw_text = await self.document_parsing_service.parse_document(document_id)
        extracted_data: Dict[str, Any] = {}
        if (raw_text or "").strip():
            extracted_data = await self.skill_extraction_service.extract_from_conversation(
                [{"role": "user", "content": raw_text or ""}]
            )
            if not extracted_data:
                extracted_data = {
                    "summary": raw_text[:500] if len(raw_text) > 500 else raw_text
                }
        skills_data = await self.skill_extraction_service.extract_skills_from_text(
            raw_text or ""
        )
        profile_data = self.skill_extraction_service.merge_skills_into_profile(
            extracted_data, skills_data
        )

        existing_profile_id = employee_profile_id
        if not existing_profile_id and conversation_id:
            convo = await self.storage_service.get_employee_conversation_by_conversation_id(
                conversation_id
            )
            if convo and convo.get("employee_profile_id"):
                existing_profile_id = convo["employee_profile_id"]

        profile = None
        if existing_profile_id:
            profile = await self.storage_service.get_employee_profile(
                existing_profile_id
            )

        if not profile:
            score = self.skill_extraction_service.calculate_completeness(profile_data)
            create_data = EmployeeProfileCreate(
                document_id=document_id,
                profile_completeness_score=score,
                full_name=profile_data.get("full_name"),
                email=profile_data.get("email"),
                phone=profile_data.get("phone"),
                summary=profile_data.get("summary"),
                experience_years=profile_data.get("experience_years"),
                skills=profile_data.get("skills"),
                certifications=profile_data.get("certifications"),
                education=profile_data.get("education"),
                experience=profile_data.get("experience"),
                preferred_roles=profile_data.get("preferred_roles"),
            )
            profile = await self.storage_service.create_employee_profile(create_data)
            if conversation_id:
                await self.storage_service.update_employee_conversation_status(
                    conversation_id=conversation_id,
                    status="in_progress",
                    employee_profile_id=profile.id,
                )
        else:
            merged_profile = self._merge_profile_data(profile, profile_data)
            merged_profile["profile_completeness_score"] = (
                self.skill_extraction_service.calculate_completeness(merged_profile)
            )
            update_data = self._build_profile_update_payload(merged_profile)
            await self.storage_service.update_employee_profile(
                profile.id, EmployeeProfileUpdate(**update_data)
            )
            profile = await self.storage_service.get_employee_profile(profile.id)

        await self.storage_service.link_document_to_profile(document_id, profile.id)
        summary = await self._generate_summary(
            profile=profile,
            completeness_score=profile.profile_completeness_score or 0,
            missing_fields=[],
        )
        return {
            "output": summary,
            "intermediate_steps": [
                {
                    "step": "retrieve_document",
                    "action": "Retrieved document",
                    "details": {},
                },
                {
                    "step": "extract_profile",
                    "action": "Extracted profile",
                    "details": {},
                },
                {
                    "step": "save_profile",
                    "action": "Created employee profile",
                    "details": {},
                },
            ],
            "employee_profile_id": str(profile.id),
            "document_id": str(document_id),
            "completeness_score": profile.profile_completeness_score or 0,
        }

    def _merge_profile_data(self, profile: Any, new_data: Dict[str, Any]) -> Dict[str, Any]:
        base = {
            "full_name": getattr(profile, "full_name", None),
            "email": getattr(profile, "email", None),
            "phone": getattr(profile, "phone", None),
            "summary": getattr(profile, "summary", None),
            "experience_years": getattr(profile, "experience_years", None),
            "skills": getattr(profile, "skills", None),
            "certifications": getattr(profile, "certifications", None),
            "education": getattr(profile, "education", None),
            "experience": getattr(profile, "experience", None),
            "preferred_roles": getattr(profile, "preferred_roles", None),
        }

        merged = dict(base)
        for key, value in (new_data or {}).items():
            if value is None or value == "":
                continue
            if key in ("skills", "certifications", "preferred_roles"):
                existing = merged.get(key) or []
                merged[key] = list({*existing, *value})
            elif key in ("education", "experience"):
                existing = merged.get(key) or []
                if isinstance(value, list):
                    merged[key] = existing + value
                else:
                    merged[key] = existing
            else:
                merged[key] = value
        return merged

    def _build_profile_update_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        for key, value in data.items():
            if value is None:
                continue
            if key in (
                "skills",
                "certifications",
                "preferred_roles",
                "education",
                "experience",
            ):
                if isinstance(value, list) and len(value) == 0:
                    continue
            payload[key] = value
        return payload

    async def _generate_summary(
        self,
        profile: Any,  # EmployeeProfile
        completeness_score: int,
        missing_fields: List[str],
    ) -> str:
        """Generate a summary of the extracted employee profile using Azure OpenAI."""
        prompt = f"""As an expert HR analyst, provide a clear summary of the employee profile extraction.

**Extracted Information:**
- Name: {getattr(profile, "full_name", None) or "Not specified"}
- Email: {getattr(profile, "email", None) or "Not specified"}
- Summary: {(getattr(profile, "summary", None) or "")[:200]}...
- Skills: {", ".join(getattr(profile, "skills", None) or [])}
- Certifications: {", ".join(getattr(profile, "certifications", None) or [])}
- Profile Completeness: {completeness_score}%

**Missing Information:** {", ".join(missing_fields[:5]) if missing_fields else "None"}

Provide:
1. A brief summary of the employee profile
2. Assessment of completeness
3. If missing fields, suggest 2–3 clarifying questions to ask the employee

Be concise and professional."""

        try:
            messages = [{"role": "user", "content": prompt}]
            response_dict = await self.azure_openai_service.generate_response(
                messages, use_functions=False
            )
            return response_dict.get("content", "")
        except Exception as e:
            logger.warning("Failed to generate AI summary: %s", e)
            return f"## Extraction Complete\n\nProfile completeness: {completeness_score}%.\nExtracted: name, skills, certifications. Missing: {', '.join(missing_fields[:5]) if missing_fields else 'None'}."

    async def ask_clarifying_question(
        self, employee_profile_id: UUID, context: Optional[str] = None
    ) -> str:
        """
        Generate clarifying questions based on missing information in the employee profile.
        Uses StorageService to get profile, then AzureOpenAIService to generate questions.
        """
        profile = await self.storage_service.get_employee_profile(employee_profile_id)
        if not profile:
            raise EmployeeProfileNotFoundError(str(employee_profile_id))
        prompt = f"""Based on this employee profile, generate 2–3 clarifying questions to complete the profile.

**Profile:**
- Name: {profile.full_name or "Not specified"}
- Email: {profile.email or "Not specified"}
- Summary: {(profile.summary or "")[:200]}...
- Skills: {", ".join(profile.skills or [])}
- Completeness: {profile.profile_completeness_score}%

{context or ""}

Generate specific questions to fill gaps (e.g. experience, certifications, preferences)."""

        messages = [{"role": "user", "content": prompt}]
        response_dict = await self.azure_openai_service.generate_response(
            messages, use_functions=False
        )
        return response_dict.get("content", "")

    async def generate_resume(self, employee_profile_id: UUID) -> Tuple[bytes, str]:
        """
        Generate a PDF resume from an extracted employee profile.

        Fetches the profile from storage and builds a formatted PDF using
        the resume generation service (template + reportlab).

        Returns:
            (pdf_bytes, suggested_filename) e.g. (b'...', 'Resume_John_Doe.pdf')
        """
        profile = await self.storage_service.get_employee_profile(employee_profile_id)
        if not profile:
            raise EmployeeProfileNotFoundError(str(employee_profile_id))
        pdf_bytes = generate_resume_pdf(profile)
        name = (profile.full_name or "resume").strip().replace(" ", "_")
        safe_name = "".join(c for c in name if c.isalnum() or c in "._-")[:80]
        filename = f"Resume_{safe_name}.pdf" if safe_name else "resume.pdf"
        return (pdf_bytes, filename)
