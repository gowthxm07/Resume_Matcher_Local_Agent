"""
Schemas for CareerCrew Local Agent, Compatibility Diagnostics, and Capabilities.
Ensures zero exposure of private file paths, secrets, tokens, or credentials.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class CompatibilityStatus(str, Enum):
    """Controlled status categories for local system compatibility checks."""
    READY = "READY"
    MISSING = "MISSING"
    OUTDATED = "OUTDATED"
    ERROR = "ERROR"
    OPTIONAL = "OPTIONAL"
    CHECKING = "CHECKING"


class CompatibilityCheckItem(BaseModel):
    """Deterministic compatibility diagnostic result for a single component."""
    name: str = Field(..., description="Name of the component checked")
    status: CompatibilityStatus = Field(..., description="Current status of the component")
    required: bool = Field(..., description="Whether this component is mandatory for local operation")
    detected_version: Optional[str] = Field(None, description="Safely detected version without path leaks")
    required_version: Optional[str] = Field(None, description="Recommended or required version range")
    message: str = Field(..., description="Human-readable status summary or remediation step")
    setup_route: Optional[str] = Field(None, description="Setup or documentation anchor/route")


class CompatibilityResponse(BaseModel):
    """Aggregate response for system compatibility."""
    ready: bool = Field(..., description="True only if all required checks are in READY status")
    checks: List[CompatibilityCheckItem] = Field(..., description="List of all component checks")
    agent_version: str = Field("1.0.0", description="CareerCrew local agent protocol version")
    timestamp: str = Field(..., description="ISO 8601 timestamp of diagnostic execution")


class AgentHealthResponse(BaseModel):
    """
    Standardized Local Agent health response for Vercel Dashboard connection verification.
    No paths, credentials, tokens, or environment secrets are exposed.
    """
    agent: str = Field("careercrew-local-agent", description="Canonical local agent identifier")
    status: str = Field("ready", description="Operational status of the local agent runtime")
    version: str = Field("1.0.0", description="Semantic version of the CareerCrew agent")
    api_version: str = Field("1", description="API protocol version")
    local_only: bool = Field(True, description="Strict confirmation of local-only architecture")


class AgentCapabilitiesResponse(BaseModel):
    """
    Feature capability map exposed by the local agent.
    Reflects true active features vs strictly deferred capabilities.
    """
    analysis: bool = Field(True, description="Deterministic & multidimensional match analysis")
    multi_agent: bool = Field(True, description="CrewAI multi-agent orchestration layer")
    evidence_scanning: bool = Field(True, description="Local Git repository parsing & evidence extraction")
    resume_optimization: bool = Field(True, description="Evidence-grounded iterative resume optimization")
    fact_checking: bool = Field(True, description="Adversarial fact checking & zero-hallucination validation")
    ats_validation: bool = Field(True, description="Enterprise ATS heuristic parsing & format scoring")
    github_import: bool = Field(True, description="Local repository inspection & clone interface")
    interview_intelligence: bool = Field(False, description="Interview prep generator strictly deferred")
