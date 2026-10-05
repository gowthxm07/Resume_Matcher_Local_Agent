"""
Base abstractions for CareerCrew multi-agent system.
Integrates with CrewAI and ensures local-only Ollama LLM execution.
All agents in Phase 1 are established as architectural foundations (planned/future components).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.logging import logger


class AgentRole(str, Enum):
    """Enumeration of planned specialized agents in CareerCrew."""
    MANAGER = "Manager Agent"
    JD_ANALYZER = "JD Analyzer Agent"
    RESUME_ANALYZER = "Resume Analyzer Agent"
    EVIDENCE = "Evidence Agent"
    MATCH_ANALYZER = "Match Analyzer Agent"
    RESUME_OPTIMIZER = "Resume Optimizer Agent"
    FACT_CHECKER = "Fact Checker Agent"
    ATS_VALIDATOR = "ATS Validator Agent"
    INTERVIEW = "Interview Agent"


class AgentMetadata(BaseModel):
    """Metadata describing a multi-agent team member."""
    role: AgentRole
    name: str
    goal: str
    backstory: str
    planned_tools: List[str] = Field(default_factory=list)
    is_implemented: bool = False
    phase: int = 2
    llm_model: str = Field(default_factory=lambda: settings.OLLAMA_MODEL)


class BaseCareerAgent(ABC):
    """
    Base contract for all CareerCrew agents.
    In Phase 1, concrete agents inherit this to define roles, goals, backstories,
    and planned tool bindings without executing unnecessary LLM calls.
    """

    def __init__(self, metadata: AgentMetadata):
        self.metadata = metadata

    @property
    def role(self) -> str:
        return self.metadata.role.value

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def goal(self) -> str:
        return self.metadata.goal

    @property
    def backstory(self) -> str:
        return self.metadata.backstory

    @property
    def is_implemented(self) -> bool:
        return self.metadata.is_implemented

    def to_dict(self) -> Dict[str, Any]:
        """Return agent configuration and status information."""
        return self.metadata.model_dump()

    def create_crewai_agent(self, verbose: bool = False):
        """
        Factory to instantiate the underlying CrewAI Agent instance.
        In Phase 1, raises NotImplementedError indicating implementation belongs to Phase 2.
        """
        raise NotImplementedError(
            f"{self.metadata.name} is a planned Phase 2 component. "
            "Real agent orchestration begins in Phase 2."
        )
