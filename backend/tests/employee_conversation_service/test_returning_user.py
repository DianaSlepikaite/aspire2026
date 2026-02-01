"""
Tests for returning user / user memory support feature.

Covers:
- New Pydantic models and backwards compatibility
- StorageService new query methods
- Prompt template changes
- AzureOpenAIService new greeting generators
- ConversationService dispatcher logic, carry-forward, resume, abandon, lookup
- API endpoints (lookup, resume)
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID

from employee_conversation_service.models.schemas import (
    ConversationStartRequest,
    ConversationStartResponse,
    ConversationSummaryItem,
    EmployeeLookupResponse,
    EmployeeProfile,
    EmployeeProfileBase,
    EmployeeProfileCreate,
    EmployeeProfileUpdate,
    ConversationMessageCreate,
    ConversationMessage,
    ConversationStatus,
    MessageRole,
    MessageType,
    BenchStatus,
)
from employee_conversation_service.prompts.system_prompts import (
    RETURNING_USER_GREETING_PROMPT,
    RESUME_GREETING_PROMPT,
    get_conversation_context,
)
from employee_conversation_service.core.exceptions import (
    ConversationError,
    ConversationNotFoundError,
)


# ─────────────────────────────────────────────
#  Helpers / Fixtures
# ─────────────────────────────────────────────

def _make_profile(
    conversation_id=None,
    employee_id="PS001",
    employee_email="test@ps.com",
    employee_name="Test User",
    status=ConversationStatus.COMPLETED,
    completeness=75,
    total_messages=10,
    **overrides,
) -> EmployeeProfile:
    """Create a realistic EmployeeProfile for testing."""
    now = datetime.utcnow()
    cid = conversation_id or uuid4()
    data = dict(
        id=uuid4(),
        conversation_id=cid,
        created_at=now,
        updated_at=now,
        conversation_status=status,
        total_messages=total_messages,
        conversation_started_at=now - timedelta(minutes=15),
        conversation_completed_at=now if status == ConversationStatus.COMPLETED else None,
        employee_id=employee_id,
        employee_name=employee_name,
        employee_email=employee_email,
        career_track="engineering",
        experience_level="senior_consultant",
        years_at_ps=4,
        years_total_experience=8,
        bench_status=BenchStatus.ON_BENCH,
        technical_skills=[
            {"skill_name": "Python", "proficiency_level": 5, "years_of_experience": 6}
        ],
        domain_expertise=["Banking", "Fintech"],
        career_goals={
            "short_term_goals": ["Lead a team"],
            "interested_technologies": ["GenAI"],
        },
        profile_completeness_score=completeness,
        extraction_confidence=Decimal("0.9"),
        source_channel="web",
        language="en",
    )
    data.update(overrides)
    return EmployeeProfile(**data)


def _make_message(conversation_id=None, role=MessageRole.ASSISTANT, content="Hello"):
    now = datetime.utcnow()
    return ConversationMessage(
        id=uuid4(),
        conversation_id=conversation_id or uuid4(),
        created_at=now,
        role=role,
        content=content,
        message_type=MessageType.TEXT,
    )


# ─────────────────────────────────────────────
#  1. Schema / Model Tests
# ─────────────────────────────────────────────

class TestSchemaBackwardsCompatibility:
    """Ensure new fields don't break existing callers."""

    def test_start_request_without_resume_id(self):
        req = ConversationStartRequest(source_channel="web")
        assert req.resume_conversation_id is None
        assert req.employee_id is None

    def test_start_request_with_resume_id(self):
        cid = uuid4()
        req = ConversationStartRequest(resume_conversation_id=cid)
        assert req.resume_conversation_id == cid

    def test_start_response_defaults(self):
        resp = ConversationStartResponse(
            conversation_id=uuid4(),
            employee_profile_id=uuid4(),
            greeting_message="Hello",
        )
        assert resp.is_returning_user is False
        assert resp.is_resumed is False
        assert resp.previous_conversation_count == 0
        assert resp.profile_completeness == 0

    def test_start_response_returning_user(self):
        resp = ConversationStartResponse(
            conversation_id=uuid4(),
            employee_profile_id=uuid4(),
            greeting_message="Welcome back!",
            is_returning_user=True,
            previous_conversation_count=3,
            profile_completeness=75,
        )
        assert resp.is_returning_user is True
        assert resp.previous_conversation_count == 3
        assert resp.profile_completeness == 75

    def test_start_response_resumed(self):
        resp = ConversationStartResponse(
            conversation_id=uuid4(),
            employee_profile_id=uuid4(),
            greeting_message="Let's continue",
            is_resumed=True,
            profile_completeness=50,
        )
        assert resp.is_resumed is True

    def test_profile_update_has_conversation_started_at(self):
        now = datetime.utcnow()
        u = EmployeeProfileUpdate(conversation_started_at=now)
        assert u.conversation_started_at == now

    def test_profile_update_backwards_compat(self):
        u = EmployeeProfileUpdate(
            conversation_status=ConversationStatus.COMPLETED,
            conversation_completed_at=datetime.utcnow(),
        )
        assert u.conversation_started_at is None


