"""
Schemas package exports for CareerCrew.
"""

from app.schemas.health import (
    HealthResponse,
    OllamaStatus,
    DatabaseStatus,
    VectorStoreStatus,
    SystemStatusResponse,
    OllamaTestPromptRequest,
    OllamaTestPromptResponse,
)
from app.schemas.ingestion import (
    NormalizedDocument,
    DocumentMetadata,
    IngestionResponse,
)
from app.schemas.entities import (
    ResumeBase,
    ResumeCreate,
    ResumeResponse,
    JobDescriptionBase,
    JobDescriptionCreate,
    JobDescriptionResponse,
    ProjectBase,
    ProjectCreate,
    ProjectResponse,
    ApplicationBase,
    ApplicationCreate,
    ApplicationResponse,
    AnalysisRunBase,
    AnalysisRunCreate,
    AnalysisRunResponse,
)

__all__ = [
    "HealthResponse",
    "OllamaStatus",
    "DatabaseStatus",
    "VectorStoreStatus",
    "SystemStatusResponse",
    "OllamaTestPromptRequest",
    "OllamaTestPromptResponse",
    "NormalizedDocument",
    "DocumentMetadata",
    "IngestionResponse",
    "ResumeBase",
    "ResumeCreate",
    "ResumeResponse",
    "JobDescriptionBase",
    "JobDescriptionCreate",
    "JobDescriptionResponse",
    "ProjectBase",
    "ProjectCreate",
    "ProjectResponse",
    "ApplicationBase",
    "ApplicationCreate",
    "ApplicationResponse",
    "AnalysisRunBase",
    "AnalysisRunCreate",
    "AnalysisRunResponse",
]
