"""
Service for extracting structured profile data from document text using GPT-4,
and merging document-extracted data into existing profiles.
"""

import json
import logging
from typing import Dict, Any, List, Tuple, Optional

from employee_conversation_service.config import get_settings
from employee_conversation_service.core.exceptions import AzureOpenAIError
from employee_conversation_service.models.schemas import EmployeeProfileUpdate
from employee_conversation_service.prompts.document_prompts import (
    DOCUMENT_EXTRACTION_PROMPT,
    DOCUMENT_EXTRACTION_FUNCTIONS,
)
from employee_conversation_service.services.skill_extraction_service import (
    SkillExtractionService,
)

logger = logging.getLogger(__name__)

# Fields that are scalar (single value) — document fills only if empty
SCALAR_FIELDS = {
    "employee_name",
    "employee_id",
    "employee_email",
    "career_track",
    "experience_level",
    "years_at_ps",
    "years_total_experience",
    "bench_status",
    "availability_date",
    "professional_summary",
    "notes",
}

# Fields that are lists — append new items, deduplicate
LIST_FIELDS = {
    "technical_skills",
    "soft_skills",
    "domain_expertise",
    "methodologies",
    "tools_platforms",
    "project_history",
    "notable_achievements",
    "training_certifications",
    "current_learning",
    "strengths",
    "areas_for_growth",
}

# Fields that are dicts — document fills only if empty
DICT_FIELDS = {
    "location",
    "current_assignment",
    "career_goals",
}


