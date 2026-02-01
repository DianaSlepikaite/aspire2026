"""Custom exceptions for the Employee Conversation Service."""

from typing import Optional, Any, Dict


class ServiceError(Exception):
    """Base exception for all service errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ConfigurationError(ServiceError):
    """Raised when there's a configuration issue."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=500)


class StorageError(ServiceError):
    """Raised when storage operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=500)


class DocumentNotFoundError(ServiceError):
    """Raised when an employee document is not found."""

    def __init__(self, document_id: str):
        super().__init__(
            message=f"Document not found: {document_id}",
            details={"document_id": document_id},
            status_code=404,
        )


class EmployeeProfileNotFoundError(ServiceError):
    """Raised when an employee profile is not found."""

    def __init__(self, profile_id: str):
        super().__init__(
            message=f"Employee profile not found: {profile_id}",
            details={"profile_id": profile_id},
            status_code=404,
        )


class ConversationNotFoundError(ServiceError):
    """Raised when a conversation is not found."""

    def __init__(self, conversation_id: str):
        super().__init__(
            message=f"Conversation not found: {conversation_id}",
            details={"conversation_id": conversation_id},
            status_code=404,
        )


class ConversationError(ServiceError):
    """Raised when a conversation operation fails."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
    ):
        super().__init__(message, details, status_code)


class SpeechServiceError(ServiceError):
    """Raised when speech (STT/TTS) fails."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 502,
    ):
        super().__init__(message, details, status_code)


class AudioProcessingError(ServiceError):
    """Raised when audio validation or processing fails."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
    ):
        super().__init__(message, details, status_code)
