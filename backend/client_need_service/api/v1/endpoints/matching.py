"""
Matching endpoints for employee-to-client need matching.
"""

import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from client_need_service.models.schemas import (
    MatchRequest,
    MatchResponse
)
from client_need_service.services.matching_agent import MatchingAgent
from client_need_service.core.exceptions import (
    ClientNeedNotFoundError,
    ServiceError
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/find-candidates",
    response_model=MatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Find matching candidates",
    description="""
    Use AI to find and rank employee candidates that match a client need.

    Returns a ranked list of candidates with:
    - Match scores (0-100)
    - Detailed explanations of why each candidate matches
    - Skill gap analysis
    - Transparent recommendations for staffing decisions

    This endpoint enables leadership visibility into candidate matching
    with AI-powered, explainable recommendations.
    """
)
async def find_matching_candidates(request: MatchRequest):
    """
    Find matching candidates for a client need using AI.

    This endpoint:
    1. Retrieves client need requirements
    2. Evaluates all employee profiles
    3. Uses AI to match and rank candidates
    4. Provides transparent, explainable recommendations

    Perfect for:
    - Staffing decisions
    - Candidate shortlisting
    - Skills gap analysis
    - Leadership visibility
    """
    try:
        matching_agent = MatchingAgent()
        response = await matching_agent.find_matches(request)
        return response

    except ClientNeedNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": e.message,
                "details": e.details
            }
        )
    except ServiceError as e:
        logger.error(f"Matching service error: {e}")
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "error": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        logger.exception(f"Unexpected error in matching: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to find matching candidates"}
        )


@router.get(
    "/candidate/{employee_profile_id}/for-need/{client_need_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Evaluate single candidate",
    description="Evaluate how well a specific candidate matches a specific client need"
)
async def evaluate_single_candidate(
    employee_profile_id: UUID,
    client_need_id: UUID
):
    """
    Evaluate a single candidate against a client need.

    Returns detailed match analysis for one specific candidate,
    useful for deep-dive evaluations or second-round screening.
    """
    try:
        matching_agent = MatchingAgent()

        # Create a request for just this one candidate
        request = MatchRequest(
            client_need_id=client_need_id,
            max_results=1,
            min_match_score=0
        )

        # Get matches (will filter to this employee in the agent)
        response = await matching_agent.find_matches(request)

        # Find the specific candidate in results
        candidate_match = next(
            (m for m in response.matches if m.employee_profile_id == employee_profile_id),
            None
        )

        if candidate_match:
            return {
                "match": candidate_match.model_dump(),
                "evaluated_at": response.generated_at,
                "ai_model": response.ai_model
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "Candidate not found or does not meet minimum criteria"}
            )

    except HTTPException:
        raise
    except ClientNeedNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": e.message}
        )
    except Exception as e:
        logger.exception(f"Failed to evaluate candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Failed to evaluate candidate"}
        )
