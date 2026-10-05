"""
Match Analyzer Agent placeholder specification for CareerCrew.
"""

from app.agents.base import BaseCareerAgent, AgentMetadata, AgentRole


class MatchAnalyzerAgent(BaseCareerAgent):
    """
    Match Analyzer Agent (Planned Phase 2 Component).
    Calculates detailed semantic and keyword match scores between candidate background
    and job requirements, surfacing exact coverage and critical gaps.
    """

    def __init__(self):
        super().__init__(
            AgentMetadata(
                role=AgentRole.MATCH_ANALYZER,
                name="Alignment & Gap Auditor",
                goal="Assess factual alignment between candidate skills and job requirements, identifying coverage gaps.",
                backstory=(
                    "An analytical compensation and talent matching strategist who computes objective "
                    "compatibility matrices between candidate abilities and role requirements."
                ),
                planned_tools=["compute_match_score", "identify_coverage_gaps", "rank_priority_alignments"],
                is_implemented=False,
                phase=2,
            )
        )
