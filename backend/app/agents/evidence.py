from typing import List, Any
from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole
from app.agents.tools.evidence_tools import get_evidence_tools


class EvidenceAgent(BaseCareerAgent):
    """
    Evidence Agent (Phase 3 Component).
    Inspects candidate's local git repositories, commit logs, code structures, and manifests
    to extract tangible, verifiable proof for claimed competencies without executing arbitrary code.
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
        """Return deterministic tools assigned to this agent."""
        return get_evidence_tools()


