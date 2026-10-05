"""
Health, system introspection, and Ollama verification endpoints.
Provides genuine diagnostics of local-only services with no fake statuses.
"""

from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.core.logging import logger
from app.db.init_db import check_db_health
from app.services.ollama_service import ollama_service
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.schemas.health import (
    HealthResponse,
    SystemStatusResponse,
    OllamaStatus,
    DatabaseStatus,
    VectorStoreStatus,
    OllamaTestPromptRequest,
    OllamaTestPromptResponse,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def get_health() -> HealthResponse:
    """Basic health check endpoint."""
    return HealthResponse(
        status="ok",
        service="careercrew-backend",
        version=settings.APP_VERSION,
    )


@router.get("/system/status", response_model=SystemStatusResponse, tags=["System Diagnostics"])
async def get_system_status() -> SystemStatusResponse:
    """
    Introspect full system health:
    - Ollama server reachability and model availability
    - SQLite database table initialization
    - Local Chroma vector store status
    - Local-only configuration verification
    """
    # 1. Inspect Ollama local LLM & Embedding Model
    ollama_check = await ollama_service.check_availability()
    primary_model_exists = False
    embed_model_exists = False

    if ollama_check["reachable"]:
        primary_model_exists = await ollama_service.model_exists(settings.OLLAMA_MODEL)
        embed_check = await embedding_service.check_availability()
        embed_model_exists = embed_check["available"]

    ollama_status = OllamaStatus(
        reachable=ollama_check["reachable"],
        base_url=settings.OLLAMA_BASE_URL,
        configured_model=settings.OLLAMA_MODEL,
        model_exists=primary_model_exists,
        embed_model=settings.OLLAMA_EMBED_MODEL,
        embed_model_exists=embed_model_exists,
        latency_ms=ollama_check["latency_ms"],
        error=ollama_check["error"],
    )

    # 2. Inspect SQLite Database
    db_health = check_db_health()
    db_status = DatabaseStatus(
        connected=db_health.get("connected", False),
        engine=db_health.get("engine", "sqlite"),
        status=db_health.get("status", "unknown"),
        tables=db_health.get("tables", []),
        error=db_health.get("error"),
    )

    # 3. Inspect Local Vector Store
    vs_stats = vector_store.get_stats()
    vs_status = VectorStoreStatus(
        status=vs_stats.get("status", "unknown"),
        store_type=vs_stats.get("store_type", "chroma"),
        storage_path=vs_stats.get("storage_path", str(settings.VECTOR_STORE_DIR)),
        collection_count=vs_stats.get("collection_count", 0),
        error=vs_stats.get("error"),
    )

    overall_backend = "ok"
    if not db_status.connected:
        overall_backend = "degraded"

    return SystemStatusResponse(
        backend_status=overall_backend,
        version=settings.APP_VERSION,
        local_only_verified=True,
        ollama=ollama_status,
        database=db_status,
        vector_store=vs_status,
    )


@router.post("/ollama/test", response_model=OllamaTestPromptResponse, tags=["Local LLM"])
async def test_ollama_completion(request: OllamaTestPromptRequest) -> OllamaTestPromptResponse:
    """
    Test endpoint that sends a lightweight prompt to the local Ollama LLM
    and measures local inference latency without any external cloud calls.
    """
    # First verify Ollama is reachable
    avail = await ollama_service.check_availability()
    if not avail["reachable"]:
        raise HTTPException(
            status_code=503,
            detail=f"Local Ollama server is unreachable: {avail.get('error')}",
        )

    # Verify model exists
    exists = await ollama_service.model_exists(settings.OLLAMA_MODEL)
    if not exists:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{settings.OLLAMA_MODEL}' not found on local Ollama instance.",
        )

    res = await ollama_service.generate(
        prompt=request.prompt,
        model=settings.OLLAMA_MODEL,
        temperature=0.1,
        max_tokens=60,
    )

    return OllamaTestPromptResponse(
        success=res["success"],
        model=res["model"],
        response_text=res["response_text"],
        latency_ms=res["latency_ms"],
        error=res.get("error"),
    )
