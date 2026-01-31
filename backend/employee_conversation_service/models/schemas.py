"""
Pydantic models and schemas for the Employee Conversation Service Agent.
Designed for Publicis Sapient internal talent matching system.
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


class BenchStatus(str, Enum):
    """Employee's current assignment status."""
    ON_PROJECT = "on_project"
    ON_BENCH = "on_bench"
    ROLLING_OFF = "rolling_off"  # Ending project soon
    PARTIALLY_ALLOCATED = "partially_allocated"  # Part-time on project


class CareerTrack(str, Enum):
    """PS career track/discipline."""
    ENGINEERING = "engineering"
    EXPERIENCE_DESIGN = "experience_design"
    PRODUCT = "product"
    STRATEGY = "strategy"
    DATA_AI = "data_ai"
    CLOUD_INFRASTRUCTURE = "cloud_infrastructure"


class ExperienceLevel(str, Enum):
    """PS experience level/grade."""
    ASSOCIATE = "associate"
    CONSULTANT = "consultant"
    SENIOR_CONSULTANT = "senior_consultant"
    MANAGER = "manager"
    SENIOR_MANAGER = "senior_manager"
    ASSOCIATE_DIRECTOR = "associate_director"
    DIRECTOR = "director"
    SENIOR_DIRECTOR = "senior_director"


class AllocationPercentage(str, Enum):
    """Allocation percentage on current project."""
    PERCENT_25 = "25"
    PERCENT_50 = "50"
    PERCENT_75 = "75"
    PERCENT_100 = "100"


class ProjectRole(str, Enum):
    """Role on a project."""
    DEVELOPER = "developer"
    SENIOR_DEVELOPER = "senior_developer"
    TECH_LEAD = "tech_lead"
    ARCHITECT = "architect"
    DESIGNER = "designer"
    LEAD_DESIGNER = "lead_designer"
    PRODUCT_MANAGER = "product_manager"
    SCRUM_MASTER = "scrum_master"
    DATA_ENGINEER = "data_engineer"
    DATA_SCIENTIST = "data_scientist"
    DEVOPS_ENGINEER = "devops_engineer"
    QA_ENGINEER = "qa_engineer"


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


# Conversation API Schemas

class ConversationStartRequest(BaseModel):
    """Request to start a new conversation."""
    employee_id: Optional[str] = Field(None, description="PS Employee ID")
    employee_email: Optional[EmailStr] = None
    source_channel: str = Field(default="web", max_length=50)
    initial_context: Optional[Dict[str, Any]] = Field(default=None)


class ConversationStartResponse(BaseModel):
    """Response when starting a conversation."""
    conversation_id: UUID
    employee_profile_id: UUID
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
    employee_profile_id: UUID
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


# Employee Profile Database Schemas

class SkillProficiency(BaseModel):
    """Skill with proficiency level and years of experience."""
    skill_name: str
    proficiency_level: int = Field(ge=1, le=5, description="1=Beginner, 5=Expert")
    years_of_experience: Optional[float] = Field(None, ge=0)
    last_used: Optional[date] = None
    acquired_through: Optional[List[str]] = Field(
        None, 
        description="Where skill was acquired: e.g., ['Project ABC', 'Training: Advanced React']"
    )


class ProjectExperience(BaseModel):
    """Experience on a specific PS project."""
    project_id: Optional[str] = Field(None, description="Project ID (PID)")
    project_name: Optional[str] = None
    client_name: Optional[str] = None
    industry: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    duration_months: Optional[int] = None
    role: Optional[ProjectRole] = None
    allocation_percentage: Optional[int] = Field(None, ge=0, le=100)
    key_responsibilities: Optional[List[str]] = None
    technologies_used: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    team_size: Optional[int] = None


class CurrentAssignment(BaseModel):
    """Current project assignment details."""
    project_id: Optional[str] = Field(None, description="Current Project ID (PID)")
    project_name: Optional[str] = None
    client_name: Optional[str] = None
    role: Optional[ProjectRole] = None
    allocation_percentage: int = Field(100, ge=0, le=100)
    start_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    rolling_off_date: Optional[date] = Field(
        None, 
        description="Date when employee will be available"
    )


class TrainingCertification(BaseModel):
    """Training or certification completed."""
    name: str
    provider: Optional[str] = Field(None, description="e.g., 'Udemy', 'Coursera', 'AWS'")
    completion_date: Optional[date] = None
    expiry_date: Optional[date] = None
    certificate_url: Optional[str] = None
    skills_gained: Optional[List[str]] = None


class CareerGoals(BaseModel):
    """Employee's career aspirations within PS."""
    short_term_goals: Optional[List[str]] = Field(
        None,
        description="6-12 month goals, e.g., 'Lead a team', 'Work on AI projects'"
    )
    long_term_goals: Optional[List[str]] = Field(
        None,
        description="2-3 year goals, e.g., 'Become Associate Director', 'Specialize in fintech'"
    )
    interested_industries: Optional[List[str]] = Field(
        None,
        description="Industries of interest, e.g., ['Finance', 'Healthcare', 'Retail']"
    )
    interested_technologies: Optional[List[str]] = Field(
        None,
        description="Technologies interested in learning/using"
    )
    preferred_project_types: Optional[List[str]] = Field(
        None,
        description="e.g., ['Greenfield', 'Transformation', 'Maintenance']"
    )
    preferred_client_engagement: Optional[List[str]] = Field(
        None,
        description="e.g., ['Long-term', 'Short-term', 'Multiple clients']"
    )
    interested_roles: Optional[List[ProjectRole]] = Field(
        None,
        description="Roles interested in taking on"
    )