class TestNewModels:
    def test_conversation_summary_item(self):
        now = datetime.utcnow()
        item = ConversationSummaryItem(
            conversation_id=uuid4(),
            profile_id=uuid4(),
            conversation_status=ConversationStatus.COMPLETED,
            profile_completeness_score=80,
            conversation_started_at=now,
            conversation_completed_at=now,
            total_messages=12,
        )
        assert item.profile_completeness_score == 80
        assert item.total_messages == 12

    def test_conversation_summary_item_optional_completed_at(self):
        item = ConversationSummaryItem(
            conversation_id=uuid4(),
            profile_id=uuid4(),
            conversation_status=ConversationStatus.IN_PROGRESS,
            profile_completeness_score=30,
            conversation_started_at=datetime.utcnow(),
            total_messages=3,
        )
        assert item.conversation_completed_at is None

    def test_employee_lookup_response_not_found(self):
        resp = EmployeeLookupResponse(found=False)
        assert resp.found is False
        assert resp.latest_profile is None
        assert resp.conversations == []
        assert resp.conversation_counts == {}
        assert resp.has_in_progress is False
        assert resp.in_progress_conversation_id is None

    def test_employee_lookup_response_found(self):
        profile = _make_profile()
        cid = uuid4()
        resp = EmployeeLookupResponse(
            found=True,
            employee_id="PS001",
            employee_email="test@ps.com",
            employee_name="Test User",
            latest_profile=profile,
            conversation_counts={"completed": 2, "total": 3},
            conversations=[
                ConversationSummaryItem(
                    conversation_id=cid,
                    profile_id=profile.id,
                    conversation_status=ConversationStatus.COMPLETED,
                    profile_completeness_score=75,
                    conversation_started_at=datetime.utcnow(),
                    total_messages=10,
                )
            ],
            has_in_progress=True,
            in_progress_conversation_id=cid,
        )
        assert resp.found is True
        assert len(resp.conversations) == 1
        assert resp.conversation_counts["completed"] == 2


# ─────────────────────────────────────────────
#  2. Prompt / Context Tests
# ─────────────────────────────────────────────

