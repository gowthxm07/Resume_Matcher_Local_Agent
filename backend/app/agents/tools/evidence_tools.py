"""
Deterministic evidence inspection tools for CrewAI agents.
Allows agents to safely query repository git metadata, commit histories,
detected technologies, and skill verification statuses without running arbitrary code.
"""

import json
from typing import List, Dict, Any, Optional
from app.core.logging import logger
from app.services.git_scanner import git_scanner
from app.services.evidence_service import evidence_service
from app.services.path_validator import PathValidator
from app.db.session import SessionLocal

try:
    from crewai.tools import tool
except ImportError:
    # Fallback decorator if crewai tools cannot be imported
    def tool(name_or_func=None):
        if callable(name_or_func):
            return name_or_func
        def decorator(f):
            return f
        return decorator


def scan_git_repository_fn(project_path: str) -> str:
    """
    Safely inspect a local candidate software project directory.
    Extracts Git metadata (branch, HEAD commit, authors) and detects technologies
    from manifests and source files without executing arbitrary code.
    Returns JSON formatted summary.
    """
    try:
        PathValidator.validate_project_path(project_path)
        meta = git_scanner.scan_repository(project_path)
        return json.dumps({
            "repo_name": meta.repo_name,
            "is_git_repo": meta.is_git_repo,
            "branch": meta.branch,
            "head_commit": meta.head_commit,
            "commit_count": meta.commit_count,
            "remote_url": meta.remote_url,
            "author_stats": meta.author_stats,
            "recent_commits_count": len(meta.recent_commits),
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error scanning git repository at '{project_path}': {e}")
        return json.dumps({"error": str(e), "path": project_path})


def extract_commit_evidence_fn(project_path: str, max_commits: int = 15) -> str:
    """
    Extract recent git commit messages, dates, authors, and changed file lists
    from a local repository. Useful for verifying hands-on contributions.
    Returns JSON formatted commit summaries.
    """
    try:
        PathValidator.validate_project_path(project_path)
        commits = git_scanner.extract_commit_history(project_path, max_commits=max_commits)
        return json.dumps([c.model_dump() for c in commits], indent=2)
    except Exception as e:
        logger.warning(f"Error extracting commits at '{project_path}': {e}")
        return json.dumps({"error": str(e), "path": project_path})


def find_skill_evidence_fn(skill: str) -> str:
    """
    Search the local SQLite database for registered repository evidence records
    supporting a specific skill (e.g. 'FastAPI', 'PostgreSQL', 'Docker').
    Returns JSON list of matching evidence records.
    """
    db = SessionLocal()
    try:
        result = evidence_service.verify_skill(skill, db)
        return json.dumps(result.model_dump(), indent=2)
    except Exception as e:
        logger.warning(f"Error finding evidence for skill '{skill}': {e}")
        return json.dumps({"error": str(e), "skill": skill})
    finally:
        db.close()


def verify_skill_fn(skill: str) -> str:
    """
    Verify whether a candidate skill is VERIFIED, LIKELY, WEAK, or UNVERIFIED
    based on concrete evidence in registered repositories.
    """
    db = SessionLocal()
    try:
        res = evidence_service.verify_skill(skill, db)
        return json.dumps({
            "skill": res.skill,
            "canonical_skill": res.canonical_skill,
            "status": res.status,
            "confidence": res.confidence,
            "evidence_count": res.evidence_count,
            "summary": res.summary,
        }, indent=2)
    except Exception as e:
        logger.warning(f"Error verifying skill '{skill}': {e}")
        return json.dumps({"error": str(e), "skill": skill})
    finally:
        db.close()


# CrewAI Tool Decorators
@tool("scan_git_repository")
def scan_git_repository_tool(project_path: str) -> str:
    """Safely scan local candidate software project for git metadata and technologies."""
    return scan_git_repository_fn(project_path)


@tool("extract_commit_evidence")
def extract_commit_evidence_tool(project_path: str, max_commits: int = 15) -> str:
    """Extract recent git commit summaries and modified files from local repository."""
    return extract_commit_evidence_fn(project_path, max_commits)


@tool("find_skill_evidence")
def find_skill_evidence_tool(skill: str) -> str:
    """Search local evidence database for atomic proofs supporting a technical skill."""
    return find_skill_evidence_fn(skill)


@tool("verify_skill")
def verify_skill_tool(skill: str) -> str:
    """Determine confidence hierarchy level (VERIFIED/LIKELY/WEAK/UNVERIFIED) for a skill."""
    return verify_skill_fn(skill)


def get_evidence_tools() -> List[Any]:
    """Return all evidence inspection tools ready for CrewAI agent binding."""
    return [
        scan_git_repository_tool,
        extract_commit_evidence_tool,
        find_skill_evidence_tool,
        verify_skill_tool,
    ]
