"""
Agents blueprint endpoint for CareerCrew.
Surfaces the planned multi-agent architecture and role descriptions to the frontend.
"""

from typing import Dict, Any
from fastapi import APIRouter
from app.agents.orchestration import orchestrator

router = APIRouter()


@router.get("/agents/architecture", tags=["Multi-Agent System"])
async def get_agent_architecture() -> Dict[str, Any]:
    """
    Retrieve specifications for all 9 planned CrewAI specialized agents,
    pipeline execution stages, and zero-hallucination verification loops.
    """
    return orchestrator.get_system_architecture_summary()