class TestPrompts:
    def test_returning_user_context_prepend(self):
        ctx = get_conversation_context(
            {"employee_name": "Alice", "career_track": "engineering"},
            is_returning_user=True,
        )
        assert "returning user" in ctx
        assert "carried forward" in ctx
        assert "Alice" in ctx

    def test_normal_context_no_prepend(self):
        ctx = get_conversation_context(
            {"employee_name": "Bob"},
            is_returning_user=False,
        )
        assert "returning user" not in ctx
        assert "Bob" in ctx

    def test_empty_data_returns_no_info(self):
        assert get_conversation_context({}) == "No information extracted yet."
        assert get_conversation_context({}, is_returning_user=True) == "No information extracted yet."

    def test_returning_user_prompt_has_placeholder(self):
        assert "{profile_context}" in RETURNING_USER_GREETING_PROMPT

    def test_resume_prompt_has_placeholders(self):
        assert "{profile_context}" in RESUME_GREETING_PROMPT
        assert "{last_messages}" in RESUME_GREETING_PROMPT

    def test_prompt_format_works(self):
        result = RETURNING_USER_GREETING_PROMPT.format(profile_context="Some context")
        assert "Some context" in result

        result2 = RESUME_GREETING_PROMPT.format(
            profile_context="Profile info",
            last_messages="user: hello\nassistant: hi",
        )
        assert "Profile info" in result2
        assert "user: hello" in result2


# ─────────────────────────────────────────────
#  3. ConversationService Tests
# ─────────────────────────────────────────────