class DocumentExtractionService:
    """Service for GPT-4 extraction from document text and profile merging."""

    def __init__(self):
        self.settings = get_settings()
        self._client = None
        self._skill_extraction = SkillExtractionService()
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Azure OpenAI client."""
        if not self.settings.has_azure_openai_credentials():
            logger.warning("Azure OpenAI not configured for document extraction")
            return

        try:
            from openai import AsyncAzureOpenAI

            self._client = AsyncAzureOpenAI(
                api_key=self.settings.AZURE_OPENAI_KEY,
                api_version=self.settings.AZURE_OPENAI_API_VERSION,
                azure_endpoint=self.settings.AZURE_OPENAI_ENDPOINT,
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client for extraction: {e}")

    def _ensure_client(self):
        """Ensure the OpenAI client is available."""
        if self._client is None:
            raise AzureOpenAIError(
                "Azure OpenAI not configured for document extraction. "
                "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY."
            )

    async def extract_profile_from_text(
        self,
        document_text: str,
        filename: str,
    ) -> Tuple[EmployeeProfileUpdate, str, List[str]]:
        """
        Send document text to GPT-4 for structured profile extraction.

        Args:
            document_text: Extracted text from the document.
            filename: Original filename for context.

        Returns:
            Tuple of (EmployeeProfileUpdate, summary_string, list_of_extracted_fields)

        Raises:
            AzureOpenAIError: If the GPT-4 call fails.
        """
        self._ensure_client()

        prompt = DOCUMENT_EXTRACTION_PROMPT.format(
            filename=filename,
            document_text=document_text,
        )

        try:
            response = await self._client.chat.completions.create(
                model=self.settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": (
                            "Please analyse the document above and extract all "
                            "structured profile information using the provided functions."
                        ),
                    },
                ],
                tools=DOCUMENT_EXTRACTION_FUNCTIONS,
                tool_choice="auto",
                temperature=0.2,
                max_tokens=self.settings.AZURE_OPENAI_MAX_TOKENS,
            )

            choice = response.choices[0]
            message = choice.message

            # Parse function calls into profile data
            function_calls = []
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.type == "function":
                        function_calls.append(
                            {
                                "id": tool_call.id,
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            }
                        )

            if not function_calls:
                logger.warning("GPT-4 returned no function calls for document extraction")
                return (
                    EmployeeProfileUpdate(),
                    "No structured data could be extracted from the document.",
                    [],
                )

            # Use SkillExtractionService to parse function calls
            profile_update = await self._skill_extraction.extract_from_function_calls(
                function_calls
            )

            # Determine which fields were extracted
            extracted_dict = profile_update.model_dump(exclude_none=True)
            fields_extracted = list(extracted_dict.keys())

            # Build summary
            summary = self._build_extraction_summary(extracted_dict)

            logger.info(
                f"Extracted {len(fields_extracted)} fields from document: {filename}"
            )

            return profile_update, summary, fields_extracted

        except AzureOpenAIError:
            raise
        except Exception as e:
            logger.error(f"Document extraction failed: {e}")
            raise AzureOpenAIError(
                f"Failed to extract profile from document: {str(e)}",
                details={"filename": filename, "error": str(e)},
            )

    def merge_document_into_profile(
        self,
        existing_profile_dict: Dict[str, Any],
        document_data: EmployeeProfileUpdate,
    ) -> Tuple[EmployeeProfileUpdate, List[str], List[str]]:
        """
        Merge document-extracted data into an existing profile.

        Strategy:
        - Scalar fields: document fills only if existing is empty/None
        - List fields: append new items, deduplicate by name key
        - Dict fields: document fills only if existing is empty/None
        - Conversation-extracted data always wins on conflicts

        Args:
            existing_profile_dict: Current profile data (dict with exclude_none).
            document_data: Extracted data from the document.

        Returns:
            Tuple of (merged EmployeeProfileUpdate, merged_fields, skipped_fields)
        """
        doc_dict = document_data.model_dump(exclude_none=True)
        merged = {}
        merged_fields = []
        skipped_fields = []

        for field, doc_value in doc_dict.items():
            existing_value = existing_profile_dict.get(field)

            if field in SCALAR_FIELDS:
                if self._is_empty(existing_value):
                    merged[field] = doc_value
                    merged_fields.append(field)
                else:
                    skipped_fields.append(field)

            elif field in LIST_FIELDS:
                if self._is_empty(existing_value):
                    merged[field] = doc_value
                    merged_fields.append(field)
                elif isinstance(doc_value, list) and isinstance(existing_value, list):
                    combined = self._merge_lists(existing_value, doc_value, field)
                    if len(combined) > len(existing_value):
                        merged[field] = combined
                        merged_fields.append(field)
                    else:
                        skipped_fields.append(field)
                else:
                    skipped_fields.append(field)

            elif field in DICT_FIELDS:
                if self._is_empty(existing_value):
                    merged[field] = doc_value
                    merged_fields.append(field)
                else:
                    skipped_fields.append(field)

            else:
                # Unknown field category — treat as scalar
                if self._is_empty(existing_value):
                    merged[field] = doc_value
                    merged_fields.append(field)
                else:
                    skipped_fields.append(field)

        logger.info(
            f"Merge result: {len(merged_fields)} merged, {len(skipped_fields)} skipped"
        )

        return EmployeeProfileUpdate(**merged), merged_fields, skipped_fields

    def _is_empty(self, value: Any) -> bool:
        """Check if a value is considered empty/missing."""
        if value is None:
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        return False

    def _merge_lists(
        self,
        existing: List[Any],
        new_items: List[Any],
        field_name: str,
    ) -> List[Any]:
        """
        Merge two lists, deduplicating by a name key where applicable.

        For technical_skills: deduplicate by skill_name
        For training_certifications: deduplicate by name
        For project_history: deduplicate by project_name
        For simple string lists: deduplicate by value
        """
        if not new_items:
            return existing

        # Determine the dedup key based on field
        dedup_keys = {
            "technical_skills": "skill_name",
            "training_certifications": "name",
            "project_history": "project_name",
        }

        dedup_key = dedup_keys.get(field_name)

        if dedup_key and existing and isinstance(existing[0], dict):
            existing_names = {
                item.get(dedup_key, "").lower()
                for item in existing
                if isinstance(item, dict)
            }
            combined = list(existing)
            for item in new_items:
                if isinstance(item, dict):
                    item_name = item.get(dedup_key, "").lower()
                    if item_name and item_name not in existing_names:
                        combined.append(item)
                        existing_names.add(item_name)
            return combined

        # Simple string list dedup
        if existing and isinstance(existing[0], str):
            existing_lower = {s.lower() for s in existing}
            combined = list(existing)
            for item in new_items:
                if isinstance(item, str) and item.lower() not in existing_lower:
                    combined.append(item)
                    existing_lower.add(item.lower())
            return combined

        # Fallback: just concatenate
        return existing + new_items

    def _build_extraction_summary(self, extracted: Dict[str, Any]) -> str:
        """Build a human-readable summary of what was extracted."""
        parts = []

        if extracted.get("employee_name"):
            parts.append(f"Name: {extracted['employee_name']}")
        if extracted.get("career_track"):
            parts.append(f"Career track: {extracted['career_track']}")
        if extracted.get("experience_level"):
            parts.append(f"Level: {extracted['experience_level']}")

        skills = extracted.get("technical_skills")
        if skills and isinstance(skills, list):
            skill_names = []
            for s in skills[:5]:
                if isinstance(s, dict):
                    skill_names.append(s.get("skill_name", ""))
                elif isinstance(s, str):
                    skill_names.append(s)
            if skill_names:
                parts.append(f"Skills: {', '.join(skill_names)}")
                if len(skills) > 5:
                    parts.append(f"  ...and {len(skills) - 5} more")

        certs = extracted.get("training_certifications")
        if certs and isinstance(certs, list):
            parts.append(f"Certifications: {len(certs)} found")

        projects = extracted.get("project_history")
        if projects and isinstance(projects, list):
            parts.append(f"Projects: {len(projects)} found")

        if not parts:
            return "No structured data could be extracted."

        return "Extracted from document:\n" + "\n".join(f"- {p}" for p in parts)
