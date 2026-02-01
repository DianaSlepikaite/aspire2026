"""
Matching Agent - AI-powered employee-to-client need matching service.

This agent uses AI to match employee profiles to client needs, providing
transparent, ranked recommendations for staffing decisions.
"""

import json
import logging
from typing import List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timezone
import asyncpg

from client_need_service.config import get_settings
from client_need_service.services.storage_service import StorageService
from client_need_service.services.azure_openai_service import AzureOpenAIService
from client_need_service.models.schemas import (
    MatchRequest,
    MatchResponse,
    CandidateMatch,
    MatchExplanation,
    SkillMatch
)
from client_need_service.core.exceptions import ServiceError, ClientNeedNotFoundError

logger = logging.getLogger(__name__)


MATCHING_SYSTEM_PROMPT = """You are an expert technical recruiter and talent matching specialist.
Your role is to analyze employee profiles and match them to client project requirements with high accuracy and transparency.

You must:
1. Evaluate technical skills alignment
2. Consider experience level requirements
3. Assess certifications and education
4. Evaluate work arrangement compatibility (remote/onsite)
5. Consider availability and timeline fit
6. Provide transparent, explainable recommendations
7. Highlight both strengths and gaps

Be objective, thorough, and provide actionable insights for hiring decisions."""


class MatchingAgent:
    """
    AI-powered matching agent for employee-to-client need matching.

    Provides transparent, ranked recommendations with detailed explanations
    to enable informed staffing decisions and leadership visibility.
    """

    def __init__(self):
        """Initialize the Matching Agent."""
        self.settings = get_settings()
        self.storage_service = StorageService()
        self.azure_openai_service = AzureOpenAIService()
        self._employee_db_pool = None

    async def _get_employee_db_pool(self) -> asyncpg.Pool:
        """Get connection pool for employee database."""
        if self._employee_db_pool is None:
            # Connect to employee database
            db_name = "employee_conversation_db"
            db_user = self.settings.DB_USER
            db_password = self.settings.DB_PASSWORD
            db_host = self.settings.DB_HOST
            db_port = self.settings.DB_PORT

            self._employee_db_pool = await asyncpg.create_pool(
                database=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                min_size=1,
                max_size=5
            )
        return self._employee_db_pool

    async def find_matches(self, request: MatchRequest) -> MatchResponse:
        """
        Find matching candidates for a client need.

        Args:
            request: Match request with client need ID and filters

        Returns:
            MatchResponse with ranked candidate matches

        Raises:
            ClientNeedNotFoundError: If client need doesn't exist
            ServiceError: If matching fails
        """
        try:
            logger.info(f"Finding matches for client need: {request.client_need_id}")

            # Step 1: Get client need details
            client_need = await self.storage_service.get_client_need(request.client_need_id)
            if not client_need:
                raise ClientNeedNotFoundError(
                    client_need_id=request.client_need_id,
                    message=f"Client need {request.client_need_id} not found"
                )

            # Step 2: Get all employee profiles
            employee_profiles = await self._fetch_employee_profiles(request.filters)
            logger.info(f"Found {len(employee_profiles)} employee profiles to evaluate")

            if not employee_profiles:
                return MatchResponse(
                    client_need_id=request.client_need_id,
                    total_candidates_evaluated=0,
                    matches=[],
                    generated_at=datetime.now(timezone.utc)
                )

            # Step 3: Use AI to match and rank candidates
            matches = await self._match_candidates_with_ai(
                client_need=client_need,
                employee_profiles=employee_profiles,
                max_results=request.max_results,
                min_score=request.min_match_score
            )

            logger.info(f"Generated {len(matches)} matches above threshold")

            return MatchResponse(
                client_need_id=request.client_need_id,
                total_candidates_evaluated=len(employee_profiles),
                matches=matches,
                generated_at=datetime.now(timezone.utc),
                ai_model=self.settings.AZURE_OPENAI_DEPLOYMENT_NAME
            )

        except ClientNeedNotFoundError:
            raise
        except Exception as e:
            logger.exception(f"Matching failed: {e}")
            raise ServiceError(
                f"Failed to find matches: {str(e)}",
                details={"error": str(e)}
            )

    async def _fetch_employee_profiles(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Fetch employee profiles from employee database."""
        try:
            pool = await self._get_employee_db_pool()
            async with pool.acquire() as conn:
                min_score = 0
                if filters and isinstance(filters, dict):
                    try:
                        min_score = int(filters.get("min_profile_score", 0))
                    except (TypeError, ValueError):
                        min_score = 0
                # Build query with optional filters
                query = """
                    SELECT id, full_name, email, phone, summary,
                           experience_years, skills, certifications, education,
                           experience, preferred_roles, profile_completeness_score,
                           created_at, updated_at
                    FROM employee_profiles
                    WHERE profile_completeness_score >= $1
                    ORDER BY profile_completeness_score DESC, updated_at DESC
                """

                rows = await conn.fetch(query, min_score)

                # Convert to dictionaries
                profiles = []
                for row in rows:
                    profile = dict(row)
                    # Parse JSONB fields
                    for field in ['skills', 'certifications', 'education', 'experience', 'preferred_roles']:
                        if profile.get(field):
                            if isinstance(profile[field], str):
                                try:
                                    profile[field] = json.loads(profile[field])
                                except json.JSONDecodeError:
                                    profile[field] = []
                    profiles.append(profile)

                return profiles

        except Exception as e:
            logger.error(f"Failed to fetch employee profiles: {e}")
            return []

    async def _match_candidates_with_ai(
        self,
        client_need,
        employee_profiles: List[Dict[str, Any]],
        max_results: int,
        min_score: int
    ) -> List[CandidateMatch]:
        """Use AI to match and rank candidates."""

        # For large candidate pools, batch process
        if len(employee_profiles) > 20:
            # First pass: Quick filtering using simpler logic
            employee_profiles = self._pre_filter_candidates(client_need, employee_profiles)
            logger.info(f"Pre-filtered to {len(employee_profiles)} candidates")

        match_data_list = []

        for profile in employee_profiles:
            try:
                # Use AI to score and explain the match
                match_result = await self._evaluate_single_match(client_need, profile)

                if match_result and match_result['score'] >= min_score:
                    # Build match data as dictionary first (don't create CandidateMatch yet)
                    match_data = {
                        'employee_profile_id': profile['id'],
                        'employee_name': profile.get('full_name') or 'Unknown',
                        'employee_email': profile.get('email'),
                        'match_score': match_result['score'],
                        'confidence': match_result['confidence'],
                        'explanation': match_result['explanation'],
                        'experience_years': profile.get('experience_years'),
                        'key_skills': profile.get('skills', [])[:10],  # Top 10 skills
                        'current_availability': match_result.get('availability', 'Unknown')
                    }
                    match_data_list.append(match_data)

            except Exception as e:
                logger.warning(f"Failed to evaluate profile {profile.get('id')}: {e}")
                continue

        # Sort by match score descending
        match_data_list.sort(key=lambda x: x['match_score'], reverse=True)

        # Create CandidateMatch objects with correct ranks
        matches = [
            CandidateMatch(**{**match_data, 'rank': idx})
            for idx, match_data in enumerate(match_data_list[:max_results], start=1)
        ]

        return matches

    def _pre_filter_candidates(
        self,
        client_need,
        profiles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Pre-filter candidates using simple heuristics before AI evaluation."""
        required_skills = set(s.lower() for s in (client_need.required_skills or []))

        if not required_skills:
            return profiles[:50]  # Limit to top 50 if no skills specified

        filtered = []
        for profile in profiles:
            candidate_skills = set(s.lower() for s in (profile.get('skills') or []))

            # Must have at least 1 required skill
            if required_skills & candidate_skills:
                filtered.append(profile)

        return filtered[:50] if filtered else profiles[:20]

    async def _evaluate_single_match(
        self,
        client_need,
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate a single candidate match using AI."""

        prompt = self._build_matching_prompt(client_need, profile)

        try:
            messages = [
                {"role": "system", "content": MATCHING_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]

            response = await self.azure_openai_service.generate_response(
                messages,
                use_functions=False
            )

            content = response.get("content", "")

            # Parse AI response
            match_result = self._parse_ai_match_response(content, client_need, profile)
            return match_result

        except Exception as e:
            logger.warning(f"AI evaluation failed for profile {profile.get('id')}: {e}")
            # Fallback to heuristic matching
            return self._heuristic_match(client_need, profile)

    def _build_matching_prompt(self, client_need, profile: Dict[str, Any]) -> str:
        """Build a detailed prompt for AI matching."""

        prompt = f"""Evaluate how well this candidate matches the client's requirements.

**CLIENT REQUIREMENTS:**
- Project: {client_need.project_title or 'Not specified'}
- Description: {client_need.project_description[:300] if client_need.project_description else 'Not specified'}
- Required Skills: {', '.join(client_need.required_skills or [])}
- Skill Level: {client_need.skill_level or 'Not specified'}
- Required Certifications: {', '.join(client_need.certifications_required or []) if client_need.certifications_required else 'None'}
- Timeline: {client_need.timeline_duration_weeks} weeks ({client_need.timeline_start_date or 'Flexible start'})
- Work Location: {client_need.work_location or 'Not specified'}
- Budget: {'$' + str(client_need.budget_min) + '-$' + str(client_need.budget_max) + '/' + (client_need.budget_type or 'hour') if client_need.budget_min else 'Not specified'}
- Urgency: {client_need.urgency_level or 'Medium'}

**CANDIDATE PROFILE:**
- Name: {profile.get('full_name', 'Unknown')}
- Experience: {profile.get('experience_years', 'Not specified')} years
- Summary: {profile.get('summary', 'Not provided')[:200]}
- Skills: {', '.join(profile.get('skills', [])[:20])}
- Certifications: {', '.join(profile.get('certifications', [])) if profile.get('certifications') else 'None'}
- Education: {json.dumps(profile.get('education', [])[:2]) if profile.get('education') else 'Not specified'}
- Preferred Roles: {', '.join(profile.get('preferred_roles', [])) if profile.get('preferred_roles') else 'Not specified'}

Provide your evaluation in JSON format:
{{
  "match_score": <0-100>,
  "confidence": <0.0-1.0>,
  "strengths": ["strength1", "strength2", ...],
  "gaps": ["gap1", "gap2", ...],
  "skill_matches": [
    {{"skill": "skill_name", "required": true, "candidate_has": true}}
  ],
  "availability": "available/unknown",
  "recommendation": "brief summary of why this is a good/poor match"
}}

Be honest and specific. Match score should reflect how well the candidate meets ALL requirements."""

        return prompt

    def _parse_ai_match_response(
        self,
        content: str,
        client_need,
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse AI response into structured match result."""

        # Try to extract JSON from response
        try:
            # Look for JSON in markdown code blocks
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()

            data = json.loads(content)

            # Build SkillMatch objects
            skill_matches = []
            for sm in data.get('skill_matches', []):
                skill_matches.append(SkillMatch(
                    skill=sm.get('skill', ''),
                    required=sm.get('required', False),
                    candidate_has=sm.get('candidate_has', False),
                    proficiency_level=sm.get('proficiency_level')
                ))

            explanation = MatchExplanation(
                strengths=data.get('strengths', []),
                skill_matches=skill_matches,
                gaps=data.get('gaps', []),
                additional_notes=data.get('recommendation', '')
            )

            return {
                'score': int(data.get('match_score', 50)),
                'confidence': float(data.get('confidence', 0.5)),
                'explanation': explanation,
                'availability': data.get('availability', 'Unknown')
            }

        except Exception as e:
            logger.warning(f"Failed to parse AI response: {e}")
            # Fallback to heuristic
            return self._heuristic_match(client_need, profile)

    def _heuristic_match(self, client_need, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback heuristic matching when AI fails."""

        required_skills = set(s.lower() for s in (client_need.required_skills or []))
        candidate_skills = set(s.lower() for s in (profile.get('skills') or []))

        # Calculate basic match score
        if not required_skills:
            skill_match_ratio = 0.5
        else:
            matched_skills = required_skills & candidate_skills
            skill_match_ratio = len(matched_skills) / len(required_skills)

        base_score = int(skill_match_ratio * 70)  # 70% weight on skills

        # Add experience bonus (up to 20 points)
        exp_years = profile.get('experience_years', 0) or 0
        if exp_years >= 8:
            base_score += 20
        elif exp_years >= 5:
            base_score += 15
        elif exp_years >= 3:
            base_score += 10

        # Add completeness bonus (up to 10 points)
        completeness = profile.get('profile_completeness_score', 0) or 0
        base_score += int(completeness / 10)

        score = min(base_score, 100)

        # Build explanation
        matched_skills = list(required_skills & candidate_skills)
        missing_skills = list(required_skills - candidate_skills)

        explanation = MatchExplanation(
            strengths=[f"Has {len(matched_skills)} of {len(required_skills)} required skills"],
            skill_matches=[
                SkillMatch(skill=s, required=True, candidate_has=True)
                for s in matched_skills
            ],
            gaps=[f"Missing skill: {s}" for s in missing_skills[:5]],
            additional_notes="Heuristic match (AI unavailable)"
        )

        return {
            'score': score,
            'confidence': 0.6,
            'explanation': explanation,
            'availability': 'Unknown'
        }
