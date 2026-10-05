"""
Pydantic schemas for health and system introspection endpoints.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Basic health check response."""
    status: str = Field(default="ok", description="Basic health status string")
    service: str = Field(default="careercrew-backend", description="Service name")
    version: str = Field(default="0.1.0", description="Backend version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp")


class OllamaStatus(BaseModel):
    """Ollama local LLM connectivity status."""
    reachable: bool = Field(description="Whether the Ollama server is reachable")
    base_url: str = Field(description="Configured Ollama base URL")
    configured_model: str = Field(description="Primary local LLM model name")
    model_exists: bool = Field(description="Whether the primary model is installed locally")
    embed_model: str = Field(description="Configured local embedding model name")
    embed_model_exists: bool = Field(description="Whether the embedding model is installed locally")
    latency_ms: Optional[float] = Field(default=None, description="Ping/query latency in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if unreachable")


class DatabaseStatus(BaseModel):
    """SQLite persistent storage status."""
    connected: bool = Field(description="Whether SQLite database is accessible")
    engine: str = Field(default="sqlite", description="Database engine")
    status: str = Field(description="healthy / degraded / unhealthy")
    tables: List[str] = Field(default_factory=list, description="Existing tables in database")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class VectorStoreStatus(BaseModel):
    """Local vector store status."""
    status: str = Field(description="healthy / degraded / uninitialized")
    store_type: str = Field(description="Vector store engine (e.g., chroma)")
    storage_path: str = Field(description="Local path where vectors are persisted")
    collection_count: int = Field(default=0, description="Number of vector collections")
    error: Optional[str] = Field(default=None, description="Error details if any")


class SystemStatusResponse(BaseModel):
    """Comprehensive system diagnostics for local-first architecture."""
    backend_status: str = Field(default="ok")
    version: str = Field(default="0.1.0")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    local_only_verified: bool = Field(
        default=True,
        description="True indicates zero cloud LLM API dependencies configured"
    )
    ollama: OllamaStatus
    database: DatabaseStatus
    vector_store: VectorStoreStatus


class OllamaTestPromptRequest(BaseModel):
    """Request payload for testing local LLM inference."""
    prompt: str = Field(default="Respond with exactly 'CareerCrew Local LLM operational.' in 5 words or less.")


class OllamaTestPromptResponse(BaseModel):
    """Response payload for testing local LLM inference."""
    success: bool
    model: str
    response_text: str
    latency_ms: float
    error: Optional[str] = None
