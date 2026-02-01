"""
Service for extracting and analyzing client needs from conversations and documents.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from decimal import Decimal

from client_need_service.core.exceptions import ConversationError, ServiceError
from client_need_service.models.schemas import ClientNeedUpdate
from client_need_service.services.azure_openai_service import AzureOpenAIService

logger = logging.getLogger(__name__)


class NeedExtractionService:
    """Service for extracting structured information from conversations and documents."""

    def __init__(self):
        """Initialize need extraction service."""
        self.azure_openai_service = AzureOpenAIService()

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

    async def extract_needs_from_text(
        self,
        text: str,
        client_name: Optional[str] = None,
        client_email: Optional[str] = None
    ) -> Tuple[ClientNeedUpdate, Dict[str, Any]]:
        """
        Extract structured client needs from raw text using AI.

        This is the main extraction method for standalone document/text processing.

        Args:
            text: Raw text content to extract from
            client_name: Optional client name
            client_email: Optional client email

        Returns:
            Tuple of (ClientNeedUpdate with extracted data, metadata with confidence scores)

        Raises:
            ServiceError: If extraction fails
        """
        try:
            logger.info(f"Extracting needs from text ({len(text)} chars)")

            # Create extraction prompt
            extraction_prompt = self._build_extraction_prompt(text)

            # Call Azure OpenAI for structured extraction
            messages = [
                {"role": "system", "content": self._get_extraction_system_prompt()},
                {"role": "user", "content": extraction_prompt}
            ]

            response_dict = await self.azure_openai_service.generate_response(
                messages,
                use_functions=False
            )
            response = response_dict.get("content", "")

            # Parse the response
            extracted_data = self._parse_extraction_response(response)

            # Add client info if provided
            if client_name:
                extracted_data["client_name"] = client_name
            if client_email:
                extracted_data["client_email"] = client_email

            # Calculate confidence and completeness
            completeness_score = self.calculate_completeness_score(extracted_data)
            missing_fields = self.identify_missing_fields(extracted_data)

            metadata = {
                "completeness_score": completeness_score,
                "missing_fields": missing_fields,
                "extraction_method": "ai_text_extraction",
                "confidence": Decimal("0.85")  # Can be enhanced with actual confidence scoring
            }

            logger.info(f"Extracted needs with {completeness_score}% completeness")

            return ClientNeedUpdate(**extracted_data), metadata

        except Exception as e:
            logger.error(f"Failed to extract needs from text: {e}")
            raise ServiceError(
                f"Need extraction failed: {str(e)}",
                details={"error": str(e)}
            )

    def _get_extraction_system_prompt(self) -> str:
        """Get the system prompt for need extraction."""
        return """You are an expert at extracting client project requirements from text.

Your task is to analyze the provided text and extract structured information about:
- Project details (title, description, type, industry)
- Required skills and experience level
- Budget information (min, max, currency, type)
- Timeline (duration, start date, flexibility)
- Urgency and priority
- Work arrangement (location, hours)
- Required roles/disciplines (identify and normalize)
- Additional requirements

**Role Extraction Instructions:**
Identify any roles or disciplines mentioned or implied in the text. For each role:
1. Extract the original wording/evidence from the client brief
2. Normalize to one of these canonical categories:
   - strategy_consulting: strategy, business analysis, domain experts, change management
   - product_management: PMs, product owners, product leads
   - technology_engineering: architects, engineers, developers, DevOps, cloud, AI/ML
   - design_ux: UX/UI designers, researchers, accessibility, service design
   - creative_content: copywriters, content strategists, brand/marketing
   - project_program_management: project managers, scrum masters, agile coaches
   - quality_testing: QA, testers, automation, UAT
   - data_analytics: data scientists, analysts, BI, visualization

3. Include count if mentioned (e.g., "3 developers" → count: 3)

Return your analysis as a JSON object with the following structure:
{
  "project_title": "string or null",
  "project_description": "string or null",
  "project_type": "string or null",
  "industry": "string or null",
  "required_skills": ["skill1", "skill2"] or null,
  "preferred_skills": ["skill1", "skill2"] or null,
  "skill_level": "junior|mid|senior|expert or null",
  "budget_min": number or null,
  "budget_max": number or null,
  "budget_currency": "string or null",
  "budget_type": "hourly|fixed|monthly or null",
  "timeline_duration_weeks": number or null,
  "timeline_start_date": "YYYY-MM-DD or null",
  "timeline_flexibility": "flexible|somewhat_flexible|strict or null",
  "urgency_level": "low|medium|high|critical or null",
  "priority_score": number (1-10) or null,
  "work_location": "remote|onsite|hybrid or null",
  "team_size_needed": number or null,
  "collaboration_tools": ["tool1", "tool2"] or null,
  "required_roles": [
    {
      "category": "technology_engineering",
      "evidence": "cloud engineering support",
      "description": "optional additional details",
      "count": 2
    }
  ] or null
}

Only include fields where you can confidently extract information. Use null for missing data.
Be precise with numbers and dates. Infer reasonable values when context is clear.
For roles: extract explicit mentions AND infer from responsibilities described."""

    def _build_extraction_prompt(self, text: str) -> str:
        """Build the extraction prompt from text."""
        return f"""Analyze the following client communication and extract all relevant project requirements:

---
{text}
---

