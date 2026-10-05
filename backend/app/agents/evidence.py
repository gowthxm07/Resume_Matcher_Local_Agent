"""
Evidence Agent placeholder specification for CareerCrew.
"""

from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole


class EvidenceAgent(BaseCareerAgent):
    """
    Evidence Agent (Planned Phase 2 Component).
    Inspects candidate's local git repositories, commit logs, code structures, and documentation
    to extract tangible, verifiable proof for claimed competencies.
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
                planned_tools=["scan_git_repository", "extract_commit_evidence", "index_code_signatures"],
                is_implemented=False,
                phase=2,
            )
        )
