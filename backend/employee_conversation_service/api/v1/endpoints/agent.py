"""Agent endpoints for Employee Service Agent orchestration."""

import logging
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form
from fastapi.responses import Response
from pydantic import BaseModel, Field

from employee_conversation_service.services.employee_service_agent import (
    EmployeeServiceAgent,
)
from employee_conversation_service.core.exceptions import (
    ServiceError,
    DocumentNotFoundError,
    EmployeeProfileNotFoundError,
)

logger = logging.getLogger(__name__)

router = APIRouter()


class ProcessDocumentRequest(BaseModel):
    """Request to process an existing document by ID."""

    document_id: UUID = Field(..., description="ID of the document to process")
    user_query: Optional[str] = Field(
        None, description="Optional instructions for the agent"
    )
    employee_profile_id: Optional[UUID] = Field(
        None, description="Existing employee profile id to update"
    )
    conversation_id: Optional[UUID] = Field(
        None, description="Conversation id to link or resolve profile"
    )


class ClarifyingQuestionRequest(BaseModel):
    """Request to generate clarifying questions for an employee profile."""

    employee_profile_id: UUID = Field(..., description="ID of the employee profile")
    context: Optional[str] = Field(
        None, description="Additional context for question generation"
    )


@router.post(
    "/process-document",
    status_code=status.HTTP_200_OK,
    summary="Process document by ID with agent",
    description="Use the Employee Service Agent to orchestrate extraction from an existing document",
    tags=["agent"],
)
async def process_document_with_agent(request: ProcessDocumentRequest):
    """Process an existing document (by ID) through the Employee Service Agent."""
    try:
        agent = EmployeeServiceAgent()
        result = await agent.process_document_by_id(
            document_id=request.document_id,
            user_query=request.user_query,
            employee_profile_id=request.employee_profile_id,
            conversation_id=request.conversation_id,
        )
        return result
    except DocumentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "details": e.details},
        )
    except ServiceError as e:
        logger.exception("Agent processing failed: %s", e)
        raise HTTPException(
            status_code=e.status_code, detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to process document", "message": str(e)},
        )


@router.post(
    "/process-upload",
    status_code=status.HTTP_200_OK,
    summary="Process uploaded document with agent",
    description="Upload a document (e.g. resume) and run the Employee Service Agent to extract profile",
    tags=["agent"],
)
async def process_upload_with_agent(
    file: UploadFile = File(..., description="Document file (e.g. PDF resume)"),
    employee_profile_id: Optional[UUID] = Form(
        None, description="Existing employee profile id to update"
    ),
    conversation_id: Optional[UUID] = Form(
        None, description="Conversation id to link or resolve profile"
    ),
):
    """Upload a document and process it through the Employee Service Agent."""
    try:
        content = await file.read()
        agent = EmployeeServiceAgent()
        result = await agent.process_uploaded_document(
            file_content=content,
            file_name=file.filename,
            mime_type=file.content_type,
            employee_profile_id=employee_profile_id,
            conversation_id=conversation_id,
        )
        return result
    except ServiceError as e:
        logger.exception("Agent processing failed: %s", e)
        raise HTTPException(
            status_code=e.status_code, detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to process upload", "message": str(e)},
        )


@router.post(
    "/clarifying-questions",
    status_code=status.HTTP_200_OK,
    summary="Generate clarifying questions",
    description="Ask the agent to generate clarifying questions for an incomplete employee profile",
    tags=["agent"],
)
async def generate_clarifying_questions(request: ClarifyingQuestionRequest):
    """Generate clarifying questions for an employee profile."""
    try:
        agent = EmployeeServiceAgent()
        questions = await agent.ask_clarifying_question(
            employee_profile_id=request.employee_profile_id,
            context=request.context,
        )
        return {
            "employee_profile_id": str(request.employee_profile_id),
            "questions": questions,
        }
    except EmployeeProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "details": e.details},
        )
    except ServiceError as e:
        logger.exception("Question generation failed: %s", e)
        raise HTTPException(
            status_code=e.status_code, detail={"error": e.message, "details": e.details}
        )
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to generate questions", "message": str(e)},
        )


@router.get(
    "/generate-resume/{employee_profile_id}",
    status_code=status.HTTP_200_OK,
    summary="Generate resume PDF from profile",
    description="Generate a formatted PDF resume from an extracted employee profile (template + PDF generation)",
    tags=["agent"],
)
async def generate_resume(employee_profile_id: UUID):
    """Generate and download a PDF resume from the given employee profile."""
    try:
        agent = EmployeeServiceAgent()
        pdf_bytes, filename = await agent.generate_resume(employee_profile_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )
    except EmployeeProfileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message, "details": e.details},
        )
    except ServiceError as e:
        logger.exception("Resume generation failed: %s", e)
        raise HTTPException(
            status_code=e.status_code,
            detail={"error": e.message, "details": e.details},
        )
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to generate resume", "message": str(e)},
        )