class Location(BaseModel):
    """Employee's location information."""
    city: str
    country: str
    timezone: str = Field(description="e.g., 'America/New_York', 'Europe/London'")
    ps_office: Optional[str] = Field(
        None, 
        description="Nearest PS office, e.g., 'London', 'New York', 'Bangalore'"
    )
    willing_to_travel: bool = Field(default=False)
    travel_percentage_preference: Optional[int] = Field(
        None, 
        ge=0, 
        le=100,
        description="Percentage of time willing to travel"
    )


class EmployeeProfileBase(BaseModel):
    """Base model for employee profile with common fields."""
    
    # Basic Information
    employee_id: Optional[str] = Field(None, description="PS Employee ID")
    employee_name: Optional[str] = Field(None, max_length=255)
    employee_email: Optional[EmailStr] = None
    
    # Location
    location: Optional[Location] = None
    
    # PS Career Information
    career_track: Optional[CareerTrack] = None
    experience_level: Optional[ExperienceLevel] = None
    years_at_ps: Optional[int] = Field(None, ge=0)
    years_total_experience: Optional[int] = Field(None, ge=0)
    
    # Current Assignment Status
    bench_status: BenchStatus = BenchStatus.ON_BENCH
    current_assignment: Optional[CurrentAssignment] = None
    availability_date: Optional[date] = Field(
        None,
        description="Date when employee will be available for new project"
    )
    
    # Skills & Expertise
    technical_skills: Optional[List[SkillProficiency]] = None
    soft_skills: Optional[List[str]] = Field(
        None,
        description="e.g., ['Leadership', 'Client Communication', 'Mentoring']"
    )
    domain_expertise: Optional[List[str]] = Field(
        None,
        description="Industry domains, e.g., ['Banking', 'E-commerce', 'Healthcare']"
    )
    methodologies: Optional[List[str]] = Field(
        None,
        description="e.g., ['Agile', 'Scrum', 'SAFe', 'Design Thinking']"
    )
    tools_platforms: Optional[List[str]] = Field(
        None,
        description="e.g., ['JIRA', 'Figma', 'AWS', 'Azure']"
    )
    
    # Project History
    project_history: Optional[List[ProjectExperience]] = Field(
        None,
        description="Past PS projects in reverse chronological order"
    )
    notable_achievements: Optional[List[str]] = None
    
    # Learning & Development
    training_certifications: Optional[List[TrainingCertification]] = None
    current_learning: Optional[List[str]] = Field(
        None,
        description="Currently taking courses/certifications"
    )
    
    # Career Goals & Interests
    career_goals: Optional[CareerGoals] = None
    
    # Additional Context
    professional_summary: Optional[str] = Field(
        None,
        description="Brief summary of experience and expertise"
    )
    strengths: Optional[List[str]] = Field(
        None,
        description="Key strengths identified through conversation"
    )
    areas_for_growth: Optional[List[str]] = Field(
        None,
        description="Skills or areas interested in developing"
    )
    
    # Internal Notes
    notes: Optional[str] = Field(
        None,
        description="Additional notes from conversation"
    )
    
    @field_validator("years_at_ps", "years_total_experience")
    @classmethod
    def validate_years(cls, v):
        """Validate years values."""
        if v is not None and v < 0:
            raise ValueError("Years must be non-negative")
        return v


class EmployeeProfileCreate(EmployeeProfileBase):
    """Schema for creating an employee profile."""
    conversation_id: UUID


class EmployeeProfileUpdate(EmployeeProfileBase):
    """Schema for updating an employee profile (all fields optional)."""
    pass


class EmployeeProfile(EmployeeProfileBase):
    """Complete employee profile model with database fields."""
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
    
    # Metadata
    source_channel: str = "web"
    language: str = "en"
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "conversation_id": "660e8400-e29b-41d4-a716-446655440000",
                "employee_id": "PS123456",
                "employee_name": "Sarah Johnson",
                "employee_email": "sarah.johnson@publicissapient.com",
                "career_track": "engineering",
                "experience_level": "senior_consultant",
                "years_at_ps": 4,
                "years_total_experience": 8,
                "bench_status": "rolling_off",
                "location": {
                    "city": "London",
                    "country": "United Kingdom",
                    "timezone": "Europe/London",
                    "ps_office": "London"
                },
                "current_assignment": {
                    "project_id": "PID-2024-001",
                    "project_name": "Digital Banking Transformation",
                    "client_name": "Major Bank UK",
                    "role": "tech_lead",
                    "allocation_percentage": 100,
                    "rolling_off_date": "2025-03-15"
                },
                "availability_date": "2025-03-15",
                "technical_skills": [
                    {
                        "skill_name": "Python",
                        "proficiency_level": 5,
                        "years_of_experience": 6
                    },
                    {
                        "skill_name": "React",
                        "proficiency_level": 4,
                        "years_of_experience": 4
                    }
                ],
                "domain_expertise": ["Banking", "Fintech"],
                "career_goals": {
                    "short_term_goals": ["Lead larger teams", "Deliver AI/ML projects"],
                    "interested_industries": ["Healthcare", "Fintech"],
                    "interested_technologies": ["GenAI", "LangChain", "Azure OpenAI"]
                },
                "profile_completeness_score": 85
            }
        }
    }


class EmployeeProfileList(BaseModel):
    """Response model for listing employee profiles."""
    items: List[EmployeeProfile]
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