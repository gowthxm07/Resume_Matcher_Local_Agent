"""
API v1 router aggregator.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import health, ingestion, agents, database

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(ingestion.router)
api_router.include_router(agents.router)
api_router.include_router(database.router)
