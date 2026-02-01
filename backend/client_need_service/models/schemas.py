"""
Pydantic models and schemas for the Client Need Service Agent.
Defines data structures for API requests, responses, and database models.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# Enums


class ConversationStatus(str, Enum):
    """Status of a conversation."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class UrgencyLevel(str, Enum):
    """Urgency level for client needs."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SkillLevel(str, Enum):
    """Required skill level."""

    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    EXPERT = "expert"


class MessageRole(str, Enum):
    """Role of a message in conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(str, Enum):
    """Type of message."""

    TEXT = "text"
    SPEECH = "speech"
    SYSTEM = "system"


class BudgetType(str, Enum):
    """Budget type."""

    HOURLY = "hourly"
    FIXED = "fixed"
    MONTHLY = "monthly"


class TimelineFlexibility(str, Enum):
    """Timeline flexibility."""

    FLEXIBLE = "flexible"
    SOMEWHAT_FLEXIBLE = "somewhat_flexible"
    STRICT = "strict"


class WorkLocation(str, Enum):
    """Work location type."""

    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"


class RoleCategory(str, Enum):
    """Canonical role categories (Publicis Sapient-equivalent disciplines)."""

    STRATEGY_CONSULTING = "strategy_consulting"
    PRODUCT_MANAGEMENT = "product_management"
    TECHNOLOGY_ENGINEERING = "technology_engineering"
    DESIGN_UX = "design_ux"
    CREATIVE_CONTENT = "creative_content"
    PROJECT_PROGRAM_MANAGEMENT = "project_program_management"
    QUALITY_TESTING = "quality_testing"
    DATA_ANALYTICS = "data_analytics"


class IntakeSourceType(str, Enum):
    """Source type for client intake."""

    PDF = "pdf"
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    EMAIL = "email"
    FORM = "form"
    CHAT_EXPORT = "chat_export"
    OTHER = "other"


