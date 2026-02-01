"""Schemas for employee profiles, documents, and agent requests."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


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
