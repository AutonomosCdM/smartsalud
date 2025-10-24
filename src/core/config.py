"""
Application configuration using Pydantic Settings.

All configuration loaded from environment variables with validation.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Literal


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="smartSalud_V2", description="Application name")
    app_env: Literal["development", "production", "test"] = Field(
        default="development",
        description="Environment"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Log level"
    )

    # Database
    database_url: str = Field(
        ...,
        description="PostgreSQL connection URL (async)",
        pattern=r"^postgresql\+asyncpg://.*"
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )

    # Groq API
    groq_api_key: str = Field(
        ...,
        description="Groq API key",
        pattern=r"^gsk_.*"
    )
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model to use"
    )
    groq_timeout: float = Field(
        default=5.0,
        description="Groq API timeout in seconds",
        gt=0,
        le=30
    )

    # Twilio
    twilio_account_sid: str = Field(..., pattern=r"^AC[a-f0-9]{32}$")
    twilio_auth_token: str = Field(..., min_length=32)
    twilio_whatsapp_number: str = Field(..., pattern=r"^whatsapp:\+\d+$")
    twilio_content_sid_confirmation: str = Field(
        ...,
        pattern=r"^HX[a-f0-9]{32}$",
        description="Twilio Content Template SID for confirmations"
    )

    # Google Calendar
    google_calendar_credentials_file: str = Field(
        default="token.json",
        description="Path to Google Calendar OAuth2 credentials"
    )
    google_calendar_scopes: str = Field(
        default="https://www.googleapis.com/auth/calendar",
        description="Google Calendar API scopes"
    )

    # Scheduler
    reminder_schedule_hour: int = Field(default=9, ge=0, le=23)
    reminder_schedule_minute: int = Field(default=0, ge=0, le=59)
    reminder_days_ahead: int = Field(
        default=1,
        ge=0,
        le=7,
        description="Days ahead to send reminders"
    )

    # Monitoring
    enable_dashboard: bool = Field(default=True)
    dashboard_path: str = Field(default="/dashboard")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure async driver is used."""
        if "+asyncpg" not in v:
            raise ValueError("Database URL must use asyncpg driver (postgresql+asyncpg://...)")
        return v


# Global settings instance (lazy loaded)
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get settings instance (lazy loaded)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
