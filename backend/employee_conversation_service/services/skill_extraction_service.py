"""
Skill extraction service.
Extracts skills, levels, certifications (and similar) for the employee profile.
"""

import logging
from typing import List, Dict, Any, Optional

from employee_conversation_service.core.exceptions import ServiceError

logger = logging.getLogger(__name__)


class SkillExtractionService:
    """Extract skills, certifications, levels from text or profile."""

    async def extract_skills_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract skills and related fields from raw text (e.g. resume).
        Returns dict with keys like skills, certifications, skill_levels.
        """
        if not text or not text.strip():
            return {"skills": [], "certifications": [], "skill_levels": {}}
        # Stub: real impl would use Azure OpenAI or NER to extract skills
        logger.info("Skill extraction stub: returned empty skills")
        return {"skills": [], "certifications": [], "skill_levels": {}}

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
