"""
Client Need Agent - Orchestrator for client need extraction.

This agent coordinates between Data Ingestion and Need Extraction services,
reasons about the process, and asks clarifying questions when needed.
"""

import logging
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone

from client_need_service.config import get_settings
from client_need_service.services.data_ingestion_service import DataIngestionService
from client_need_service.services.need_extraction_service import NeedExtractionService
from client_need_service.services.storage_service import StorageService
from client_need_service.services.azure_openai_service import AzureOpenAIService
from client_need_service.models.schemas import ClientIntakePackageUpdate, ClientNeedCreate, ClientNeedUpdate
from client_need_service.core.exceptions import ServiceError

logger = logging.getLogger(__name__)


class ClientNeedAgent:
    """
    Orchestrator for client need extraction.

    Responsibilities:
    - Orchestrate data ingestion and extraction workflows
    - Reason about what information is available and what's missing
    - Ask clarifying questions to the user
    - Explain extraction results
    """

    def __init__(self):
        """Initialize the Client Need Agent."""
        self.settings = get_settings()
        self.ingestion_service = DataIngestionService()
        self.extraction_service = NeedExtractionService()
        self.storage_service = StorageService()
        self.azure_openai_service = AzureOpenAIService()

    async def process_intake_package(
        self,
        intake_id: UUID,
        user_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an intake package through the agent workflow.

        Args:
            intake_id: ID of the intake package to process
            user_query: Optional user query/instruction

        Returns:
            Dictionary with agent response and extracted needs

        Raises:
            ServiceError: If processing fails
        """
        try:
            logger.info(f"Processing intake package: {intake_id}")

            steps = []

            # Step 1: Retrieve the intake package
            logger.info("Step 1: Retrieving intake package")
            package = await self.storage_service.get_intake_package(intake_id)

            if not package:
                raise ServiceError(f"Intake package {intake_id} not found")

            steps.append({
                "step": "retrieve_intake",
                "action": "Retrieved intake package",
                "details": {
                    "source_type": package.source_type,
                    "word_count": package.normalized_content.word_count if package.normalized_content else None
                }
            })

            # Step 2: Extract structured client needs
            logger.info("Step 2: Extracting client needs")
            text = package.normalized_content.text if package.normalized_content else package.raw_content

            if not text:
                raise ServiceError("No text content available for extraction")

            extracted_needs, metadata = await self.extraction_service.extract_needs_from_text(
                text=text,
                client_name=package.client_name,
                client_email=package.client_email
            )

            steps.append({
                "step": "extract_needs",
                "action": "Extracted structured client needs",
                "details": {
                    "completeness_score": metadata["completeness_score"],
                    "fields_extracted": len(extracted_needs.model_dump(exclude_none=True))
                }
            })

            # Step 3: Create client need in database
            logger.info("Step 3: Saving client need to database")
            client_need_data = extracted_needs.model_dump(exclude_none=True)

            # Add conversation metadata
            client_need_data.update({
                "conversation_id": uuid4(),
                "source_channel": "intake_package"
            })

            # Create ClientNeedCreate object
            client_need_create = ClientNeedCreate(**client_need_data)
            client_need = await self.storage_service.create_client_need(client_need_create)

            # Update with all extracted fields
            client_need = await self.storage_service.update_client_need(
                client_need.id,
                extracted_needs
            )

            # Update completeness score
            await self.storage_service.update_client_need(
                client_need.id,
                ClientNeedUpdate(profile_completeness_score=metadata["completeness_score"])
            )

            # Link intake package to client need
            await self.storage_service.update_intake_package(
                intake_id,
                ClientIntakePackageUpdate(client_need_id=client_need.id)
            )

            steps.append({
                "step": "save_client_need",
                "action": "Created client need profile",
                "details": {
                    "client_need_id": str(client_need.id),
                    "completeness_score": metadata["completeness_score"]
                }
            })

            # Step 4: Analyze missing information
            logger.info("Step 4: Analyzing missing information")
            profile_dict = client_need.model_dump()
            missing_fields = self.extraction_service.identify_missing_fields(profile_dict)
            critical_missing = self.extraction_service.identify_critical_missing_fields(profile_dict)

            steps.append({
                "step": "analyze_completeness",
                "action": "Analyzed profile completeness",
                "details": {
                    "missing_fields_count": len(missing_fields),
                    "critical_missing_count": len(critical_missing)
                }
            })

            # Step 5: Generate summary and recommendations
            logger.info("Step 5: Generating summary")
            summary = await self._generate_summary(
                client_need=client_need,
                completeness_score=metadata["completeness_score"],
                missing_fields=missing_fields[:10],  # Top 10
                critical_missing=critical_missing
            )

            # Persist summary + missing info for frontend display
            await self.storage_service.update_client_need(
                client_need.id,
                ClientNeedUpdate(
                    needs_summary=summary,
                    missing_information=missing_fields[:10]
                )
            )

            logger.info("Agent processing completed successfully")

            return {
                "output": summary,
                "intermediate_steps": steps,
                "client_need_id": str(client_need.id),
                "completeness_score": metadata["completeness_score"],
                "missing_fields": missing_fields[:10],
                "critical_missing_fields": critical_missing
            }

        except Exception as e:
            logger.error(f"Agent processing failed: {e}")
            raise ServiceError(
                f"Failed to process intake package: {str(e)}",
                details={"error": str(e)}
            )

    async def _generate_summary(
        self,
        client_need,
        completeness_score: int,
        missing_fields: List[str],
        critical_missing: List[str]
    ) -> str:
        """Generate a summary of the extraction results using AI."""

        prompt = f"""As an expert client needs analyst, please provide a clear, professional summary of the client requirements extraction.

**Extracted Information:**
- Client: {client_need.client_name or 'Not specified'}
- Email: {client_need.client_email or 'Not specified'}
- Project: {client_need.project_title or 'Not specified'}
- Description: {client_need.project_description[:200] if client_need.project_description else 'Not specified'}...
- Required Skills: {', '.join(client_need.required_skills) if client_need.required_skills else 'Not specified'}
- Budget: {'$' + str(client_need.budget_min) + ' - $' + str(client_need.budget_max) + ' ' + client_need.budget_currency if client_need.budget_min else 'Not specified'}
- Timeline: {str(client_need.timeline_duration_weeks) + ' weeks' if client_need.timeline_duration_weeks else 'Not specified'}
- Urgency: {client_need.urgency_level or 'Not specified'}
- Work Location: {client_need.work_location or 'Not specified'}

**Profile Completeness:** {completeness_score}%

**Missing Information:** {', '.join(missing_fields[:5]) if missing_fields else 'None - profile is complete!'}

**Critical Missing Fields:** {', '.join(critical_missing) if critical_missing else 'None'}

Please provide:
1. A brief summary of what we learned about the client's needs
2. Assessment of profile completeness
3. If there are missing fields, suggest 2-3 specific clarifying questions to ask the client

Be concise, professional, and helpful."""

        try:
            messages = [{"role": "user", "content": prompt}]
            response_dict = await self.azure_openai_service.generate_response(
                messages,
                use_functions=False
            )
            return response_dict.get("content", "")
        except Exception as e:
            logger.warning(f"Failed to generate AI summary: {e}")
            # Fallback to simple summary
            return f"""## Extraction Complete

**Profile Completeness:** {completeness_score}%

**Extracted Information:**
- Client: {client_need.client_name or 'Not specified'}
- Project: {client_need.project_title or 'Not specified'}
- Budget: {'$' + str(client_need.budget_min) + ' - $' + str(client_need.budget_max) if client_need.budget_min else 'Not specified'}
- Timeline: {str(client_need.timeline_duration_weeks) + ' weeks' if client_need.timeline_duration_weeks else 'Not specified'}

**Missing Information:** {', '.join(missing_fields[:5]) if missing_fields else 'Profile is complete!'}
"""

    async def ask_clarifying_question(
        self,
        client_need_id: UUID,
        context: Optional[str] = None
    ) -> str:
        """
        Generate clarifying questions based on missing information.

        Args:
            client_need_id: ID of the client need profile
            context: Optional additional context

        Returns:
            Clarifying question(s) to ask the client

        Raises:
            ServiceError: If generation fails
        """
        try:
            client_need = await self.storage_service.get_client_need(client_need_id)
            if not client_need:
                raise ServiceError(f"Client need {client_need_id} not found")

            # Get missing fields
            profile_dict = client_need.model_dump()
            missing_fields = self.extraction_service.identify_missing_fields(profile_dict)
            critical_missing = self.extraction_service.identify_critical_missing_fields(profile_dict)

            if not missing_fields:
                return "The client need profile appears to be complete! No additional information is needed."

            # Generate question using AI
            prompt = f"""Based on the following client need profile, generate 2-3 thoughtful clarifying questions to ask the client.

**Current Profile:**
- Project: {client_need.project_title or 'Not specified'}
- Description: {client_need.project_description[:200] if client_need.project_description else 'Not specified'}
- Completeness: {client_need.profile_completeness_score}%

**Missing Information:**
Critical: {', '.join(critical_missing) if critical_missing else 'None'}
Other: {', '.join(missing_fields[:10]) if missing_fields else 'None'}

{context if context else ''}

Generate specific, actionable questions that will help complete the profile. Focus on the most critical missing information first."""

            messages = [{"role": "user", "content": prompt}]
            response_dict = await self.azure_openai_service.generate_response(
                messages,
                use_functions=False
            )

            return response_dict.get("content", "")

        except Exception as e:
            logger.error(f"Failed to generate clarifying questions: {e}")
            raise ServiceError(
                f"Failed to generate questions: {str(e)}",
                details={"error": str(e)}
            )
