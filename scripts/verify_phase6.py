"""
Phase 6 Complete Verification Script for CareerCrew.
Verifies Local Agent, Vercel Dashboard Compatibility, and Privacy Architecture:
1. Local Agent Health Endpoint (GET /api/local-agent/health)
2. Compatibility Endpoint (GET /api/local-agent/compatibility)
3. Capabilities Negotiation Endpoint (GET /api/local-agent/capabilities)
4. Deterministic Ollama Reachability Detection
5. Deterministic Llama 3.2:3b Model Detection
6. Deterministic nomic-embed-text Model Detection
7. CrewAI Runtime Detection (import & orchestration readiness)
8. Git CLI & Evidence Scanning Initialization Check
9. Local Database Detection (SQLite relational tables)
10. Local Vector Store Persistence Detection (ChromaDB)
11. Local-Only Privacy Architecture & Cloud API Prohibition
12. Localhost Network Binding & Security Isolation
13. CORS Strictness & Prohibited Wildcard Validation
14. Frontend Onboarding & Setup Architecture (/get-started)
15. Frontend Privacy Center Architecture (/privacy)
"""

import sys
import os
import json
import shutil
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from fastapi.testclient import TestClient

# Add backend to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.core.config import settings, Settings
from app.main import app
from app.services.compatibility_service import compatibility_service, CompatibilityService
from app.schemas.local_agent import CompatibilityStatus


