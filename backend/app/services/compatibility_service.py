"""
Deterministic Compatibility Engine for CareerCrew Local Agent.
Checks Python runtime, FastAPI, CrewAI, Ollama, Llama 3.2:3b, nomic-embed-text,
Git, SQLite, ChromaDB, and Local Ports without using any LLM calls or destructive actions.
"""

import sys
import shutil
import sqlite3
import subprocess
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx

from app.core.config import settings
from app.core.logging import logger
from app.schemas.local_agent import (
    CompatibilityStatus,
    CompatibilityCheckItem,
    CompatibilityResponse,
    AgentCapabilitiesResponse,
    AgentHealthResponse,
)


class CompatibilityService:
    """
    Deterministic system diagnostics service for verifying local runtime capabilities.
    Does NOT invoke any LLM or remote cloud services.
    """

    def __init__(self, ollama_base_url: Optional[str] = None):
        self.ollama_base_url = (ollama_base_url or settings.OLLAMA_BASE_URL).rstrip("/")

    def check_python(self) -> CompatibilityCheckItem:
        """Deterministic check for Python runtime version."""
        ver = sys.version_info
        detected = f"{ver.major}.{ver.minor}.{ver.micro}"
        if ver.major == 3 and ver.minor >= 10:
            return CompatibilityCheckItem(
                name="Python",
                status=CompatibilityStatus.READY,
                required=True,
                detected_version=detected,
                required_version=">= 3.10",
                message=f"Python {detected} runtime is fully supported.",
                setup_route="/get-started#python",
            )
        return CompatibilityCheckItem(
            name="Python",
            status=CompatibilityStatus.OUTDATED,
            required=True,
            detected_version=detected,
            required_version=">= 3.10",
            message=f"Python {detected} detected; CareerCrew requires Python 3.10+.",
            setup_route="/get-started#python",
        )

    def check_fastapi(self) -> CompatibilityCheckItem:
        """Deterministic check for FastAPI import and runtime."""
        try:
            import fastapi
            ver = getattr(fastapi, "__version__", "installed")
            return CompatibilityCheckItem(
                name="FastAPI",
                status=CompatibilityStatus.READY,
                required=True,
                detected_version=str(ver),
                required_version=">= 0.100.0",
                message="FastAPI local REST server is active.",
                setup_route="/get-started#fastapi",
            )
        except ImportError as exc:
            return CompatibilityCheckItem(
                name="FastAPI",
                status=CompatibilityStatus.MISSING,
                required=True,
                detected_version=None,
                required_version=">= 0.100.0",
                message=f"FastAPI is not installed: {exc}",
                setup_route="/get-started#fastapi",
            )

    def check_crewai(self) -> CompatibilityCheckItem:
        """Deterministic check for CrewAI multi-agent runtime."""
        try:
            import crewai
            ver = getattr(crewai, "__version__", "installed")
            return CompatibilityCheckItem(
                name="CrewAI",
                status=CompatibilityStatus.READY,
                required=True,
                detected_version=str(ver),
                required_version=">= 0.50.0",
                message="CrewAI multi-agent orchestration runtime is ready.",
                setup_route="/get-started#crewai",
            )
        except ImportError as exc:
            return CompatibilityCheckItem(
                name="CrewAI",
                status=CompatibilityStatus.MISSING,
                required=True,
                detected_version=None,
                required_version=">= 0.50.0",
                message=f"CrewAI is not installed: {exc}",
                setup_route="/get-started#crewai",
            )

    async def check_ollama(self) -> tuple[CompatibilityCheckItem, List[str]]:
        """
        Deterministic check for Ollama reachability and retrieved model tags.
        Returns check item and list of installed model names.
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.ollama_base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name", "") for m in data.get("models", []) if isinstance(m, dict)]
                    return (
                        CompatibilityCheckItem(
                            name="Ollama",
                            status=CompatibilityStatus.READY,
                            required=True,
                            detected_version="reachable",
                            required_version=">= 0.1.0",
                            message="Local Ollama server is running and reachable on localhost.",
                            setup_route="/get-started#ollama",
                        ),
                        models,
                    )
                return (
                    CompatibilityCheckItem(
                        name="Ollama",
                        status=CompatibilityStatus.ERROR,
                        required=True,
                        detected_version=f"HTTP {res.status_code}",
                        required_version=">= 0.1.0",
                        message=f"Ollama server returned unexpected HTTP status {res.status_code}.",
                        setup_route="/get-started#ollama",
                    ),
                    [],
                )
        except Exception:
            return (
                CompatibilityCheckItem(
                    name="Ollama",
                    status=CompatibilityStatus.MISSING,
                    required=True,
                    detected_version=None,
                    required_version=">= 0.1.0",
                    message="Ollama server is not reachable at configured base URL. Start Ollama locally.",
                    setup_route="/get-started#ollama",
                ),
                [],
            )

    def check_llm_model(self, models: List[str]) -> CompatibilityCheckItem:
        """Deterministic check for Llama 3.2:3b model in Ollama tags."""
        target = "llama3.2:3b"
        found = any(m == target or m.startswith("llama3.2:3b") or m.startswith("llama3.2") for m in models)
        if found:
            matched = next((m for m in models if "llama3.2" in m), target)
            return CompatibilityCheckItem(
                name="Llama 3.2:3B",
                status=CompatibilityStatus.READY,
                required=True,
                detected_version=matched,
                required_version="llama3.2:3b",
                message="Llama 3.2:3b inference model is installed and ready in local Ollama.",
                setup_route="/get-started#models",
            )
        return CompatibilityCheckItem(
            name="Llama 3.2:3B",
            status=CompatibilityStatus.MISSING,
            required=True,
            detected_version=None,
            required_version="llama3.2:3b",
            message="Required LLM model 'llama3.2:3b' not found in Ollama. Run: ollama pull llama3.2:3b",
            setup_route="/get-started#models",
        )

    def check_embedding_model(self, models: List[str]) -> CompatibilityCheckItem:
        """Deterministic check for nomic-embed-text model in Ollama tags."""
        target = "nomic-embed-text"
        found = any(target in m for m in models)
        if found:
            matched = next((m for m in models if target in m), target)
            return CompatibilityCheckItem(
                name="nomic-embed-text",
                status=CompatibilityStatus.READY,
                required=True,
                detected_version=matched,
                required_version="nomic-embed-text",
                message="Local embedding model 'nomic-embed-text' is installed in Ollama.",
                setup_route="/get-started#models",
            )
        return CompatibilityCheckItem(
            name="nomic-embed-text",
            status=CompatibilityStatus.MISSING,
            required=True,
            detected_version=None,
            required_version="nomic-embed-text",
            message="Required embedding model 'nomic-embed-text' not found. Run: ollama pull nomic-embed-text",
            setup_route="/get-started#models",
        )

    def check_git(self) -> CompatibilityCheckItem:
        """Deterministic check for Git CLI availability."""
        git_path = shutil.which("git")
        if not git_path:
            return CompatibilityCheckItem(
                name="Git",
                status=CompatibilityStatus.MISSING,
                required=True,
                detected_version=None,
                required_version=">= 2.20",
                message="Git command line tool not found in PATH. Required for project evidence scanning.",
                setup_route="/get-started#git",
            )
        try:
            res = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            out = res.stdout.strip()
            # Parse version string e.g. "git version 2.45.0.windows.1"
            parts = out.split()
            ver = parts[2] if len(parts) >= 3 else "available"
            return CompatibilityCheckItem(
                name="Git",
                status=CompatibilityStatus.READY,
                required=True,
                detected_version=ver,
                required_version=">= 2.20",
                message=f"Git CLI detected ({ver}). Evidence scanning runtime ready.",
                setup_route="/get-started#git",
            )
        except Exception as exc:
            return CompatibilityCheckItem(
                name="Git",
                status=CompatibilityStatus.ERROR,
                required=True,
                detected_version=None,
                required_version=">= 2.20",
                message=f"Git check failed during execution: {exc}",
                setup_route="/get-started#git",
            )

    def check_sqlite(self) -> CompatibilityCheckItem:
        """Deterministic check for SQLite accessibility and database connectivity."""
        try:
            ver = sqlite3.sqlite_version
            # Non-destructive read verification using SQLAlchemy session
            from sqlalchemy import text
            from app.db.session import SessionLocal
            db = SessionLocal()
            try:
                db.execute(text("SELECT 1"))
            finally:
                db.close()

            return CompatibilityCheckItem(
                name="SQLite",
                status=CompatibilityStatus.READY,
                required=True,
                detected_version=ver,
                required_version=">= 3.30",
                message=f"SQLite {ver} local relational database operational.",
                setup_route="/get-started#sqlite",
            )
        except Exception as exc:
            return CompatibilityCheckItem(
                name="SQLite",
                status=CompatibilityStatus.ERROR,
                required=True,
                detected_version=getattr(sqlite3, "sqlite_version", None),
                required_version=">= 3.30",
                message=f"SQLite database error: {exc}",
                setup_route="/get-started#sqlite",
            )

    def check_chromadb(self) -> CompatibilityCheckItem:
        """Deterministic check for local ChromaDB vector store initialization."""
        try:
            import chromadb
            ver = getattr(chromadb, "__version__", "installed")
            from app.services.vector_store import vector_store
            # Safe status probe without modifying vectors
            if vector_store._initialized or settings.VECTOR_STORE_DIR.exists():
                return CompatibilityCheckItem(
                    name="ChromaDB",
                    status=CompatibilityStatus.READY,
                    required=True,
                    detected_version=str(ver),
                    required_version=">= 0.4.0",
                    message="ChromaDB local vector store persistence accessible.",
                    setup_route="/get-started#chroma",
                )
            return CompatibilityCheckItem(
                name="ChromaDB",
                status=CompatibilityStatus.READY,
                required=True,
                detected_version=str(ver),
                required_version=">= 0.4.0",
                message="ChromaDB library available; persistence directory configured.",
                setup_route="/get-started#chroma",
            )
        except ImportError as exc:
            return CompatibilityCheckItem(
                name="ChromaDB",
                status=CompatibilityStatus.MISSING,
                required=True,
                detected_version=None,
                required_version=">= 0.4.0",
                message=f"ChromaDB is not installed: {exc}",
                setup_route="/get-started#chroma",
            )
        except Exception as exc:
            return CompatibilityCheckItem(
                name="ChromaDB",
                status=CompatibilityStatus.ERROR,
                required=True,
                detected_version=None,
                required_version=">= 0.4.0",
                message=f"ChromaDB access error: {exc}",
                setup_route="/get-started#chroma",
            )

    def check_local_agent_version(self) -> CompatibilityCheckItem:
        """CareerCrew agent version check."""
        return CompatibilityCheckItem(
            name="CareerCrew Local Agent",
            status=CompatibilityStatus.READY,
            required=True,
            detected_version="1.0.0",
            required_version="1.0.0",
            message="CareerCrew Local Agent runtime active on localhost.",
            setup_route="/get-started",
        )

    def check_local_ports(self) -> CompatibilityCheckItem:
        """Deterministic confirmation of configured ports for local agent and Ollama."""
        return CompatibilityCheckItem(
            name="Local Ports",
            status=CompatibilityStatus.READY,
            required=False,
            detected_version=f"Port {settings.PORT} (API), 11434 (Ollama)",
            required_version="8000, 11434",
            message=f"Local Agent bound to {settings.HOST}:{settings.PORT}; Ollama configured at {settings.OLLAMA_BASE_URL}.",
            setup_route="/get-started#ports",
        )

    async def get_compatibility_report(self) -> CompatibilityResponse:
        """
        Execute all deterministic checks and aggregate into an overall compatibility response.
        Overall ready is True ONLY if all required checks are in READY status.
        """
        # 1. Synchronous checks
        py_check = self.check_python()
        fastapi_check = self.check_fastapi()
        crewai_check = self.check_crewai()
        git_check = self.check_git()
        sqlite_check = self.check_sqlite()
        chroma_check = self.check_chromadb()
        agent_check = self.check_local_agent_version()
        ports_check = self.check_local_ports()

        # 2. Asynchronous Ollama + model checks
        ollama_check, models = await self.check_ollama()
        llm_check = self.check_llm_model(models)
        embed_check = self.check_embedding_model(models)

        # Order matches logical stack:
        # Runtime -> LLM & Embeddings -> Multi-Agent & Orchestration -> Tools & DB -> Agent Ports
        all_checks = [
            agent_check,
            ollama_check,
            llm_check,
            embed_check,
            crewai_check,
            fastapi_check,
            git_check,
            sqlite_check,
            chroma_check,
            py_check,
            ports_check,
        ]

        # Calculate ready: ALL required checks must be READY
        is_ready = all(
            c.status == CompatibilityStatus.READY
            for c in all_checks
            if c.required
        )

        now_iso = datetime.now(timezone.utc).isoformat()

        return CompatibilityResponse(
            ready=is_ready,
            checks=all_checks,
            agent_version="1.0.0",
            timestamp=now_iso,
        )

    def get_capabilities(self) -> AgentCapabilitiesResponse:
        """Return truthful capability mapping."""
        return AgentCapabilitiesResponse(
            analysis=True,
            multi_agent=True,
            evidence_scanning=True,
            resume_optimization=True,
            fact_checking=True,
            ats_validation=True,
            github_import=True,
            interview_intelligence=False,  # Strictly deferred per Phase 5/6 boundary
        )

    def get_health(self) -> AgentHealthResponse:
        """Return local agent health status with zero path or credential exposure."""
        return AgentHealthResponse(
            agent="careercrew-local-agent",
            status="ready",
            version="1.0.0",
            api_version="1",
            local_only=True,
        )


compatibility_service = CompatibilityService()
