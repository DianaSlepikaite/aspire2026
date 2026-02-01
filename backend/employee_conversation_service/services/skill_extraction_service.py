"""
Service for extracting and analyzing employee skills, experience, and career goals from conversations.
Tailored for Publicis Sapient internal staffing context.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID

from employee_conversation_service.core.exceptions import ConversationError
from employee_conversation_service.models.schemas import EmployeeProfileUpdate

logger = logging.getLogger(__name__)


class SkillExtractionService:
    """Service for extracting structured information from employee conversations."""

    # Required fields for a complete profile
    REQUIRED_FIELDS = [
        "technical_skills",
        "career_track",
        "experience_level",
        "bench_status",
        "career_goals"
    ]

    # Field weights for completeness calculation
    FIELD_WEIGHTS = {
        "technical_skills": 15,
        "career_track": 8,
        "experience_level": 8,
        "bench_status": 8,
        "career_goals": 10,
        "years_total_experience": 5,
        "years_at_ps": 3,
        "current_assignment": 8,
        "availability_date": 5,
        "domain_expertise": 5,
        "project_history": 8,
        "soft_skills": 3,
        "methodologies": 3,
        "tools_platforms": 3,
        "training_certifications": 3,
        "professional_summary": 3,
        "employee_name": 3,
        "location": 3,
        "notable_achievements": 2,
        "areas_for_growth": 2,
        "strengths": 2,
    }

    async def extract_from_function_calls(
        self,
        function_calls: List[Dict[str, Any]]
    ) -> EmployeeProfileUpdate:
        """
        Extract employee profile data from OpenAI function calls.

        Args:
            function_calls: List of function call dictionaries

        Returns:
            EmployeeProfileUpdate with extracted data

        Raises:
            ConversationError: If extraction fails
        """
        try:
            extracted_data = {}

            for func_call in function_calls:
                function_name = func_call["name"]
                arguments_str = func_call["arguments"]

                # Parse arguments
                try:
                    arguments = json.loads(arguments_str)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse function arguments: {e}")
                    continue

                # Map function calls to extracted data
                if function_name == "update_basic_info":
                    extracted_data.update(self._extract_basic_info(arguments))

                elif function_name == "update_career_info":
                    extracted_data.update(self._extract_career_info(arguments))

                elif function_name == "update_assignment_status":
                    extracted_data.update(self._extract_assignment_status(arguments))

                elif function_name == "update_skills":
                    extracted_data.update(self._extract_skills(arguments))

                elif function_name == "update_project_history":
                    extracted_data.update(self._extract_project_history(arguments))

                elif function_name == "update_learning_development":
                    extracted_data.update(self._extract_learning(arguments))

                elif function_name == "update_career_goals":
                    extracted_data.update(self._extract_career_goals(arguments))

            logger.info(f"Extracted {len(extracted_data)} fields from function calls")

            return EmployeeProfileUpdate(**extracted_data)

        except Exception as e:
            logger.error(f"Failed to extract data from function calls: {e}")
            raise ConversationError(
                f"Failed to extract profile data: {str(e)}",
                details={"error": str(e)}
            )

    def _extract_basic_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic information from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["employee_id", "employee_name", "employee_email", "location"]
        }

    def _extract_career_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract PS career information from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in [
                "career_track", "experience_level", "years_at_ps",
                "years_total_experience", "professional_summary"
            ]
        }

    def _extract_assignment_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract assignment status from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["bench_status", "current_assignment", "availability_date"]
        }

    def _extract_skills(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract skills from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in [
                "technical_skills", "soft_skills", "domain_expertise",
                "methodologies", "tools_platforms"
            ]
        }

    def _extract_project_history(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract project history from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["project_history", "notable_achievements", "strengths"]
        }

    def _extract_learning(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract learning and development from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["training_certifications", "current_learning", "areas_for_growth"]
        }

    def _extract_career_goals(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract career goals from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["career_goals"]
        }

    def calculate_completeness_score(
        self,
        profile: Dict[str, Any]
    ) -> int:
        """
        Calculate profile completeness score (0-100).

        Args:
            profile: Profile data dictionary

        Returns:
            Completeness score from 0 to 100
        """
        total_weight = sum(self.FIELD_WEIGHTS.values())
        achieved_weight = 0

        for field, weight in self.FIELD_WEIGHTS.items():
            value = profile.get(field)

            # Check if field has a meaningful value
            if value is not None:
                if isinstance(value, (list, dict)):
                    if len(value) > 0:
                        achieved_weight += weight
                elif isinstance(value, str):
                    if value.strip():
                        achieved_weight += weight
                else:
                    achieved_weight += weight

        score = int((achieved_weight / total_weight) * 100)

        logger.debug(f"Calculated completeness score: {score}")

        return score

    def identify_missing_fields(
        self,
        profile: Dict[str, Any]
    ) -> List[str]:
        """
        Identify missing required and important fields.

        Args:
            profile: Profile data dictionary

        Returns:
            List of missing field names
        """
        missing = []

        for field, weight in sorted(
            self.FIELD_WEIGHTS.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            value = profile.get(field)

            # Check if field is missing or empty
            if value is None:
                missing.append(field)
            elif isinstance(value, (list, dict)) and len(value) == 0:
                missing.append(field)
            elif isinstance(value, str) and not value.strip():
                missing.append(field)

        logger.debug(f"Identified {len(missing)} missing fields")

        return missing

    def identify_critical_missing_fields(
        self,
        profile: Dict[str, Any]
    ) -> List[str]:
        """
        Identify critical missing fields from REQUIRED_FIELDS.

        Args:
            profile: Profile data dictionary

        Returns:
            List of missing critical field names
        """
        missing = []

        for field in self.REQUIRED_FIELDS:
            value = profile.get(field)

            if value is None:
                missing.append(field)
            elif isinstance(value, (list, dict)) and len(value) == 0:
                missing.append(field)
            elif isinstance(value, str) and not value.strip():
                missing.append(field)

        return missing

    def can_complete_conversation(
        self,
        profile: Dict[str, Any],
        min_completeness: int = 70
    ) -> bool:
        """
        Determine if conversation has enough information to complete.

        Args:
            profile: Profile data dictionary
            min_completeness: Minimum completeness score required

        Returns:
            True if conversation can be completed
        """
        # Check completeness score
        completeness = self.calculate_completeness_score(profile)

        if completeness < min_completeness:
            logger.debug(
                f"Completeness {completeness} below minimum {min_completeness}"
            )
            return False

        # Check critical fields
        critical_missing = self.identify_critical_missing_fields(profile)

        if critical_missing:
            logger.debug(f"Critical fields missing: {critical_missing}")
            return False

        return True

    def generate_follow_up_question_hint(
        self,
        missing_fields: List[str]
    ) -> Optional[str]:
        """
        Generate a hint for follow-up questions based on missing fields.

        Args:
            missing_fields: List of missing field names

        Returns:
            Hint string or None if no critical fields missing
        """
        if not missing_fields:
            return None

        # Prioritize most important missing fields
        priority_fields = [
            field for field in missing_fields
            if field in self.REQUIRED_FIELDS
        ]

        if not priority_fields:
            priority_fields = missing_fields[:3]  # Take top 3 by weight

        field_hints = {
            "technical_skills": "technical skills and proficiency levels",
            "career_track": "career track or discipline",
            "experience_level": "PS level or grade",
            "bench_status": "current assignment status and availability",
            "career_goals": "career goals and aspirations",
            "years_total_experience": "years of professional experience",
            "current_assignment": "current project details",
            "availability_date": "availability date for new projects",
            "domain_expertise": "industry domain expertise",
            "project_history": "past PS project experience",
        }

        hints = [
            field_hints.get(field, field.replace("_", " "))
            for field in priority_fields
        ]

        if len(hints) == 1:
            return f"We're still missing information about {hints[0]}."
        elif len(hints) == 2:
            return f"We're still missing information about {hints[0]} and {hints[1]}."
        else:
            return f"We're still missing information about {', '.join(hints[:-1])}, and {hints[-1]}."