class TestConversationServiceDispatcher:
    """Test start_conversation routing logic."""

    @pytest.fixture
    def service(self):
        """Create a ConversationService with all dependencies mocked."""
        with patch(
            "employee_conversation_service.services.conversation_service.AzureOpenAIService"
        ), patch(
            "employee_conversation_service.services.conversation_service.StorageService"
        ), patch(
            "employee_conversation_service.services.conversation_service.SkillExtractionService"
        ), patch(
            "employee_conversation_service.services.conversation_service.SpeechService"
        ), patch(
            "employee_conversation_service.services.conversation_service.get_settings"
        ) as mock_settings:
            settings = MagicMock()
            settings.ENABLE_TEXT_TO_SPEECH = False
            settings.MAX_CONVERSATION_MESSAGES = 50
            settings.CONVERSATION_TIMEOUT_MINUTES = 30
            settings.MIN_PROFILE_COMPLETENESS_FOR_COMPLETION = 70
            mock_settings.return_value = settings

            from employee_conversation_service.services.conversation_service import (
                ConversationService,
            )

            svc = ConversationService()
            svc.storage_service = AsyncMock()
            svc.openai_service = AsyncMock()
            svc.extraction_service = MagicMock()
            svc.speech_service = AsyncMock()
            yield svc

    @pytest.mark.asyncio
    async def test_branch1_resume_via_start(self, service):
        """resume_conversation_id triggers Branch 1."""
        cid = uuid4()
        profile = _make_profile(
            conversation_id=cid,
            status=ConversationStatus.IN_PROGRESS,
            completeness=40,
        )
        service.storage_service.get_by_conversation_id.return_value = profile
        service.storage_service.update_employee_profile.return_value = profile
        service.storage_service.get_conversation_history.return_value = []
        service.openai_service.generate_resume_greeting.return_value = "Welcome back!"
        service.openai_service.build_conversation_history.return_value = []
        service.storage_service.save_message.return_value = _make_message(cid)

        req = ConversationStartRequest(resume_conversation_id=cid)
        resp = await service.start_conversation(req)

        assert resp.is_resumed is True
        assert resp.conversation_id == cid
        service.storage_service.get_in_progress_conversation.assert_not_called()

    @pytest.mark.asyncio
    async def test_branch2_returning_user(self, service):
        """Identified user with completed profile triggers Branch 2."""
        completed_profile = _make_profile(
            employee_id="PS001", status=ConversationStatus.COMPLETED, completeness=80
        )
        new_profile = _make_profile(
            employee_id="PS001", status=ConversationStatus.IN_PROGRESS, completeness=0
        )

        service.storage_service.get_in_progress_conversation.return_value = None
        service.storage_service.get_latest_completed_profile.return_value = completed_profile
        service.storage_service.create_employee_profile.return_value = new_profile
        service.storage_service.update_employee_profile.return_value = new_profile
        service.storage_service.get_conversation_count_for_employee.return_value = {
            "completed": 2, "total": 2,
        }
        service.extraction_service.calculate_completeness_score.return_value = 75
        service.openai_service.generate_returning_user_greeting.return_value = "Welcome back, Test User!"
        service.storage_service.save_message.return_value = _make_message()

        req = ConversationStartRequest(employee_id="PS001")
        resp = await service.start_conversation(req)

        assert resp.is_returning_user is True
        assert resp.previous_conversation_count == 2
        service.storage_service.create_employee_profile.assert_called_once()

    @pytest.mark.asyncio
    async def test_branch2_abandons_in_progress(self, service):
        """In-progress conversation is abandoned when starting new."""
        in_progress = _make_profile(
            employee_id="PS001",
            status=ConversationStatus.IN_PROGRESS,
            completeness=30,
        )
        completed = _make_profile(
            employee_id="PS001",
            status=ConversationStatus.COMPLETED,
            completeness=80,
        )
        new_profile = _make_profile(
            employee_id="PS001",
            status=ConversationStatus.IN_PROGRESS,
            completeness=0,
        )

        service.storage_service.get_in_progress_conversation.return_value = in_progress
        service.storage_service.get_latest_completed_profile.return_value = completed
        service.storage_service.create_employee_profile.return_value = new_profile
        service.storage_service.update_employee_profile.return_value = new_profile
        service.storage_service.get_conversation_count_for_employee.return_value = {
            "completed": 1, "abandoned": 1, "total": 2,
        }
        service.extraction_service.calculate_completeness_score.return_value = 70
        service.openai_service.generate_returning_user_greeting.return_value = "Hey!"
        service.storage_service.save_message.return_value = _make_message()

        req = ConversationStartRequest(employee_id="PS001")
        resp = await service.start_conversation(req)

        # Verify abandon was called
        abandon_calls = [
            c for c in service.storage_service.update_employee_profile.call_args_list
            if any(
                isinstance(arg, EmployeeProfileUpdate) and arg.conversation_status == ConversationStatus.ABANDONED
                for arg in c.args + tuple(c.kwargs.values())
            )
        ]
        assert len(abandon_calls) >= 1
        assert resp.is_returning_user is True

    @pytest.mark.asyncio
    async def test_branch2_no_completed_uses_abandoned(self, service):
        """If no completed profile, carry from the just-abandoned one."""
        in_progress = _make_profile(
            employee_id="PS001",
            status=ConversationStatus.IN_PROGRESS,
            completeness=30,
            employee_name="First Timer",
        )
        new_profile = _make_profile(
            employee_id="PS001",
            status=ConversationStatus.IN_PROGRESS,
            completeness=0,
        )

        service.storage_service.get_in_progress_conversation.return_value = in_progress
        service.storage_service.get_latest_completed_profile.return_value = None  # no completed
        service.storage_service.create_employee_profile.return_value = new_profile
        service.storage_service.update_employee_profile.return_value = new_profile
        service.storage_service.get_conversation_count_for_employee.return_value = {
            "abandoned": 1, "total": 1,
        }
        service.extraction_service.calculate_completeness_score.return_value = 25
        service.openai_service.generate_returning_user_greeting.return_value = "Back again!"
        service.storage_service.save_message.return_value = _make_message()

        req = ConversationStartRequest(employee_id="PS001")
        resp = await service.start_conversation(req)

        assert resp.is_returning_user is True

    @pytest.mark.asyncio
    async def test_branch3_new_anonymous(self, service):
        """No identifier triggers brand-new conversation."""
        new_profile = _make_profile(
            employee_id=None,
            employee_email=None,
            status=ConversationStatus.IN_PROGRESS,
            completeness=0,
        )
        service.storage_service.create_employee_profile.return_value = new_profile
        service.openai_service.generate_greeting.return_value = "Hello! Welcome..."
        service.storage_service.save_message.return_value = _make_message()

        req = ConversationStartRequest()
        resp = await service.start_conversation(req)

        assert resp.is_returning_user is False
        assert resp.is_resumed is False
        assert resp.previous_conversation_count == 0
        service.storage_service.get_in_progress_conversation.assert_not_called()
        service.storage_service.get_latest_completed_profile.assert_not_called()

    @pytest.mark.asyncio
    async def test_branch3_identified_no_history(self, service):
        """Identified user with no prior conversations gets Branch 3."""
        new_profile = _make_profile(
            employee_id="PS999",
            status=ConversationStatus.IN_PROGRESS,
            completeness=0,
        )
        service.storage_service.get_in_progress_conversation.return_value = None
        service.storage_service.get_latest_completed_profile.return_value = None
        service.storage_service.create_employee_profile.return_value = new_profile
        service.openai_service.generate_greeting.return_value = "Hello! Welcome..."
        service.storage_service.save_message.return_value = _make_message()

        req = ConversationStartRequest(employee_id="PS999")
        resp = await service.start_conversation(req)

        assert resp.is_returning_user is False
        assert resp.is_resumed is False