def run_phase6_verification():
    print("=" * 75)
    print("CAREERCREW PHASE 6 VERIFICATION SUITE")
    print("Local Agent + Vercel Dashboard + Compatibility & Privacy Architecture")
    print("=" * 75)

    client = TestClient(app)
    checks_passed = 0
    total_checks = 15

    # --------------------------------------------------------------------------
    # Check 1: Local Agent Health Endpoint
    # --------------------------------------------------------------------------
    print("\n[CHECK 1/15] Testing Local Agent Health Endpoint (/api/local-agent/health)...")
    res = client.get("/api/local-agent/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    health_data = res.json()
    assert health_data["agent"] == "careercrew-local-agent"
    assert health_data["status"] == "ready"
    assert health_data["version"] == "1.0.0"
    assert health_data["api_version"] == "1"
    assert health_data["local_only"] is True
    # Ensure zero path or secret exposure
    dump = json.dumps(health_data).lower()
    assert "token" not in dump and "secret" not in dump and "c:\\" not in dump
    print(f"  -> Health OK: {health_data['agent']} v{health_data['version']} (local_only={health_data['local_only']})")
    print("  [PASS] Check 1 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 2: Compatibility Endpoint
    # --------------------------------------------------------------------------
    print("\n[CHECK 2/15] Testing Compatibility Diagnostics Endpoint (/api/local-agent/compatibility)...")
    res = client.get("/api/local-agent/compatibility")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    comp_data = res.json()
    assert "ready" in comp_data and isinstance(comp_data["ready"], bool)
    assert "checks" in comp_data and len(comp_data["checks"]) >= 10
    assert comp_data["agent_version"] == "1.0.0"
    print(f"  -> Aggregate Compatibility Status: ready={comp_data['ready']}, checks_count={len(comp_data['checks'])}")
    print("  [PASS] Check 2 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 3: Capabilities Negotiation Endpoint
    # --------------------------------------------------------------------------
    print("\n[CHECK 3/15] Testing Capabilities Negotiation Endpoint (/api/local-agent/capabilities)...")
    res = client.get("/api/local-agent/capabilities")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    caps_data = res.json()
    assert caps_data["analysis"] is True
    assert caps_data["multi_agent"] is True
    assert caps_data["evidence_scanning"] is True
    assert caps_data["resume_optimization"] is True
    assert caps_data["fact_checking"] is True
    assert caps_data["ats_validation"] is True
    assert caps_data["github_import"] is True
    assert caps_data["interview_intelligence"] is False, "InterviewAgent must remain strictly deferred"
    print(f"  -> Active Capabilities: {json.dumps(caps_data, indent=2)}")
    print("  [PASS] Check 3 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 4: Deterministic Ollama Reachability Detection
    # --------------------------------------------------------------------------
    print("\n[CHECK 4/15] Verifying Deterministic Ollama Reachability Detection...")
    ollama_check, models = asyncio.run(compatibility_service.check_ollama())
    print(f"  -> Ollama Status: {ollama_check.status} ({ollama_check.message})")
    print(f"  -> Detected Models: {models}")
    assert ollama_check.name == "Ollama"
    assert ollama_check.required is True
    assert ollama_check.status in (CompatibilityStatus.READY, CompatibilityStatus.MISSING)
    print("  [PASS] Check 4 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 5: Deterministic Llama 3.2:3B Model Detection
    # --------------------------------------------------------------------------
    print("\n[CHECK 5/15] Verifying Deterministic Llama 3.2:3b Model Detection...")
    llm_check = compatibility_service.check_llm_model(models)
    print(f"  -> Llama 3.2:3B Status: {llm_check.status} (detected={llm_check.detected_version})")
    assert llm_check.name == "Llama 3.2:3B"
    assert llm_check.required is True
    print("  [PASS] Check 5 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 6: Deterministic nomic-embed-text Model Detection
    # --------------------------------------------------------------------------
    print("\n[CHECK 6/15] Verifying Deterministic nomic-embed-text Embedding Model Detection...")
    embed_check = compatibility_service.check_embedding_model(models)
    print(f"  -> nomic-embed-text Status: {embed_check.status} (detected={embed_check.detected_version})")
    assert embed_check.name == "nomic-embed-text"
    assert embed_check.required is True
    print("  [PASS] Check 6 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 7: CrewAI Runtime Detection
    # --------------------------------------------------------------------------
    print("\n[CHECK 7/15] Verifying CrewAI Multi-Agent Runtime Detection...")
    crewai_check = compatibility_service.check_crewai()
    print(f"  -> CrewAI Status: {crewai_check.status} (ver={crewai_check.detected_version})")
    assert crewai_check.name == "CrewAI"
    assert crewai_check.status == CompatibilityStatus.READY
    assert crewai_check.required is True
    print("  [PASS] Check 7 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 8: Git CLI & Evidence Scanning Readiness Check
    # --------------------------------------------------------------------------
    print("\n[CHECK 8/15] Verifying Git CLI & Evidence Scanner Readiness...")
    git_check = compatibility_service.check_git()
    print(f"  -> Git Status: {git_check.status} (ver={git_check.detected_version})")
    assert git_check.name == "Git"
    assert git_check.status == CompatibilityStatus.READY
    assert git_check.required is True
    print("  [PASS] Check 8 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 9: Local Database Detection (SQLite)
    # --------------------------------------------------------------------------
    print("\n[CHECK 9/15] Verifying Local Database Detection (SQLite)...")
    sqlite_check = compatibility_service.check_sqlite()
    print(f"  -> SQLite Status: {sqlite_check.status} (ver={sqlite_check.detected_version})")
    assert sqlite_check.name == "SQLite"
    assert sqlite_check.status == CompatibilityStatus.READY
    print("  [PASS] Check 9 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 10: Local Vector Store Persistence Detection (ChromaDB)
    # --------------------------------------------------------------------------
    print("\n[CHECK 10/15] Verifying Local Vector Store Detection (ChromaDB)...")
    chroma_check = compatibility_service.check_chromadb()
    print(f"  -> ChromaDB Status: {chroma_check.status} (ver={chroma_check.detected_version})")
    assert chroma_check.name == "ChromaDB"
    assert chroma_check.status == CompatibilityStatus.READY
    print("  [PASS] Check 10 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 11: Local-Only Privacy Architecture & Cloud API Prohibition
    # --------------------------------------------------------------------------
    print("\n[CHECK 11/15] Verifying Local-Only Privacy Architecture & Cloud API Prohibition...")
    assert settings.LLM_PROVIDER == "ollama"
    prohibited = ["openai", "anthropic", "gemini", "bedrock", "azure"]
    for prov in prohibited:
        try:
            Settings(LLM_PROVIDER=prov)
            assert False, f"Settings should have rejected prohibited cloud provider: {prov}"
        except ValueError:
            pass  # Expected rejection
    print("  -> Confirmed: Prohibited cloud AI providers are strictly rejected by Pydantic validators.")
    print("  [PASS] Check 11 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 12: Localhost Network Binding & Security Isolation
    # --------------------------------------------------------------------------
    print("\n[CHECK 12/15] Verifying Localhost Network Binding & Security Isolation...")
    assert settings.HOST == "127.0.0.1", f"Expected HOST='127.0.0.1', got {settings.HOST}"
    print(f"  -> Local agent host binding strictly locked to: {settings.HOST}")
    print("  [PASS] Check 12 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 13: CORS Strictness & Prohibited Wildcard Validation
    # --------------------------------------------------------------------------
    print("\n[CHECK 13/15] Verifying CORS Strictness & Prohibited Wildcard Validation...")
    assert "*" not in settings.CORS_ORIGINS
    try:
        Settings(CORS_ORIGINS=["*"])
        assert False, "Settings should have rejected wildcard '*' CORS origin."
    except ValueError:
        pass  # Expected rejection
    print(f"  -> Allowed CORS origins: {settings.CORS_ORIGINS}")
    print("  [PASS] Check 13 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 14: Frontend Onboarding & Setup Architecture (/get-started)
    # --------------------------------------------------------------------------
    print("\n[CHECK 14/15] Verifying Frontend Onboarding & Setup Architecture...")
    get_started_page = ROOT_DIR / "frontend" / "app" / "get-started" / "page.tsx"
    assert get_started_page.exists(), "frontend/app/get-started/page.tsx must exist"
    content = get_started_page.read_text(encoding="utf-8")
    assert "Re-check Compatibility" in content
    assert "COMPATIBILITY CHECK OK" in content
    assert "COMPATIBILITY CHECK FAILED" in content
    assert "ollama pull llama3.2:3b" in content
    assert "ollama pull nomic-embed-text" in content
    print("  -> Found /get-started setup page with live diagnostics, recheck, and OS tabs.")
    print("  [PASS] Check 14 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Check 15: Frontend Privacy Center Architecture (/privacy)
    # --------------------------------------------------------------------------
    print("\n[CHECK 15/15] Verifying Frontend Privacy Center Architecture...")
    privacy_page = ROOT_DIR / "frontend" / "app" / "privacy" / "page.tsx"
    assert privacy_page.exists(), "frontend/app/privacy/page.tsx must exist"
    content = privacy_page.read_text(encoding="utf-8")
    assert "WHERE YOUR DATA GOES" in content
    assert "Data Processing Matrix" in content
    assert "100% LOCAL" in content
    assert "Localhost Binding" in content
    assert "Strict CORS Restrictions" in content
    print("  -> Found /privacy center with data flow breakdown and technical privacy guarantees.")
    print("  [PASS] Check 15 passed.")
    checks_passed += 1

    # --------------------------------------------------------------------------
    # Final Summary
    # --------------------------------------------------------------------------
    print("\n" + "=" * 75)
    print(f"PHASE 6 VERIFICATION COMPLETE: {checks_passed}/{total_checks} CHECKS PASSED (100%)")
    print("=" * 75)
    return checks_passed == total_checks


if __name__ == "__main__":
    success = run_phase6_verification()
    sys.exit(0 if success else 1)