Extract and structure all available information about the project requirements.
Return only the JSON object, no additional text."""

    def _parse_extraction_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI extraction response into structured data."""
        try:
            # Try to parse as JSON
            # The response might have markdown code blocks, so clean it
            cleaned_response = response.strip()

            # Remove markdown code blocks if present
            if cleaned_response.startswith("```"):
                lines = cleaned_response.split("\n")
                cleaned_response = "\n".join(lines[1:-1])  # Remove first and last lines

            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]  # Remove ```

            cleaned_response = cleaned_response.strip()

            extracted = json.loads(cleaned_response)

            # Normalize enum values before validation
            extracted = self._normalize_enum_values(extracted)

            # Filter out null values
            return {k: v for k, v in extracted.items() if v is not None}

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse extraction response as JSON: {e}")
            logger.debug(f"Response was: {response}")
            # Return empty dict if parsing fails
            return {}

    def _normalize_enum_values(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize AI-generated enum values to match schema enums."""
        # Skill level normalization
        skill_level_mapping = {
            "experienced": "senior",
            "intermediate": "mid",
            "beginner": "junior",
            "advanced": "expert",
            "entry": "junior",
            "entry-level": "junior",
            "mid-level": "mid",
            "senior-level": "senior",
        }

        if "skill_level" in data and isinstance(data["skill_level"], str):
            normalized = skill_level_mapping.get(data["skill_level"].lower())
            if normalized:
                data["skill_level"] = normalized

        # Timeline flexibility normalization
        flexibility_mapping = {
            "very flexible": "flexible",
            "not flexible": "strict",
            "somewhat flexible": "somewhat_flexible",
        }

        if "timeline_flexibility" in data and isinstance(data["timeline_flexibility"], str):
            normalized = flexibility_mapping.get(data["timeline_flexibility"].lower())
            if normalized:
                data["timeline_flexibility"] = normalized

        # Work location normalization
        location_mapping = {
            "fully remote": "remote",
            "fully onsite": "onsite",
            "on-site": "onsite",
            "mixed": "hybrid",
        }

        if "work_location" in data and isinstance(data["work_location"], str):
            normalized = location_mapping.get(data["work_location"].lower())
            if normalized:
                data["work_location"] = normalized

        # Role category normalization
        if "required_roles" in data and isinstance(data["required_roles"], list):
            data["required_roles"] = self._normalize_roles(data["required_roles"])

        return data

    def _normalize_roles(self, roles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize role categories and validate structure."""
        role_category_mapping = {
            # Strategy & Consulting
            "strategy": "strategy_consulting",
            "business analyst": "strategy_consulting",
            "business analysis": "strategy_consulting",
            "domain expert": "strategy_consulting",
            "change management": "strategy_consulting",
            "transformation": "strategy_consulting",

            # Product Management
            "product manager": "product_management",
            "product owner": "product_management",
            "pm": "product_management",
            "apm": "product_management",
            "product lead": "product_management",
            "feature owner": "product_management",

            # Technology & Engineering
            "architect": "technology_engineering",
            "engineer": "technology_engineering",
            "developer": "technology_engineering",
            "engineering": "technology_engineering",
            "backend": "technology_engineering",
            "frontend": "technology_engineering",
            "full-stack": "technology_engineering",
            "fullstack": "technology_engineering",
            "devops": "technology_engineering",
            "sre": "technology_engineering",
            "cloud": "technology_engineering",
            "ai": "technology_engineering",
            "ml": "technology_engineering",
            "machine learning": "technology_engineering",
            "data engineer": "technology_engineering",

            # Design & UX
            "designer": "design_ux",
            "ux": "design_ux",
            "ui": "design_ux",
            "interaction design": "design_ux",
            "service design": "design_ux",
            "researcher": "design_ux",
            "user research": "design_ux",
            "accessibility": "design_ux",

            # Creative & Content
            "copywriter": "creative_content",
            "content": "creative_content",
            "brand": "creative_content",
            "marketing": "creative_content",
            "creative": "creative_content",

            # Project & Program Management
            "project manager": "project_program_management",
            "program manager": "project_program_management",
            "scrum master": "project_program_management",
            "agile coach": "project_program_management",
            "delivery": "project_program_management",
            "pmo": "project_program_management",

            # Quality & Testing
            "qa": "quality_testing",
            "tester": "quality_testing",
            "quality": "quality_testing",
            "testing": "quality_testing",
            "automation": "quality_testing",
            "uat": "quality_testing",

            # Data & Analytics
            "data scientist": "data_analytics",
            "data analyst": "data_analytics",
            "analytics": "data_analytics",
            "bi": "data_analytics",
            "business intelligence": "data_analytics",
            "insights": "data_analytics",
            "reporting": "data_analytics",
        }

        normalized_roles = []

        for role in roles:
            if not isinstance(role, dict):
                continue

            # Normalize category if it's a string that needs mapping
            category = role.get("category", "")
            if isinstance(category, str):
                category_lower = category.lower().replace("_", " ")

                # Try exact match first
                if category_lower in role_category_mapping:
                    role["category"] = role_category_mapping[category_lower]
                # Try partial match
                else:
                    for keyword, normalized_category in role_category_mapping.items():
                        if keyword in category_lower:
                            role["category"] = normalized_category
                            break

            # Validate that we have required fields
            if "category" in role and "evidence" in role:
                normalized_roles.append(role)

        return normalized_roles
