"""
CrewAI Orchestration Architecture Plan for CareerCrew.
Defines the planned multi-agent lifecycle, delegation rules, and verification loops.
Zero LLM calls are executed in Phase 1; this module serves as the architectural specification.
"""

from typing import List, Dict, Any
from app.agents.base import BaseCareerAgent
from app.agents.manager import ManagerAgent
from app.agents.jd_analyzer import JDAnalyzerAgent
from app.agents.resume_analyzer import ResumeAnalyzerAgent
from app.agents.evidence import EvidenceAgent
from app.agents.match_analyzer import MatchAnalyzerAgent
from app.agents.resume_optimizer import ResumeOptimizerAgent
from app.agents.fact_checker import FactCheckerAgent
from app.agents.ats_validator import ATSValidatorAgent
from app.agents.interview import InterviewAgent


class CareerCrewOrchestrator:
    """
    Architectural blueprint for the Phase 2 CrewAI multi-agent career intelligence engine.

    Workflow Sequence:
    ==================
    Stage 1: Ingestion & Extraction (Parallel)
      - JD Analyzer deconstructs target role requirements.
      - Resume Analyzer decomposes applicant resume into structured accomplishments.
      - Evidence Agent scans local git projects to index authentic proof.

    Stage 2: Match & Gap Assessment
      - Match Analyzer computes semantic overlap and surfaces critical gaps.

    Stage 3: Iterative Verification & Optimization Loop (Manager Supervised)
      - Resume Optimizer refactors bullets to highlight verified skills.
      - Fact Checker evaluates EVERY updated bullet against original resume + project code.
        If any hallucinated or unverified claim is detected, the draft is rejected back to Optimizer.
      - ATS Validator checks layout hierarchy, keyword density, and formatting.
      - Iteration completes when both Fact Checker and ATS Validator pass.

    Stage 4: Dossier & Interview Prep
      - Interview Agent generates grounded technical & STAR questions based on matched evidence.
      - Manager compiles final review dossier.
    """

    def __init__(self):
        self.manager = ManagerAgent()
        self.jd_analyzer = JDAnalyzerAgent()
        self.resume_analyzer = ResumeAnalyzerAgent()
        self.evidence_agent = EvidenceAgent()
        self.match_analyzer = MatchAnalyzerAgent()
        self.resume_optimizer = ResumeOptimizerAgent()
        self.fact_checker = FactCheckerAgent()
        self.ats_validator = ATSValidatorAgent()
        self.interview_agent = InterviewAgent()

    def get_all_agents(self) -> List[BaseCareerAgent]:
        """Return list of all registered team agents."""
        return [
            self.manager,
            self.jd_analyzer,
            self.resume_analyzer,
            self.evidence_agent,
            self.match_analyzer,
            self.resume_optimizer,
            self.fact_checker,
            self.ats_validator,
            self.interview_agent,
        ]

    def get_system_architecture_summary(self) -> Dict[str, Any]:
        """Return structured summary of the agent system architecture."""
        return {
            "orchestrator": "CareerCrew Local Multi-Agent Orchestrator",
            "framework": "CrewAI (Local Ollama LLM / Llama 3.2:3b)",
            "cloud_dependencies": "None (Strict local-only execution)",
            "pipeline_status": "Phase 1 Foundation - Architecture Established",
            "agent_count": 9,
            "agents": [a.to_dict() for a in self.get_all_agents()],
            "pipeline_stages": [
                {
                    "stage": 1,
                    "name": "Deconstruction & Evidence Scanning",
                    "agents": ["JD Analyzer Agent", "Resume Analyzer Agent", "Evidence Agent"],
                },
                {
                    "stage": 2,
                    "name": "Baseline Match Assessment",
                    "agents": ["Match Analyzer Agent"],
                },
                {
                    "stage": 3,
                    "name": "Zero-Hallucination Iterative Optimization Loop",
                    "agents": ["Resume Optimizer Agent", "Fact Checker Agent", "ATS Validator Agent"],
                    "loop_guardrail": "Fact Checker rejects ungrounded claims; ATS Validator checks parsing",
                },
                {
                    "stage": 4,
                    "name": "Interview Intelligence & Packaging",
                    "agents": ["Interview Agent", "Manager Agent"],
                },
            ],
        }


# Singleton orchestrator blueprint
orchestrator = CareerCrewOrchestrator()