class TestResumeConversation:
    @pytest.fixture
    def service(self):
        with patch(
            "employee_conversation_service.services.conversation_service.AzureOpenAIService"
        ), patch(
            "employee_conversation_service.services.conversation_service.StorageService"
        ), patch(
            "employee_conversation_service.services.conversation_service.SkillExtractionService"
        ), patch(
            "employee_conversation_service.services.conversation_service.SpeechService"
        ), patch(
            "employee_conversation_service.services.conversation_service.get_settings"
        ) as mock_settings:
            settings = MagicMock()
            settings.ENABLE_TEXT_TO_SPEECH = False
            mock_settings.return_value = settings

            from employee_conversation_service.services.conversation_service import (
                ConversationService,
            )

            svc = ConversationService()
            svc.storage_service = AsyncMock()
            svc.openai_service = AsyncMock()
            svc.extraction_service = MagicMock()
            svc.speech_service = AsyncMock()
            yield svc

    @pytest.mark.asyncio
    async def test_resume_success(self, service):
        cid = uuid4()
        profile = _make_profile(
            conversation_id=cid,
            status=ConversationStatus.IN_PROGRESS,
            completeness=45,
        )
        service.storage_service.get_by_conversation_id.return_value = profile
        service.storage_service.update_employee_profile.return_value = profile
        service.storage_service.get_conversation_history.return_value = [
            _make_message(cid, MessageRole.ASSISTANT, "Hello"),
            _make_message(cid, MessageRole.USER, "I'm a developer"),
        ]
        service.openai_service.build_conversation_history.return_value = [
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "I'm a developer"},
        ]
        service.openai_service.generate_resume_greeting.return_value = "Let's continue!"
        service.storage_service.save_message.return_value = _make_message(cid)

        resp = await service.resume_conversation(cid)

        assert resp.is_resumed is True
        assert resp.conversation_id == cid
        assert resp.greeting_message == "Let's continue!"
        # Verify timeout was reset
        service.storage_service.update_employee_profile.assert_called()

    @pytest.mark.asyncio
    async def test_resume_not_found(self, service):
        service.storage_service.get_by_conversation_id.return_value = None
        with pytest.raises(ConversationNotFoundError):
            await service.resume_conversation(uuid4())

    @pytest.mark.asyncio
    async def test_resume_completed_conversation_fails(self, service):
        cid = uuid4()
        profile = _make_profile(
            conversation_id=cid,
            status=ConversationStatus.COMPLETED,
        )
        service.storage_service.get_by_conversation_id.return_value = profile
        with pytest.raises(ConversationError, match="Cannot resume"):
            await service.resume_conversation(cid)

    @pytest.mark.asyncio
    async def test_resume_abandoned_conversation_fails(self, service):
        cid = uuid4()
        profile = _make_profile(
            conversation_id=cid,
            status=ConversationStatus.ABANDONED,
        )
        service.storage_service.get_by_conversation_id.return_value = profile
        with pytest.raises(ConversationError, match="Cannot resume"):
            await service.resume_conversation(cid)


