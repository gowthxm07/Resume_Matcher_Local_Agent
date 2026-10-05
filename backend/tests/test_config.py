"""
Unit tests for configuration loading and strict local-only policy enforcement.
"""

import pytest
from pydantic import ValidationError
from app.core.config import Settings, settings


def test_default_config_loading():
    """Verify default configurations load with expected local values."""
    assert settings.APP_NAME == "CareerCrew Backend"
    assert settings.LLM_PROVIDER == "ollama"
    assert "llama3.2" in settings.OLLAMA_MODEL
    assert settings.DATABASE_URL.startswith("sqlite")
    assert ".pdf" in settings.ALLOWED_FILE_EXTENSIONS
    assert settings.UPLOAD_MAX_BYTES > 0


def test_reject_cloud_llm_providers():
    """Verify that cloud LLM providers (OpenAI, Anthropic, Gemini, Azure) are strictly rejected."""
    prohibited_providers = ["openai", "anthropic", "gemini", "azure", "bedrock", "cohere"]

    for provider in prohibited_providers:
        with pytest.raises(ValidationError):
            Settings(LLM_PROVIDER=provider)


def test_allow_local_providers():
    """Verify local providers are accepted."""
    s = Settings(LLM_PROVIDER="ollama")
    assert s.LLM_PROVIDER == "ollama"
