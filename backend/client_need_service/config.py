"""
Configuration management for the Client Need Service Agent.
Uses Pydantic Settings for type-safe configuration from environment variables.
"""

from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str = Field(
        default="", description="Azure OpenAI endpoint URL"
    )
    AZURE_OPENAI_KEY: str = Field(default="", description="Azure OpenAI API key")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = Field(
        default="gpt-4", description="Azure OpenAI deployment/model name"
    )
    AZURE_OPENAI_API_VERSION: str = Field(
        default="2024-02-01", description="Azure OpenAI API version"
    )
    AZURE_OPENAI_MAX_TOKENS: int = Field(
        default=4096, description="Maximum tokens for OpenAI responses"
    )
    AZURE_OPENAI_TEMPERATURE: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Temperature for OpenAI responses"
    )

    # Azure Speech Service Configuration
    AZURE_SPEECH_KEY: str = Field(
        default="", description="Azure Speech Service API key"
    )
    AZURE_SPEECH_REGION: str = Field(
        default="eastus", description="Azure Speech Service region"
    )
    AZURE_SPEECH_LANGUAGE: str = Field(
        default="en-US", description="Default language for speech recognition"
    )
    AZURE_SPEECH_VOICE_NAME: str = Field(
        default="en-US-JennyNeural", description="Default voice for text-to-speech"
    )

    # Database Configuration
    DB1: str = Field(
        default="",
        description="PostgreSQL connection URL (postgresql://user:pass@host:port/dbname)",
    )
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=5432, description="Database port")
    DB_NAME: str = Field(default="client_needs_db", description="Database name")
    DB_USER: str = Field(default="postgres", description="Database user")
    DB_PASSWORD: str = Field(default="", description="Database password")

    # Application Configuration
    APP_ENV: str = Field(
        default="development",
        description="Application environment (development, staging, production)",
    )
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or text)")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 route prefix")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )

    # Conversation Settings
    MAX_CONVERSATION_MESSAGES: int = Field(
        default=50, ge=1, description="Maximum messages to keep in conversation history"
    )
    CONVERSATION_TIMEOUT_MINUTES: int = Field(
        default=30, ge=1, description="Conversation timeout in minutes"
    )
    MIN_PROFILE_COMPLETENESS_FOR_COMPLETION: int = Field(
        default=70,
        ge=0,
        le=100,
        description="Minimum profile completeness score required for completion",
    )

    # Feature Flags
    ENABLE_SPEECH_TO_TEXT: bool = Field(
        default=True, description="Enable speech-to-text functionality"
    )
    ENABLE_TEXT_TO_SPEECH: bool = Field(
        default=True, description="Enable text-to-speech functionality"
    )
    ENABLE_STREAMING_RESPONSES: bool = Field(
        default=False, description="Enable streaming responses from OpenAI"
    )

    # Storage Configuration
    AUDIO_STORAGE_PATH: str = Field(
        default="/tmp/audio", description="Path for temporary audio file storage"
    )
    MAX_AUDIO_FILE_SIZE_MB: int = Field(
        default=10, ge=1, description="Maximum audio file size in MB"
    )
    MIN_AUDIO_FILE_SIZE_BYTES: int = Field(
        default=1000,
        ge=0,
        description="Minimum audio file size in bytes (reject empty/tiny files)",
    )
    ALLOWED_AUDIO_EXTENSIONS: List[str] = Field(
        default=["wav", "mp3", "ogg", "m4a"],
        description="Allowed audio file extensions for upload/transcribe",
    )
    ALLOWED_AUDIO_MIME_TYPES: List[str] = Field(
        default=[
            "audio/wav",
            "audio/wave",
            "audio/mpeg",
            "audio/mp3",
            "audio/ogg",
            "audio/mp4",
            "audio/x-m4a",
        ],
        description="Allowed MIME types for audio upload/transcribe",
    )
    SPEECH_STREAM_SESSION_TIMEOUT_MINUTES: int = Field(
        default=30,
        ge=1,
        le=120,
        description="Streaming speech session idle timeout in minutes",
    )

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.APP_ENV.lower() == "development"

    def has_azure_openai_credentials(self) -> bool:
        """Check if Azure OpenAI credentials are configured."""
        return bool(self.AZURE_OPENAI_ENDPOINT and self.AZURE_OPENAI_KEY)

    def has_azure_speech_credentials(self) -> bool:
        """Check if Azure Speech credentials are configured."""
        return bool(self.AZURE_SPEECH_KEY and self.AZURE_SPEECH_REGION)

    def has_database_credentials(self) -> bool:
        """Check if database credentials are configured."""
        return bool(self.DB1 or (self.DB_HOST and self.DB_NAME))

    def get_database_url(self) -> str:
        """Get database connection URL."""
        if self.DB1:
            return self.DB1

        # Build URL from individual components
        password_part = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return f"postgresql://{self.DB_USER}{password_part}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def get_max_audio_size_bytes(self) -> int:
        """Maximum allowed audio file size in bytes for upload/transcribe."""
        return self.MAX_AUDIO_FILE_SIZE_MB * 1024 * 1024


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings instance."""
    return settings
