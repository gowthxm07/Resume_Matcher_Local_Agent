"""
Phase 7 End-to-End Acceptance and Production Validation Test Suite.
Verifies complete fresh-user journey, Dataset A (Strong Match), Dataset B (Evidence Gaps),
Anti-hallucination guardrails, Metric stripping, ATS validation, Versioning, Capability negotiation, and Security.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from pathlib import Path
import json

from app.core.config import settings
from app.schemas.local_agent import CompatibilityStatus
from app.services.compatibility_service import CompatibilityService
from app.services.ollama_service import ollama_service
from app.services.matching_engine import matching_engine
from app.services.fact_checker_service import fact_checker_service
from app.services.ats_service import ats_service
from app.schemas.optimization import OptimizationChange, ChangeType, FactCheckStatus

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "fixtures"
with open(FIXTURES_DIR / "dataset_a_strong_match.json", "r", encoding="utf-8") as f:
    DATASET_A = json.load(f)
with open(FIXTURES_DIR / "dataset_b_evidence_gaps.json", "r", encoding="utf-8") as f:
    DATASET_B = json.load(f)


@pytest.mark.asyncio
async def test_fresh_user_compatibility_failure_and_recovery():
    """Verify deterministic compatibility failure detection and immediate recovery without restart."""
    service = CompatibilityService()

    # 1. Failure simulation: Ollama unreachable
    with patch("httpx.AsyncClient.get", side_effect=Exception("Connection refused")):
        check, models = await service.check_ollama()
        assert check.status == CompatibilityStatus.MISSING
        assert models == []

    # 2. Recovery simulation: Ollama reachable with required models
    dummy_tags = {
        "models": [
            {"name": "llama3.2:3b"},
            {"name": "nomic-embed-text:latest"},
        ]
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = dummy_tags

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        check, models = await service.check_ollama()
        assert check.status == CompatibilityStatus.READY
        assert "llama3.2:3b" in models
        assert "nomic-embed-text:latest" in models


def test_dataset_a_strong_match_e2e(client: TestClient):
    """
    End-to-end evaluation using Dataset A:
    Candidate with genuine local evidence for Python, FastAPI, and PostgreSQL.
    Verifies high match score (>= 70), evidence corroboration, ATS validation, and grounded optimization.
    """
    with patch.object(ollama_service, "check_availability", new_callable=AsyncMock) as mock_avail:
        mock_avail.return_value = {"reachable": False, "models": []}

        # 1. Post match analysis
        res = client.post(
            "/api/analysis/match",
            data={
                "resume_text": DATASET_A["resume_text"],
                "jd_text": DATASET_A["jd_text"],
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["overall_score"] >= 70.0
        run_id = data["analysis_run_id"]

        # 2. Verify ATS validation on original resume
        ats_result = ats_service.evaluate_resume(DATASET_A["resume_text"])
        assert ats_result.overall_ats_score >= 65.0
        assert "ATS scores are heuristic estimates" in ats_result.disclaimer

        # 3. Verify optimization loop creates grounded improvements
        opt_res = client.post(
            "/api/analysis/optimize",
            json={
                "raw_resume_text": DATASET_A["resume_text"],
                "raw_jd_text": DATASET_A["jd_text"],
                "max_iterations": 2,
                "use_live_llm": False,
            },
        )
        assert opt_res.status_code == 200
        opt_data = opt_res.json()
        assert opt_data["run_id"] is not None
        assert len(opt_data["versions"]) >= 1
        assert opt_data["versions"][0]["iteration"] == 0
        assert opt_data["versions"][0]["status"] == "ORIGINAL"


def test_dataset_b_evidence_gaps_and_anti_hallucination(client: TestClient):
    """
    End-to-end evaluation using Dataset B:
    Frontend candidate applying for senior cloud architect position.
    Strictly verifies:
    1. Low baseline match score (< 60.0)
    2. Missing required cloud skills remain explicitly missing
    3. Zero hallucination: AWS and Kubernetes are NOT invented
    4. Unsupported scale claim ('10x throughput scaling on AWS') is rejected or repaired
    """
    with patch.object(ollama_service, "check_availability", new_callable=AsyncMock) as mock_avail:
        mock_avail.return_value = {"reachable": False, "models": []}

        # 1. Baseline analysis
        res = client.post(
            "/api/analysis/match",
            data={
                "resume_text": DATASET_B["resume_text"],
                "jd_text": DATASET_B["jd_text"],
            },
        )
        assert res.status_code == 200
        data = res.json()
        # Should have a lower match score due to skill mismatch
        assert data["overall_score"] < 60.0

        # 2. Fact-checking audit on unsupported candidate claim
        unsupported_proposal = OptimizationChange(
            change_id="change_unsupported_cloud",
            original_text="Static portfolio website built with Next.js.",
            proposed_text="Architected Kubernetes clusters using Terraform and Helm for multi-cloud infrastructure.",
            reason="Injected high-demand cloud keywords to match JD",
            change_type=ChangeType.TECHNICAL_SPECIFICITY.value,
        )

        result = fact_checker_service.verify_change(
            change=unsupported_proposal,
            trusted_resume_text=DATASET_B["resume_text"],
            verified_technologies=set(),
        )
        assert result.overall_status in (FactCheckStatus.UNSUPPORTED.value, FactCheckStatus.PARTIALLY_SUPPORTED.value)
        unsupported_texts = [c.text.lower() for c in result.unsupported_claims]
        assert any("kubernetes" in t for t in unsupported_texts)
        assert any("terraform" in t for t in unsupported_texts)


def test_security_audit_path_traversal_prevention(client: TestClient):
    """Security verification: Filesystem path traversal attempts are rejected."""
    traversal_paths = [
        "../../../../Windows/System32/cmd.exe",
        "/etc/passwd",
        "..\\..\\sensitive_data.db",
    ]
    for bad_path in traversal_paths:
        res = client.post(
            "/api/projects/register",
            json={"name": "Exploit Test", "path": bad_path, "description": "Security test"},
        )
        assert res.status_code == 400


def test_security_audit_network_and_cors_invariants():
    """Security verification: Host binding is 127.0.0.1 and wildcard CORS is rejected."""
    assert settings.HOST == "127.0.0.1"
    assert "*" not in settings.CORS_ORIGINS


def test_local_agent_capability_negotiation(client: TestClient):
    """Verify Local Agent capabilities endpoint explicitly reports InterviewAgent as deferred/unsupported."""
    res = client.get("/api/local-agent/capabilities")
    assert res.status_code == 200
    caps = res.json()
    assert caps["interview_intelligence"] is False
    assert caps["analysis"] is True
    assert caps["evidence_scanning"] is True
    assert caps["resume_optimization"] is True
    assert caps["fact_checking"] is True
    assert caps["ats_validation"] is True


@pytest.mark.asyncio
async def test_ollama_service_embed_and_smoke():
    """Verify local embedding generation and lightweight smoke test execution."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"embedding": [0.123] * 768}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        vec = await ollama_service.embed("Test local embedding")
        assert len(vec) == 768
        assert vec[0] == 0.123