class TestLookupEmployee:
    @pytest.fixture
    def service(self):
        with patch(
            "employee_conversation_service.services.conversation_service.AzureOpenAIService"
        ), patch(
            "employee_conversation_service.services.conversation_service.StorageService"
        ), patch(
            "employee_conversation_service.services.conversation_service.SkillExtractionService"
        ), patch(
            "employee_conversation_service.services.conversation_service.SpeechService"
        ), patch(
            "employee_conversation_service.services.conversation_service.get_settings"
        ) as mock_settings:
            settings = MagicMock()
            mock_settings.return_value = settings

            from employee_conversation_service.services.conversation_service import (
                ConversationService,
            )

            svc = ConversationService()
            svc.storage_service = AsyncMock()
            svc.openai_service = AsyncMock()
            svc.extraction_service = MagicMock()
            yield svc

    @pytest.mark.asyncio
    async def test_lookup_not_found(self, service):
        service.storage_service.find_employee_profiles_by_identifier.return_value = ([], 0)
        resp = await service.lookup_employee(employee_email="nobody@ps.com")
        assert resp.found is False
        assert resp.employee_email == "nobody@ps.com"

    @pytest.mark.asyncio
    async def test_lookup_found_with_completed(self, service):
        completed = _make_profile(status=ConversationStatus.COMPLETED)
        in_prog = _make_profile(status=ConversationStatus.IN_PROGRESS, completeness=30)

        service.storage_service.find_employee_profiles_by_identifier.return_value = (
            [completed, in_prog], 2,
        )
        service.storage_service.get_latest_completed_profile.return_value = completed
        service.storage_service.get_in_progress_conversation.return_value = in_prog
        service.storage_service.get_conversation_count_for_employee.return_value = {
            "completed": 1, "in_progress": 1, "total": 2,
        }

        resp = await service.lookup_employee(employee_id="PS001")
        assert resp.found is True
        assert resp.latest_profile is not None
        assert resp.has_in_progress is True
        assert resp.in_progress_conversation_id == in_prog.conversation_id
        assert len(resp.conversations) == 2


class TestCarryForwardFields:
    """Test that carry-forward works correctly."""

    def test_carry_forward_excludes_metadata(self):
        from employee_conversation_service.services.conversation_service import ConversationService

        forbidden = [
            "id", "conversation_id", "conversation_status",
            "conversation_started_at", "conversation_completed_at",
            "total_messages", "created_at", "updated_at",
            "extraction_confidence", "profile_completeness_score",
            "missing_information", "conversation_transcript",
            "raw_audio_references", "source_channel", "language",
        ]
        for field in forbidden:
            assert field not in ConversationService.CARRY_FORWARD_FIELDS, (
                f"{field} should NOT be carried forward"
            )

    def test_carry_forward_includes_profile_fields(self):
        from employee_conversation_service.services.conversation_service import ConversationService

        expected = [
            "employee_name", "employee_id", "employee_email",
            "location", "career_track", "experience_level",
            "technical_skills", "soft_skills", "domain_expertise",
            "career_goals", "project_history", "professional_summary",
        ]
        for field in expected:
            assert field in ConversationService.CARRY_FORWARD_FIELDS, (
                f"{field} SHOULD be carried forward"
            )


# ─────────────────────────────────────────────
#  4. API Endpoint Tests (via TestClient)
# ─────────────────────────────────────────────

