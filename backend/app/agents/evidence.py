"""
Evidence Agent implementation for CareerCrew.
Inspects candidate's local git repositories, commit logs, code structures, and manifests
to extract tangible, verifiable proof for claimed competencies without executing arbitrary code.
"""

from typing import List, Any
from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole
from app.agents.tools.evidence_tools import get_evidence_tools
from app.agents.llm_config import get_crewai_llm

try:
    from crewai import Agent
except ImportError:
    Agent = None


class EvidenceAgent(BaseCareerAgent):
    """
    Evidence Agent.
    Inspects candidate's local git repositories, commit logs, code structures, and manifests
    to extract tangible, verifiable proof for claimed competencies without executing arbitrary code.
    Distinguishes VERIFIED, LIKELY, WEAK, UNVERIFIED, and UNAVAILABLE.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.EVIDENCE,
                name="Project Evidence & Codebase Inspector",
                goal="Ground resume claims in verifiable local project evidence, git commits, and code artifacts.",
                backstory=(
                    "A lead software architect and code forensic expert who verifies technical authenticity "
                    "by inspecting git trees, commit histories, PR comments, and code patterns."
                ),
                planned_tools=["scan_git_repository", "extract_commit_evidence", "find_skill_evidence", "verify_skill"],
                is_implemented=False,
                phase=2,
            )
        )

    def get_tools(self) -> List[Any]:
        """Return deterministic evidence inspection tools assigned to this agent."""
        return get_evidence_tools()

    def create_crewai_agent(self, llm=None, verbose: bool = False):
        """Instantiate underlying CrewAI Agent instance configured with local Ollama."""
        agent_llm = llm or get_crewai_llm()
        if Agent is None:
            raise RuntimeError("CrewAI Agent class is not installed.")
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=self.get_tools(),
            llm=agent_llm,
            verbose=verbose,
            allow_delegation=False,
        )
