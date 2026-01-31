"""
Service for extracting and analyzing client needs from conversations.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID

from client_need_service.core.exceptions import ConversationError
from client_need_service.models.schemas import ClientNeedUpdate

logger = logging.getLogger(__name__)


class NeedExtractionService:
    """Service for extracting structured information from conversations."""

    # Required fields for a complete profile
    REQUIRED_FIELDS = [
        "project_description",
        "required_skills",
        "budget_min",
        "timeline_duration_weeks",
        "urgency_level"
    ]

    # Field weights for completeness calculation
    FIELD_WEIGHTS = {
        "project_title": 5,
        "project_description": 10,
        "project_type": 5,
        "required_skills": 15,
        "skill_level": 5,
        "budget_min": 10,
        "budget_max": 5,
        "timeline_duration_weeks": 10,
        "timeline_start_date": 5,
        "urgency_level": 10,
        "work_location": 5,
        "client_name": 5,
        "client_email": 5,
        "timeline_flexibility": 3,
        "priority_score": 3,
        "team_size_needed": 2,
        "collaboration_tools": 2
    }

    async def extract_needs_from_function_calls(
        self,
        function_calls: List[Dict[str, Any]]
    ) -> ClientNeedUpdate:
        """
        Extract needs from OpenAI function calls.

        Args:
            function_calls: List of function call dictionaries

        Returns:
            ClientNeedUpdate with extracted data

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
                if function_name == "update_project_details":
                    extracted_data.update(self._extract_project_details(arguments))

                elif function_name == "update_skill_requirements":
                    extracted_data.update(self._extract_skill_requirements(arguments))

                elif function_name == "update_budget_information":
                    extracted_data.update(self._extract_budget_info(arguments))

                elif function_name == "update_timeline_details":
                    extracted_data.update(self._extract_timeline_details(arguments))

                elif function_name == "update_urgency_and_priority":
                    extracted_data.update(self._extract_urgency(arguments))

                elif function_name == "update_work_arrangement":
                    extracted_data.update(self._extract_work_arrangement(arguments))

                elif function_name == "update_additional_requirements":
                    extracted_data.update(self._extract_additional_requirements(arguments))

                elif function_name == "update_client_information":
                    extracted_data.update(self._extract_client_info(arguments))

            logger.info(f"Extracted {len(extracted_data)} fields from function calls")

            return ClientNeedUpdate(**extracted_data)

        except Exception as e:
            logger.error(f"Failed to extract needs from function calls: {e}")
            raise ConversationError(
                f"Failed to extract needs: {str(e)}",
                details={"error": str(e)}
            )

    def _extract_project_details(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract project details from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["project_title", "project_description", "project_type", "industry", "key_challenges"]
        }

    def _extract_skill_requirements(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract skill requirements from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["required_skills", "preferred_skills", "skill_level", "certifications_required"]
        }

    def _extract_budget_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract budget information from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["budget_min", "budget_max", "budget_currency", "budget_type"]
        }

    def _extract_timeline_details(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract timeline details from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in [
                "timeline_start_date",
                "timeline_end_date",
                "timeline_duration_weeks",
                "timeline_flexibility",
                "start_date_importance"
            ]
        }

    def _extract_urgency(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract urgency and priority from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["urgency_level", "priority_score"]
        }

    def _extract_work_arrangement(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract work arrangement from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["work_location", "work_location_details", "work_hours_requirement"]
        }

    def _extract_additional_requirements(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional requirements from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["team_size_needed", "collaboration_tools", "communication_preferences"]
        }

    def _extract_client_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract client information from function arguments."""
        return {
            key: value
            for key, value in args.items()
            if key in ["client_name", "client_email", "client_phone", "client_company"]
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
            "project_description": "project details and objectives",
            "required_skills": "required skills and expertise",
            "budget_min": "budget expectations",
            "budget_max": "budget range",
            "timeline_duration_weeks": "project timeline",
            "urgency_level": "urgency and priority",
            "work_location": "work arrangement preferences",
            "skill_level": "desired experience level",
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