class IntakeStatus(str, Enum):
    """Processing status for intake packages."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Conversation API Schemas


class ConversationStartRequest(BaseModel):
    """Request to start a new conversation."""

    client_name: Optional[str] = Field(None, max_length=255)
    client_email: Optional[EmailStr] = None
    client_phone: Optional[str] = Field(None, max_length=50)
    source_channel: str = Field(default="web", max_length=50)
    initial_context: Optional[Dict[str, Any]] = Field(default=None)


class ConversationStartResponse(BaseModel):
    """Response when starting a conversation."""

    conversation_id: UUID
    client_need_id: UUID
    greeting_message: str
    audio_url: Optional[str] = None


class MessageRequest(BaseModel):
    """Request to send a message in conversation."""

    message: str = Field(..., min_length=1, max_length=5000)
    message_type: MessageType = MessageType.TEXT


class ExtractionUpdate(BaseModel):
    """Updates to extracted information from a message."""

    field_name: str
    field_value: Any
    confidence: float = Field(ge=0.0, le=1.0)


class MessageResponse(BaseModel):
    """Response after sending a message."""

    conversation_id: UUID
    message_id: UUID
    assistant_message: str
    audio_url: Optional[str] = None
    extraction_updates: Optional[List[ExtractionUpdate]] = None
    profile_completeness: int = Field(ge=0, le=100)
    missing_fields: List[str]
    can_complete: bool


class ConversationStatusResponse(BaseModel):
    """Response for conversation status query."""

    conversation_id: UUID
    status: ConversationStatus
    total_messages: int
    profile_completeness: int
    missing_fields: List[str]
    duration_minutes: int
    can_complete: bool
    conversation_started_at: datetime
    last_message_at: Optional[datetime] = None


class ConversationCompleteResponse(BaseModel):
    """Response when completing a conversation."""

    conversation_id: UUID
    client_need_id: UUID
    status: ConversationStatus
    profile_completeness: int
    summary: str


# Speech API Schemas


class TranscriptionRequest(BaseModel):
    """Request for speech transcription (form data handled separately)."""

    language: Optional[str] = Field(default="en-US")


class TranscriptionResponse(BaseModel):
    """Response from speech transcription."""

    transcription: str
    confidence: float = Field(ge=0.0, le=1.0)
    duration_seconds: float


class TranscriptionErrorDetail(BaseModel):
    """Error detail for transcription/audio upload failures (API docs)."""

    error: str
    error_code: str = Field(
        ...,
        description="Stable code: file_too_large, file_too_small, unsupported_format, no_speech_detected, transcription_service_error, audio_processing_error",
    )
    details: Optional[Dict[str, Any]] = None


class SynthesisRequest(BaseModel):
    """Request for text-to-speech synthesis."""

    text: str = Field(..., min_length=1, max_length=5000)
    voice_name: Optional[str] = Field(default="en-US-JennyNeural")


class Voice(BaseModel):
    """Available voice for TTS."""

    name: str
    language: str
    gender: str
    locale: str


class VoicesResponse(BaseModel):
    """Response with available voices."""

    voices: List[Voice]


# Client Need Database Schemas


class WorkLocationDetails(BaseModel):
    """Details about work location."""

    city: Optional[str] = None
    country: Optional[str] = None
    timezone: Optional[str] = None
    address: Optional[str] = None


class RoleInfo(BaseModel):
    """Information about a required role/discipline."""

    category: RoleCategory = Field(..., description="Normalized role category")
    evidence: str = Field(..., description="Original wording from client brief")
    description: Optional[str] = Field(
        None, description="Additional details about the role"
    )
    count: Optional[int] = Field(
        None, ge=1, description="Number of people needed in this role"
    )


class ClientNeedBase(BaseModel):
    """Base model for client need with common fields."""

    # Client Information
    client_name: Optional[str] = Field(None, max_length=255)
    client_email: Optional[EmailStr] = None
    client_phone: Optional[str] = Field(None, max_length=50)
    client_company: Optional[str] = Field(None, max_length=255)

    # Project Details
    project_title: Optional[str] = Field(None, max_length=500)
    project_description: Optional[str] = None
    project_type: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)

    # Skills
    required_skills: Optional[List[str]] = None
    preferred_skills: Optional[List[str]] = None
    skill_level: Optional[SkillLevel] = None
    certifications_required: Optional[List[str]] = None

    # Budget
    budget_min: Optional[Decimal] = Field(None, ge=0)
    budget_max: Optional[Decimal] = Field(None, ge=0)
    budget_currency: str = Field(default="USD", max_length=10)
    budget_type: Optional[BudgetType] = None

    # Timeline
    timeline_start_date: Optional[date] = None
    timeline_end_date: Optional[date] = None
    timeline_duration_weeks: Optional[int] = Field(None, ge=1)
    timeline_flexibility: Optional[TimelineFlexibility] = None

    # Urgency
    urgency_level: Optional[UrgencyLevel] = None
    priority_score: Optional[int] = Field(None, ge=1, le=10)
    start_date_importance: Optional[str] = Field(None, max_length=50)

    # Work Arrangement
    work_location: Optional[WorkLocation] = None
    work_location_details: Optional[WorkLocationDetails] = None
    work_hours_requirement: Optional[str] = Field(None, max_length=100)

    # Additional Requirements
    team_size_needed: Optional[int] = Field(None, ge=1)
    collaboration_tools: Optional[List[str]] = None
    communication_preferences: Optional[List[str]] = None

    # Roles & Disciplines
    required_roles: Optional[List[RoleInfo]] = Field(
        None, description="Identified roles/disciplines needed for the project"
    )

    # AI Insights
    needs_summary: Optional[str] = None
    key_challenges: Optional[List[str]] = None
    success_criteria: Optional[List[str]] = None
    risk_factors: Optional[List[str]] = None

    # Metadata
    source_channel: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

    @field_validator("budget_min", "budget_max")
    @classmethod
    def validate_budget(cls, v):
        """Validate budget values."""
        if v is not None and v < 0:
            raise ValueError("Budget must be non-negative")
        return v


class ClientNeedCreate(ClientNeedBase):
    """Schema for creating a client need."""

    conversation_id: UUID


class ClientNeedUpdate(ClientNeedBase):
    """Schema for updating a client need (all fields optional)."""

    pass


class ClientNeed(ClientNeedBase):
    """Complete client need model with database fields."""

    id: UUID
    conversation_id: UUID
    created_at: datetime
    updated_at: datetime

    # Conversation Status
    conversation_status: ConversationStatus
    total_messages: int = 0
    conversation_started_at: datetime
    conversation_completed_at: Optional[datetime] = None

    # Profile Metrics
    extraction_confidence: Optional[Decimal] = Field(None, ge=0, le=1)
    profile_completeness_score: int = Field(default=0, ge=0, le=100)
    missing_information: Optional[List[str]] = None

    # Raw Data
    conversation_transcript: Optional[List[Dict[str, Any]]] = None
    raw_audio_references: Optional[List[str]] = None

    # Additional Metadata
    source_channel: str = "web"
    language: str = "en"

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "conversation_id": "660e8400-e29b-41d4-a716-446655440000",
                "client_name": "John Doe",
                "client_email": "john@example.com",
                "project_title": "E-commerce Platform Development",
                "required_skills": ["Python", "React", "PostgreSQL"],
                "budget_min": 5000,
                "budget_max": 10000,
                "urgency_level": "high",
                "profile_completeness_score": 85,
            }
        },
    }


class ClientNeedList(BaseModel):
    """Response model for listing client needs."""

    items: List[ClientNeed]
    total: int
    limit: int
    offset: int


# Conversation Message Schemas


class ConversationMessageBase(BaseModel):
    """Base model for conversation messages."""

    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    audio_url: Optional[str] = None
    transcription_confidence: Optional[Decimal] = Field(None, ge=0, le=1)


class ConversationMessageCreate(ConversationMessageBase):
    """Schema for creating a conversation message."""

    conversation_id: UUID


class ConversationMessage(ConversationMessageBase):
    """Complete conversation message model."""

    id: UUID
    conversation_id: UUID
    created_at: datetime
    tokens_used: Optional[int] = None
    model_version: Optional[str] = None
    processing_time_ms: Optional[int] = None

    model_config = {"from_attributes": True}


class ConversationHistory(BaseModel):
    """Response model for conversation history."""

    conversation_id: UUID
    messages: List[ConversationMessage]
    total_messages: int


# Extraction History Schemas


class ExtractionHistoryCreate(BaseModel):
    """Schema for creating extraction history entry."""

    conversation_id: UUID
    extracted_field: str
    extracted_value: Any
    confidence_score: Optional[Decimal] = Field(None, ge=0, le=1)
    extraction_method: Optional[str] = Field(None, max_length=50)


class ExtractionHistory(BaseModel):
    """Complete extraction history model."""

    id: UUID
    conversation_id: UUID
    created_at: datetime
    extracted_field: str
    extracted_value: Any
    confidence_score: Optional[Decimal] = None
    extraction_method: Optional[str] = None

    model_config = {"from_attributes": True}


# Client Intake Package Schemas


class IntakeMetadata(BaseModel):
    """Metadata for intake package."""

    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    language: Optional[str] = "en"
    uploaded_by: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class NormalizedContent(BaseModel):
    """Normalized content structure."""

    text: str
    sections: Optional[List[Dict[str, str]]] = None  # [{title, content}]
    entities: Optional[List[Dict[str, Any]]] = None  # Extracted entities
    word_count: Optional[int] = None
    language: Optional[str] = None


class ClientIntakePackageBase(BaseModel):
    """Base model for client intake package."""

    source_type: IntakeSourceType
    raw_content: Optional[str] = None  # Original raw content
    normalized_content: Optional[NormalizedContent] = None
    metadata: Optional[IntakeMetadata] = None
    processing_notes: Optional[str] = None


class ClientIntakePackageCreate(BaseModel):
    """Schema for creating an intake package."""

    source_type: IntakeSourceType
    raw_content: str
    metadata: Optional[IntakeMetadata] = None
    client_name: Optional[str] = None
    client_email: Optional[EmailStr] = None


class ClientIntakePackageUpdate(BaseModel):
    """Schema for updating an intake package."""

    status: Optional[IntakeStatus] = None
    normalized_content: Optional[NormalizedContent] = None
    processing_notes: Optional[str] = None
    error_message: Optional[str] = None


class ClientIntakePackage(ClientIntakePackageBase):
    """Complete intake package model with database fields."""

    id: UUID
    status: IntakeStatus
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    client_name: Optional[str] = None
    client_email: Optional[EmailStr] = None
    client_need_id: Optional[UUID] = None  # Link to extracted client need
    error_message: Optional[str] = None
    audit_trail: Optional[List[Dict[str, Any]]] = None  # Processing steps

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "source_type": "text",
            }
        },
    }

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "ClientIntakePackage":
        """Create ClientIntakePackage from database row, handling JSONB fields."""
        import json

        data = dict(row)

        # Parse JSONB fields if they're strings
        if isinstance(data.get("normalized_content"), str):
            data["normalized_content"] = json.loads(data["normalized_content"])

        if isinstance(data.get("metadata"), str):
            data["metadata"] = json.loads(data["metadata"])

        if isinstance(data.get("audit_trail"), str):
            data["audit_trail"] = json.loads(data["audit_trail"])

        return cls(**data)


class ClientIntakePackageList(BaseModel):
    """Paginated list of intake packages."""

    items: List[ClientIntakePackage]
    total: int
    limit: int
    offset: int


# Health Check Schemas


class HealthCheck(BaseModel):
    """Basic health check response."""

    status: str = "healthy"
    timestamp: datetime


class ServiceStatus(BaseModel):
    """Status of individual service."""

    name: str
    status: str
    message: Optional[str] = None


class DetailedHealthCheck(BaseModel):
    """Detailed health check with service statuses."""

    status: str
    timestamp: datetime
    services: List[ServiceStatus]
    version: str = "1.0.0"


# Matching Agent Schemas


class SkillMatch(BaseModel):
    """Details about a skill match."""

    skill: str = Field(..., description="Skill name")
    required: bool = Field(..., description="Whether this skill is required")
    candidate_has: bool = Field(..., description="Whether candidate has this skill")
    proficiency_level: Optional[str] = Field(None, description="Candidate's proficiency level")


class MatchExplanation(BaseModel):
    """Detailed explanation of why a candidate matches."""

    strengths: List[str] = Field(default_factory=list, description="Candidate strengths for this role")
    skill_matches: List[SkillMatch] = Field(default_factory=list, description="Detailed skill matching")
    gaps: List[str] = Field(default_factory=list, description="Missing skills or requirements")
    additional_notes: Optional[str] = Field(None, description="Additional context or notes")


class CandidateMatch(BaseModel):
    """A single candidate match result."""

    employee_profile_id: UUID = Field(..., description="ID of the matched employee profile")
    employee_name: str = Field(..., description="Employee name")
    employee_email: Optional[str] = Field(None, description="Employee email")
    match_score: int = Field(..., ge=0, le=100, description="Overall match score (0-100)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="AI confidence in this match")
    explanation: MatchExplanation = Field(..., description="Detailed match explanation")
    rank: int = Field(..., ge=1, description="Ranking position in results")

    # Profile highlights
    experience_years: Optional[int] = Field(None, description="Years of experience")
    key_skills: List[str] = Field(default_factory=list, description="Candidate's key skills")
    current_availability: Optional[str] = Field(None, description="Availability status")


class MatchRequest(BaseModel):
    """Request to find matching candidates for a client need."""

    client_need_id: UUID = Field(..., description="ID of the client need to match against")
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum number of results to return")
    min_match_score: int = Field(default=50, ge=0, le=100, description="Minimum match score threshold")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional filtering criteria")


class MatchResponse(BaseModel):
    """Response with ranked candidate matches."""

    client_need_id: UUID = Field(..., description="ID of the client need")
    total_candidates_evaluated: int = Field(..., description="Total number of candidates evaluated")
    matches: List[CandidateMatch] = Field(..., description="Ranked list of matching candidates")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When matches were generated")
    ai_model: str = Field(default="gpt-4", description="AI model used for matching")


class SavedMatchResult(BaseModel):
    """Saved match result for audit trail."""

    id: UUID = Field(..., description="Match result ID")
    client_need_id: UUID = Field(..., description="Client need ID")
    employee_profile_id: UUID = Field(..., description="Employee profile ID")
    match_score: int = Field(..., description="Match score")
    confidence: float = Field(..., description="Confidence level")
    explanation: Dict[str, Any] = Field(..., description="Match explanation as JSON")
    rank: int = Field(..., description="Ranking position")
    created_at: datetime = Field(..., description="When match was created")
    created_by: Optional[str] = Field(None, description="Who triggered the matching")