class TestAPIEndpoints:
    """Test new API endpoints with httpx TestClient."""

    @pytest.fixture
    def client(self):
        """Create a TestClient with mocked services."""
        from fastapi.testclient import TestClient

        # Patch ConversationService before importing the router
        with patch(
            "employee_conversation_service.api.v1.endpoints.conversation.ConversationService"
        ) as MockService:
            mock_svc = AsyncMock()
            MockService.return_value = mock_svc

            from employee_conversation_service.api.v1.endpoints.conversation import router
            from fastapi import FastAPI

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/conversation")

            yield TestClient(app), mock_svc

    def test_lookup_no_params_returns_400(self, client):
        test_client, _ = client
        resp = test_client.get("/api/v1/conversation/lookup")
        assert resp.status_code == 400

    def test_lookup_by_email_not_found(self, client):
        test_client, mock_svc = client
        mock_svc.lookup_employee.return_value = EmployeeLookupResponse(
            found=False, employee_email="nobody@ps.com"
        )
        resp = test_client.get(
            "/api/v1/conversation/lookup?employee_email=nobody@ps.com"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["found"] is False

    def test_lookup_by_id_found(self, client):
        test_client, mock_svc = client
        mock_svc.lookup_employee.return_value = EmployeeLookupResponse(
            found=True,
            employee_id="PS001",
            employee_name="Test User",
            conversation_counts={"completed": 1, "total": 1},
            conversations=[],
        )
        resp = test_client.get("/api/v1/conversation/lookup?employee_id=PS001")
        assert resp.status_code == 200
        data = resp.json()
        assert data["found"] is True
        assert data["employee_name"] == "Test User"

    def test_resume_success(self, client):
        test_client, mock_svc = client
        cid = uuid4()
        mock_svc.resume_conversation.return_value = ConversationStartResponse(
            conversation_id=cid,
            employee_profile_id=uuid4(),
            greeting_message="Welcome back!",
            is_resumed=True,
            profile_completeness=50,
        )
        resp = test_client.post(f"/api/v1/conversation/{cid}/resume")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_resumed"] is True
        assert data["greeting_message"] == "Welcome back!"

    def test_resume_not_found(self, client):
        test_client, mock_svc = client
        cid = uuid4()
        mock_svc.resume_conversation.side_effect = ConversationNotFoundError(str(cid))
        resp = test_client.post(f"/api/v1/conversation/{cid}/resume")
        assert resp.status_code == 404

    def test_resume_bad_status(self, client):
        test_client, mock_svc = client
        cid = uuid4()
        mock_svc.resume_conversation.side_effect = ConversationError(
            "Cannot resume conversation with status 'completed'"
        )
        resp = test_client.post(f"/api/v1/conversation/{cid}/resume")
        assert resp.status_code == 400

    def test_start_still_works(self, client):
        """Existing POST /start endpoint still works."""
        test_client, mock_svc = client
        cid = uuid4()
        mock_svc.start_conversation.return_value = ConversationStartResponse(
            conversation_id=cid,
            employee_profile_id=uuid4(),
            greeting_message="Hello!",
        )
        resp = test_client.post(
            "/api/v1/conversation/start",
            json={"source_channel": "web"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["is_returning_user"] is False
        assert data["is_resumed"] is False


# ─────────────────────────────────────────────
#  5. SQL Schema Validation
# ─────────────────────────────────────────────

class TestSQLSchema:
    def test_schema_contains_new_indexes(self):
        import os
        schema_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..",
            "employee_conversation_service", "schema.sql",
        )
        schema_path = os.path.normpath(schema_path)
        with open(schema_path) as f:
            sql = f.read()

        assert "idx_employee_profiles_employee_id" in sql
        assert "idx_employee_profiles_employee_email" in sql
        assert "idx_employee_profiles_employee_id_completed" in sql
        assert "idx_employee_profiles_employee_email_completed" in sql
        assert "WHERE employee_id IS NOT NULL" in sql
        assert "WHERE employee_email IS NOT NULL" in sql
        assert "WHERE conversation_status = 'completed'" in sql
