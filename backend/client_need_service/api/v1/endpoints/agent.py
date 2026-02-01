"""
Agent endpoints for orchestrated client need processing.
Uses the Client Need Agent to coordinate ingestion and extraction.
"""

import logging
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from client_need_service.services.client_need_agent import ClientNeedAgent
from client_need_service.core.exceptions import ServiceError

logger = logging.getLogger(__name__)

router = APIRouter()


class ProcessIntakeRequest(BaseModel):
    """Request to process an intake package."""
    intake_id: UUID = Field(..., description="ID of the intake package to process")
    user_query: Optional[str] = Field(None, description="Optional custom instructions for the agent")


class AgentResponse(BaseModel):
    """Response from the agent."""
    output: str = Field(..., description="Agent's response and findings")
    intermediate_steps: list = Field(default_factory=list, description="Steps the agent took")


class ClarifyingQuestionRequest(BaseModel):
    """Request to generate clarifying questions."""
    client_need_id: UUID = Field(..., description="ID of the client need profile")
    context: Optional[str] = Field(None, description="Additional context for question generation")


@router.post(
    "/process-intake",
    response_model=AgentResponse,
    status_code=status.HTTP_200_OK,
    summary="Process intake package with agent",
    description="Use the Client Need Agent to orchestrate extraction from an intake package"
)
async def process_intake_with_agent(request: ProcessIntakeRequest):
    """
    Process an intake package using the Client Need Agent.

    The agent will:
    1. Retrieve and analyze the intake package
    2. Extract structured client needs
    3. Identify missing information
    4. Provide a summary and suggest clarifying questions

    This is the main orchestration endpoint that combines all services.
    """
    try:
        logger.info(f"Processing intake {request.intake_id} with agent")

        agent = ClientNeedAgent()

        result = await agent.process_intake_package(
            intake_id=request.intake_id,
            user_query=request.user_query
        )

        return AgentResponse(**result)

    except ServiceError as e:
        logger.error(f"Agent processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error in agent processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to process with agent", "message": str(e)}
        )


@router.post(
    "/clarifying-questions",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Generate clarifying questions",
    description="Ask the agent to generate clarifying questions for incomplete client needs"
)
async def generate_clarifying_questions(request: ClarifyingQuestionRequest):
    """
    Generate intelligent clarifying questions for a client need profile.

    The agent will analyze the profile and suggest questions to ask the client
    to fill in missing information.
    """
    try:
        logger.info(f"Generating clarifying questions for client need {request.client_need_id}")

        agent = ClientNeedAgent()

        questions = await agent.ask_clarifying_question(
            client_need_id=request.client_need_id,
            context=request.context
        )

        return {
            "client_need_id": str(request.client_need_id),
            "questions": questions
        }

    except ServiceError as e:
        logger.error(f"Question generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.error(f"Unexpected error generating questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to generate questions", "message": str(e)}
        )
