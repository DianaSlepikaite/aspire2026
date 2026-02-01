"""
Document extraction service.
Extracts structured fields from document text (experience, education, roles, etc.) into employee profile shape.
"""

import logging
from typing import Dict, Any, Tuple, Optional

from employee_conversation_service.models.schemas import EmployeeProfileUpdate
from employee_conversation_service.core.exceptions import ServiceError

logger = logging.getLogger(__name__)


class DocumentExtractionService:
    """Extract structured employee fields from document text."""

    async def extract_from_text(
        self, text: str, file_name: Optional[str] = None
    ) -> Tuple[EmployeeProfileUpdate, Dict[str, Any]]:
        """
        Extract structured profile fields from raw text (e.g. resume text).
        Returns (EmployeeProfileUpdate, metadata with completeness_score, etc.).
        """
        if not text or not text.strip():
            return (
                EmployeeProfileUpdate(profile_completeness_score=0),
                {"completeness_score": 0, "extraction_method": "document"},
            )
        # Stub: real impl would call Azure OpenAI or similar to extract name, experience, education, etc.
        from employee_conversation_service.models.schemas import EmployeeProfileUpdate

        update = EmployeeProfileUpdate(
            summary=text[:500] if len(text) > 500 else text,
            profile_completeness_score=20,
        )
        metadata = {"completeness_score": 20, "extraction_method": "document_stub"}
        logger.info("Document extraction stub: returned minimal profile")
        return update, metadata
