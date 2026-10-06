"""
Local Agent API endpoints for CareerCrew.
Enables Vercel Dashboard connection discovery, deterministic compatibility checks,
and feature negotiation without exposing private user data, tokens, or system paths.
"""

from fastapi import APIRouter
from app.schemas.local_agent import (
    AgentHealthResponse,
    CompatibilityResponse,
    AgentCapabilitiesResponse,
)
from app.services.compatibility_service import compatibility_service


router = APIRouter(prefix="/local-agent", tags=["Local Agent"])


@router.get("/health", response_model=AgentHealthResponse)
async def get_local_agent_health() -> AgentHealthResponse:
    """
    Standardized health check for local agent runtime.
    Invoked by Vercel-hosted dashboard to verify localhost connectivity.
    Guaranteed zero filesystem paths, credentials, or environment secrets exposed.
    """
    return compatibility_service.get_health()


@router.get("/compatibility", response_model=CompatibilityResponse)
async def get_local_agent_compatibility() -> CompatibilityResponse:
    """
    Run deterministic local system compatibility diagnostics.
    Detects Python, FastAPI, CrewAI, Ollama reachability, Llama 3.2:3b model,
    nomic-embed-text model, Git CLI, SQLite, ChromaDB, and local port configuration.
    """
    return await compatibility_service.get_compatibility_report()


@router.get("/capabilities", response_model=AgentCapabilitiesResponse)
async def get_local_agent_capabilities() -> AgentCapabilitiesResponse:
    """
    Retrieve active feature capabilities for protocol negotiation with the dashboard.
    Reflects true implemented subsystems (interview intelligence is strictly false).
    """
    return compatibility_service.get_capabilities()
