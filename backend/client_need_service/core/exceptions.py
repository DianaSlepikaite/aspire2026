"""
Custom exceptions for the Client Need Service Agent.
"""

from typing import Optional, Any, Dict


class ServiceError(Exception):
    """Base exception for all service errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ConfigurationError(ServiceError):
    """Raised when there's a configuration issue."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=500)


class AzureOpenAIError(ServiceError):
    """Raised when Azure OpenAI service encounters an error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=502)


class SpeechServiceError(ServiceError):
    """Raised when Azure Speech service encounters an error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=502)


class StorageError(ServiceError):
    """Raised when database/storage operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=500)


class ConversationError(ServiceError):
    """Raised when conversation operations fail."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=400)


class ConversationNotFoundError(ServiceError):
    """Raised when a conversation is not found."""

    def __init__(self, conversation_id: str):
        super().__init__(
            message=f"Conversation not found: {conversation_id}",
            details={"conversation_id": conversation_id},
            status_code=404
        )


class ClientNeedNotFoundError(ServiceError):
    """Raised when a client need profile is not found."""

    def __init__(self, client_need_id: str):
        super().__init__(
            message=f"Client need not found: {client_need_id}",
            details={"client_need_id": client_need_id},
            status_code=404
        )


class ConversationTimeoutError(ServiceError):
    """Raised when a conversation times out."""

    def __init__(self, conversation_id: str, timeout_minutes: int):
        super().__init__(
            message=f"Conversation timed out after {timeout_minutes} minutes",
            details={
                "conversation_id": conversation_id,
                "timeout_minutes": timeout_minutes
            },
            status_code=408
        )


class AudioProcessingError(ServiceError):
    """Raised when audio processing fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=400)


class ValidationError(ServiceError):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details, status_code=422)


class RateLimitError(ServiceError):
    """Raised when rate limits are exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(message, details, status_code=429)
