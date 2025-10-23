"""
Unit tests for configuration.
"""
import pytest
from src.core.config import Settings


class TestConfig:
    """Test configuration loading and validation."""

    def test_settings_load(self):
        """Test that settings load correctly."""
        settings = Settings()
        assert settings.app_name == "smartSalud_V2"
        assert settings.groq_timeout > 0
        assert settings.groq_timeout <= 30

    def test_database_url_validation(self):
        """Test database URL validation requires asyncpg."""
        # This will use the actual env var
        settings = Settings()
        assert "+asyncpg" in settings.database_url

    def test_groq_api_key_pattern(self):
        """Test Groq API key pattern validation."""
        settings = Settings()
        assert settings.groq_api_key.startswith("gsk_")
