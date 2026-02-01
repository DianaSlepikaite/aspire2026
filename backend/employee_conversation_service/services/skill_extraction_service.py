"""
Skill extraction service.
Extracts skills, levels, certifications (and similar) for the employee profile.
"""

import json
import logging
from typing import List, Dict, Any, Optional

from employee_conversation_service.core.exceptions import ServiceError
from employee_conversation_service.services.azure_openai_service import AzureOpenAIService

logger = logging.getLogger(__name__)


EXTRACTION_PROMPT = """Extract employee profile information from the following conversation messages.

Return a JSON object with these fields (only include fields if information is found):
{{
  "full_name": "string",
  "email": "string",
  "phone": "string",
  "summary": "brief professional summary",
  "experience_years": number,
  "skills": ["skill1", "skill2", ...],
  "certifications": ["cert1", "cert2", ...],
  "education": [{{"degree": "string", "school": "string", "year": "string"}}],
  "experience": [{{"title": "string", "company": "string", "years": "string", "description": "string"}}],
  "preferred_roles": ["role1", "role2", ...]
}}

Conversation:
{conversation_text}

Extract all mentioned information. Be thorough and include all skills, technologies, and certifications mentioned."""


class SkillExtractionService:
    """Extract skills, certifications, levels from text or profile."""

    def __init__(self):
        self.openai_service = AzureOpenAIService()

    async def extract_from_conversation(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Extract profile information from conversation messages.
        Returns dict with profile fields.
        """
        if not messages:
            return {}

        # Build conversation text
        conversation_text = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in messages
        ])

        prompt = EXTRACTION_PROMPT.format(conversation_text=conversation_text)

        try:
            response = await self.openai_service.generate_response(
                messages=[{"role": "user", "content": prompt}],
                use_functions=False
            )

            content = response.get("content", "")

            # Try to parse JSON from the response
            # OpenAI might wrap it in markdown code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()

            extracted = json.loads(content)
            logger.info(f"Extracted profile data: {list(extracted.keys())}")
            return extracted

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extraction JSON: {e}")
            logger.error(f"Content: {content}")
            return {}
        except Exception as e:
            logger.exception(f"Extraction failed: {e}")
            return {}

    async def extract_skills_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract skills and related fields from raw text (e.g. resume).
        Returns dict with keys like skills, certifications, skill_levels.
        """
        if not text or not text.strip():
            return {"skills": [], "certifications": [], "skill_levels": {}}

        # Use conversation extraction with text as a single message
        messages = [{"role": "user", "content": text}]
        extracted = await self.extract_from_conversation(messages)

        return {
            "skills": extracted.get("skills", []),
            "certifications": extracted.get("certifications", []),
            "skill_levels": {}
        }

    def merge_skills_into_profile(
        self, profile_data: Dict[str, Any], extracted: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge extracted skills/certs into profile dict (for agent use)."""
        out = dict(profile_data)
        if extracted.get("skills"):
            out["skills"] = list(
                set(out.get("skills") or []) | set(extracted["skills"])
            )
        if extracted.get("certifications"):
            out["certifications"] = list(
                set(out.get("certifications") or []) | set(extracted["certifications"])
            )
        return out

    def calculate_completeness(self, profile_data: Dict[str, Any]) -> int:
        """Calculate profile completeness score (0-100)."""
        total_fields = 10
        filled_fields = 0

        # Check each major field
        if profile_data.get("full_name"):
            filled_fields += 1
        if profile_data.get("email"):
            filled_fields += 1
        if profile_data.get("phone"):
            filled_fields += 1
        if profile_data.get("summary"):
            filled_fields += 1
        if profile_data.get("experience_years"):
            filled_fields += 1
        if profile_data.get("skills") and len(profile_data["skills"]) > 0:
            filled_fields += 1
        if profile_data.get("certifications") and len(profile_data["certifications"]) > 0:
            filled_fields += 1
        if profile_data.get("education") and len(profile_data["education"]) > 0:
            filled_fields += 1
        if profile_data.get("experience") and len(profile_data["experience"]) > 0:
            filled_fields += 1
        if profile_data.get("preferred_roles") and len(profile_data["preferred_roles"]) > 0:
            filled_fields += 1

        return int((filled_fields / total_fields) * 100)
