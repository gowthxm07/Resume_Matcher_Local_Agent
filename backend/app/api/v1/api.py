"""
API v1 router aggregator.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    ingestion,
    agents,
    database,
    analysis,
    projects,
    optimization,
    local_agent,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(ingestion.router)
api_router.include_router(agents.router)
api_router.include_router(database.router)
api_router.include_router(analysis.router)
api_router.include_router(projects.router)
api_router.include_router(optimization.router)
api_router.include_router(local_agent.router)

