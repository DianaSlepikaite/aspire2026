"""Schemas for employee profiles, documents, conversation, speech, and agent requests."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class ConversationStatus(str, Enum):
    """Conversation status."""

    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MessageType(str, Enum):
    """Message type."""

    TEXT = "text"
    SPEECH = "speech"
    SYSTEM = "system"


class EmployeeProfileBase(BaseModel):
    """Base employee profile fields."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    experience_years: Optional[int] = None
    skills: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    education: Optional[List[Dict[str, Any]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    preferred_roles: Optional[List[str]] = None
    profile_completeness_score: int = Field(default=0, ge=0, le=100)
    tags: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class EmployeeProfileCreate(EmployeeProfileBase):
    """Schema for creating an employee profile."""

    document_id: Optional[UUID] = None


class EmployeeProfileUpdate(EmployeeProfileBase):
    """Schema for updating an employee profile (all optional)."""

    pass


class EmployeeProfile(EmployeeProfileBase):
    """Full employee profile with DB fields."""

    id: UUID
    document_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeDocumentBase(BaseModel):
    """Base document schema."""

    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    raw_text: Optional[str] = None
    source: Optional[str] = None  # e.g. upload, conversation


class EmployeeDocumentCreate(EmployeeDocumentBase):
    """Create document (e.g. from upload)."""

    pass


class EmployeeDocument(EmployeeDocumentBase):
    """Document with DB fields."""

    id: UUID
    employee_profile_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Conversation API Schemas ---


class ConversationStartRequest(BaseModel):
    """Request to start a new employee conversation."""

    employee_name: Optional[str] = Field(None, max_length=255)
    employee_email: Optional[EmailStr] = None
    employee_phone: Optional[str] = Field(None, max_length=50)
    source_channel: str = Field(default="web", max_length=50)
    initial_context: Optional[Dict[str, Any]] = Field(default=None)


class ConversationStartResponse(BaseModel):
    """Response when starting a conversation."""

    conversation_id: UUID
    employee_profile_id: Optional[UUID] = None
    greeting_message: str
    audio_url: Optional[str] = None


class MessageRequest(BaseModel):
    """Request to send a message in conversation."""

    message: str = Field(..., min_length=1, max_length=5000)
    message_type: MessageType = MessageType.TEXT


class ExtractionUpdate(BaseModel):
    """Extraction update from a message."""

    field_name: str
    field_value: Any
    confidence: float = Field(ge=0.0, le=1.0)


class MessageResponse(BaseModel):
    """Response after sending a message."""

    conversation_id: UUID
    message_id: UUID
    employee_profile_id: Optional[UUID] = None
    assistant_message: str
    audio_url: Optional[str] = None
    extraction_updates: Optional[List[ExtractionUpdate]] = None
    profile_completeness: int = Field(ge=0, le=100)
    missing_fields: List[str]
    can_complete: bool


class ConversationStatusResponse(BaseModel):
    """Response for conversation status."""

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
    employee_profile_id: Optional[UUID] = None
    status: ConversationStatus
    profile_completeness: int
    summary: str


class ConversationMessage(BaseModel):
    """Single message in conversation history."""

    id: UUID
    role: str
    content: str
    message_type: str = "text"
    created_at: datetime


class ConversationHistory(BaseModel):
    """Full conversation history."""

    conversation_id: UUID
    messages: List[ConversationMessage]


# --- Speech API Schemas ---


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
