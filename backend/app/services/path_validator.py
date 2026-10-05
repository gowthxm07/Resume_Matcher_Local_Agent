"""
Security and path validation service for CareerCrew repository scanning.
Strictly prevents path traversal attacks, system directory scans, internal data leakage,
and dangerous directory operations. Read-only filesystem operations only.
"""

import os
import platform
from pathlib import Path
from typing import Tuple, List
from app.core.config import settings
from app.core.logging import logger


class SecurityValidationError(ValueError):
    """Raised when a candidate project path fails security validation."""
    pass


PathValidationError = SecurityValidationError



class PathValidator:
    """
    Validates and sanitizes candidate project directory paths before any scan.
    Enforces strict read-only security boundaries.
    """

    # Prohibited system directory prefixes (lowercased)
    PROHIBITED_SYSTEM_PATTERNS = [
        "c:\\windows",
        "c:\\program files",
        "c:\\program files (x86)",
        "c:\\programdata",
        "/etc",
        "/proc",
        "/sys",
        "/dev",
        "/root",
        "/bin",
        "/sbin",
        "/usr/bin",
        "/usr/sbin",
    ]

    @classmethod
    def validate_project_path(cls, user_path: str) -> Path:
        """
        Validate, canonicalize, and verify safety of a candidate project path.
        Returns the resolved Path object if valid and safe.
        Raises SecurityValidationError if unsafe or invalid.
        """
        if not user_path or not user_path.strip():
            raise SecurityValidationError("Project path cannot be empty")

        raw_path = user_path.strip()

        # 1. Resolve canonical absolute path (defeats symlinks and ../ path traversal)
        try:
            resolved = Path(raw_path).resolve()
        except Exception as exc:
            raise SecurityValidationError(f"Invalid path syntax: {exc}")

        # 2. Check existence and directory type
        if not resolved.exists():
            raise SecurityValidationError(f"Project directory does not exist: {resolved}")

        if not resolved.is_dir():
            raise SecurityValidationError(f"Project path is not a directory: {resolved}")

        # 3. Check read permissions
        if not os.access(resolved, os.R_OK):
            raise SecurityValidationError(f"Project directory is not readable: {resolved}")

        # 4. Check for root drive / root filesystem prohibition
        # Do not allow scanning C:\ or D:\ or /
        if len(resolved.parts) <= 1:
            raise SecurityValidationError(
                f"Cannot register root drive or system root directly: {resolved}"
            )

        resolved_str_lower = str(resolved).lower()

        # 5. Check against prohibited system paths
        for prohibited in cls.PROHIBITED_SYSTEM_PATTERNS:
            if resolved_str_lower == prohibited or resolved_str_lower.startswith(prohibited + os.sep):
                raise SecurityValidationError(
                    f"Access denied: Prohibited system directory '{resolved}'"
                )

        # 6. Check against CareerCrew internal data directories
        # Never allow scanning the database or embeddings directories
        careercrew_data = Path(settings.DATA_DIR).resolve()
        careercrew_chroma = Path(settings.VECTOR_STORE_DIR).resolve()

        if cls._is_subpath_or_equal(resolved, careercrew_data):
            raise SecurityValidationError(
                f"Access denied: Cannot register internal data directory"
            )

        if cls._is_subpath_or_equal(resolved, careercrew_chroma):
            raise SecurityValidationError(
                f"Access denied: Cannot register internal vector store directory"
            )


        logger.info(f"Project path passed security validation: {resolved}")
        return resolved

    @classmethod
    def is_git_repository(cls, path: Path) -> bool:
        """Check if directory contains a .git folder or worktree."""
        git_dir = path / ".git"
        return git_dir.exists()

    @staticmethod
    def _is_subpath_or_equal(child: Path, parent: Path) -> bool:
        """Check if child is equal to or located within parent."""
        try:
            child.relative_to(parent)
            return True
        except ValueError:
            return False


path_validator = PathValidator()
