"""
Unit tests for the dedicated Ollama service abstraction.
Uses mock tests for deterministic testing and live tests when local Ollama is available.
Zero external cloud APIs are ever contacted.
"""

import pytest
from unittest.mock import AsyncMock, patch
import httpx
from app.services.ollama_service import OllamaService
from app.core.config import settings


@pytest.mark.asyncio
async def test_ollama_service_configuration():
    """Verify Ollama service is configured with local defaults."""
    service = OllamaService()
    assert service.base_url == settings.OLLAMA_BASE_URL.rstrip("/")
    assert service.model == settings.OLLAMA_MODEL
    assert "openai" not in service.base_url
    assert "anthropic" not in service.base_url


@pytest.mark.asyncio
async def test_ollama_availability_mock_success():
    """Verify availability check correctly parses successful response."""
    service = OllamaService()
    mock_resp = httpx.Response(200, json={"models": [{"name": "llama3.2:3b"}]})

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        status = await service.check_availability()
        assert status["reachable"] is True
        assert status["error"] is None
        assert status["latency_ms"] is not None


@pytest.mark.asyncio
async def test_ollama_availability_mock_connection_error():
    """Verify availability check handles connection failure gracefully."""
    service = OllamaService()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.ConnectError("Connection refused")
        status = await service.check_availability()
        assert status["reachable"] is False
        assert "Could not connect" in status["error"]


@pytest.mark.asyncio
async def test_ollama_model_exists_mock():
    """Verify model existence check with mocked model list."""
    service = OllamaService()
    mock_resp = httpx.Response(200, json={"models": [{"name": "llama3.2:3b"}, {"name": "nomic-embed-text:latest"}]})

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        assert await service.model_exists("llama3.2:3b") is True
        assert await service.model_exists("gpt-4") is False


@pytest.mark.asyncio
async def test_ollama_generate_mock_success():
    """Verify generate handles prompt completion correctly."""
    service = OllamaService()
    mock_resp = httpx.Response(
        200,
        json={
            "response": "CareerCrew Local LLM operational.",
            "total_duration": 1200000,
            "eval_count": 5,
        },
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        res = await service.generate(prompt="Ping")
        assert res["success"] is True
        assert res["response_text"] == "CareerCrew Local LLM operational."
        assert res["eval_count"] == 5
        assert res["latency_ms"] > 0


@pytest.mark.asyncio
async def test_live_ollama_integration_if_available():
    """
    Live integration test against running local Ollama instance.
    Skips cleanly if Ollama daemon is not currently active on the host.
    """
    service = OllamaService()
    check = await service.check_availability()
    if not check["reachable"]:
        pytest.skip("Local Ollama server is not running, skipping live integration test.")

    model_present = await service.model_exists(settings.OLLAMA_MODEL)
    if not model_present:
        pytest.skip(f"Configured model {settings.OLLAMA_MODEL} not loaded in local Ollama.")

    # Live generation test with a 1-word answer prompt
    res = await service.generate(
        prompt="Say 'pong'",
        max_tokens=5,
    )
    assert res["success"] is True
    assert len(res["response_text"]) > 0
    assert res["latency_ms"] > 0
