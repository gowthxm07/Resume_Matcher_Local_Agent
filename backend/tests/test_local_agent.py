"""
Tests for CareerCrew Local Agent Endpoints, Deterministic Compatibility Service,
Security Invariants, and Capabilities Negotiation.
"""

import sys
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.schemas.local_agent import CompatibilityStatus, CompatibilityCheckItem
from app.services.compatibility_service import CompatibilityService, compatibility_service
from app.core.config import settings, Settings


def test_local_agent_health_endpoint(client: TestClient):
    """Verify GET /api/local-agent/health returns correct structure without exposing secrets."""
    res = client.get("/api/local-agent/health")
    assert res.status_code == 200
    data = res.json()
    assert data["agent"] == "careercrew-local-agent"
    assert data["status"] == "ready"
    assert data["version"] == "1.0.0"
    assert data["api_version"] == "1"
    assert data["local_only"] is True

    # Security check: Ensure no sensitive paths, environment secrets, or credentials
    serialized = str(data).lower()
    assert "password" not in serialized
    assert "secret" not in serialized
    assert "token" not in serialized
    assert "c:\\" not in serialized
    assert "/home/" not in serialized
    assert "api_key" not in serialized


def test_local_agent_capabilities_endpoint(client: TestClient):
    """Verify GET /api/local-agent/capabilities accurately exposes implemented vs deferred features."""
    res = client.get("/api/local-agent/capabilities")
    assert res.status_code == 200
    data = res.json()
    assert data["analysis"] is True
    assert data["multi_agent"] is True
    assert data["evidence_scanning"] is True
    assert data["resume_optimization"] is True
    assert data["fact_checking"] is True
    assert data["ats_validation"] is True
    assert data["github_import"] is True
    # Interview intelligence must be strictly deferred (Phase 6 boundary)
    assert data["interview_intelligence"] is False


@pytest.mark.asyncio
async def test_compatibility_service_all_ready():
    """Verify compatibility service returns ready=True when all components are present."""
    service = CompatibilityService()

    dummy_ollama_item = CompatibilityCheckItem(
        name="Ollama",
        status=CompatibilityStatus.READY,
        required=True,
        detected_version="reachable",
        required_version=">= 0.1.0",
        message="Local Ollama server is running.",
        setup_route="/get-started#ollama",
    )

    with patch.object(
        service,
        "check_ollama",
        AsyncMock(return_value=(dummy_ollama_item, ["llama3.2:3b", "nomic-embed-text:latest"])),
    ):
        report = await service.get_compatibility_report()
        # Verify check count and names
        names = [c.name for c in report.checks]
        assert "Ollama" in names
        assert "Llama 3.2:3B" in names
        assert "nomic-embed-text" in names
        assert "Git" in names
        assert "SQLite" in names
        assert "ChromaDB" in names
        assert "CrewAI" in names
        assert "Python" in names
        assert "FastAPI" in names
        assert "CareerCrew Local Agent" in names
        assert "Local Ports" in names
        assert report.ready is True


@pytest.mark.asyncio
async def test_compatibility_service_ollama_missing():
    """Verify system is NOT ready when Ollama server is unreachable."""
    service = CompatibilityService()

    with patch("httpx.AsyncClient.get", side_effect=Exception("Connection refused")):
        ollama_check, models = await service.check_ollama()
        assert ollama_check.status == CompatibilityStatus.MISSING
        assert models == []

        report = await service.get_compatibility_report()
        assert report.ready is False
        ollama_item = next(c for c in report.checks if c.name == "Ollama")
        assert ollama_item.status == CompatibilityStatus.MISSING


def test_compatibility_llm_model_missing():
    """Verify Llama 3.2:3b check returns MISSING when model is absent from Ollama tags."""
    service = CompatibilityService()
    # Only other models present
    check = service.check_llm_model(["mistral:latest", "phi3:mini"])
    assert check.status == CompatibilityStatus.MISSING
    assert check.required is True
    assert "ollama pull llama3.2:3b" in check.message


def test_compatibility_llm_model_present():
    """Verify Llama 3.2:3b check returns READY when model tag is present."""
    service = CompatibilityService()
    check = service.check_llm_model(["llama3.2:3b", "nomic-embed-text"])
    assert check.status == CompatibilityStatus.READY
    assert "installed" in check.message.lower()


def test_compatibility_embedding_model_missing():
    """Verify nomic-embed-text check returns MISSING when model is absent."""
    service = CompatibilityService()
    check = service.check_embedding_model(["llama3.2:3b"])
    assert check.status == CompatibilityStatus.MISSING
    assert check.required is True
    assert "nomic-embed-text" in check.message


def test_compatibility_embedding_model_present():
    """Verify nomic-embed-text check returns READY when tag is present."""
    service = CompatibilityService()
    check = service.check_embedding_model(["llama3.2:3b", "nomic-embed-text:latest"])
    assert check.status == CompatibilityStatus.READY


def test_compatibility_git_missing():
    """Verify Git check returns MISSING when git is not on PATH."""
    service = CompatibilityService()
    with patch("shutil.which", return_value=None):
        check = service.check_git()
        assert check.status == CompatibilityStatus.MISSING
        assert check.required is True


def test_compatibility_git_present():
    """Verify Git check returns READY when git CLI is operational."""
    service = CompatibilityService()
    check = service.check_git()
    assert check.status in (CompatibilityStatus.READY, CompatibilityStatus.MISSING)
    if check.status == CompatibilityStatus.READY:
        assert check.detected_version is not None


def test_compatibility_crewai_check():
    """Verify CrewAI runtime detection."""
    service = CompatibilityService()
    check = service.check_crewai()
    assert check.status == CompatibilityStatus.READY
    assert check.name == "CrewAI"
    assert check.required is True


def test_compatibility_sqlite_check():
    """Verify SQLite non-destructive read test."""
    service = CompatibilityService()
    check = service.check_sqlite()
    assert check.status == CompatibilityStatus.READY
    assert check.name == "SQLite"


def test_compatibility_chromadb_check():
    """Verify ChromaDB runtime detection."""
    service = CompatibilityService()
    check = service.check_chromadb()
    assert check.status == CompatibilityStatus.READY
    assert check.name == "ChromaDB"


def test_cors_wildcard_prohibited():
    """Verify that wildcard '*' CORS is strictly rejected by security validation."""
    with pytest.raises(ValueError, match="Wildcard '\\*' CORS origin is strictly prohibited"):
        Settings(CORS_ORIGINS=["*"])


def test_cors_valid_origins_accepted():
    """Verify valid CORS origins list is parsed and preserved."""
    test_settings = Settings(
        CORS_ORIGINS=["http://localhost:3000", "https://careercrew.vercel.app"]
    )
    assert "https://careercrew.vercel.app" in test_settings.CORS_ORIGINS
    assert "http://localhost:3000" in test_settings.CORS_ORIGINS


def test_localhost_binding_default():
    """Verify default server binding is strictly 127.0.0.1 (localhost)."""
    assert settings.HOST == "127.0.0.1"


def test_compatibility_endpoint_integration(client: TestClient):
    """Verify GET /api/local-agent/compatibility returns well-formed response."""
    res = client.get("/api/local-agent/compatibility")
    assert res.status_code == 200
    data = res.json()
    assert "ready" in data
    assert isinstance(data["ready"], bool)
    assert "checks" in data
    assert len(data["checks"]) >= 10
    assert data["agent_version"] == "1.0.0"
    assert "timestamp" in data
