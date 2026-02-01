"""Configuration for Employee Conversation Service."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings from environment."""

    APP_ENV: str = Field(default="development", description="Environment")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API prefix")
    LOG_LEVEL: str = Field(default="INFO", description="Log level")

    # Database Configuration (PostgreSQL)
    # Employee service prefers EMPLOYEE_* vars so it can use a different DB on the same host.
    # If unset, falls back to shared DATABASE_URL / DB_* (e.g. same .env as client service).
    EMPLOYEE_DATABASE_URL: str = Field(
        default="",
        description="PostgreSQL URL for employee service (optional; overrides EMPLOYEE_DB_* / shared DB_*)",
    )
    EMPLOYEE_DB_HOST: str = Field(
        default="", description="Employee DB host (default: DB_HOST)"
    )
    EMPLOYEE_DB_PORT: int = Field(
        default=0, description="Employee DB port (0 = use DB_PORT)"
    )
    EMPLOYEE_DB_NAME: str = Field(
        default="",
        description="Employee DB name (default: employee_conversation_db or DB_NAME)",
    )
    EMPLOYEE_DB_USER: str = Field(
        default="", description="Employee DB user (default: DB_USER)"
    )
    EMPLOYEE_DB_PASSWORD: str = Field(
        default="", description="Employee DB password (default: DB_PASSWORD)"
    )

    DATABASE_URL: str = Field(
        default="",
        description="Shared PostgreSQL URL (used if EMPLOYEE_* not set)",
    )
    DB_HOST: str = Field(default="localhost", description="Shared database host")
    DB_PORT: int = Field(default=5432, description="Shared database port")
    DB_NAME: str = Field(default="client_needs_db", description="Shared database name")
    DB_USER: str = Field(default="postgres", description="Shared database user")
    DB_PASSWORD: str = Field(default="", description="Shared database password")

    # Azure OpenAI (for extraction/summary)
    AZURE_OPENAI_ENDPOINT: str = Field(default="", description="Azure OpenAI endpoint")
    AZURE_OPENAI_KEY: str = Field(default="", description="Azure OpenAI key")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = Field(
        default="gpt-4", description="Deployment name"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    def has_database_credentials(self) -> bool:
        """Check if database credentials are configured (employee or shared)."""
        return bool(
            self.EMPLOYEE_DATABASE_URL
            or (self.EMPLOYEE_DB_NAME and (self.EMPLOYEE_DB_HOST or self.DB_HOST))
            or self.DATABASE_URL
            or (self.DB_HOST and self.DB_NAME)
        )

    def get_database_url(self) -> str:
        """Get database connection URL (employee-specific if set, else shared)."""
        if self.EMPLOYEE_DATABASE_URL:
            return self.EMPLOYEE_DATABASE_URL
        # If no employee-specific DB name, use shared DATABASE_URL (same DB as client)
        if not self.EMPLOYEE_DB_NAME and self.DATABASE_URL:
            return self.DATABASE_URL
        host = self.EMPLOYEE_DB_HOST or self.DB_HOST
        port = self.EMPLOYEE_DB_PORT if self.EMPLOYEE_DB_PORT else self.DB_PORT
        name = self.EMPLOYEE_DB_NAME or "employee_conversation_db"
        user = self.EMPLOYEE_DB_USER or self.DB_USER
        password = self.EMPLOYEE_DB_PASSWORD or self.DB_PASSWORD
        password_part = f":{password}" if password else ""
        return f"postgresql://{user}{password_part}@{host}:{port}/{name}"


def get_settings() -> Settings:
    """Return application settings."""
    return Settings()
