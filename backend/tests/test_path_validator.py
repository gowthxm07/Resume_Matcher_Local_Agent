"""
Unit tests for safe local filesystem path validation.
Verifies path traversal defenses, root directory blocks, and system directory protections.
"""

import os
import tempfile
import pytest
from app.services.path_validator import PathValidator, PathValidationError


def test_valid_temporary_directory():
    """Verify that a standard user-created directory passes validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        res = PathValidator.validate_project_path(tmpdir)
        assert res.exists()
        assert res.is_dir()


def test_nonexistent_directory_rejected():
    """Verify non-existent paths raise validation error."""
    with pytest.raises(PathValidationError) as exc:
        PathValidator.validate_project_path("D:\\NonExistent_Directory_123456789")
    assert "does not exist" in str(exc.value)


def test_file_instead_of_directory_rejected():
    """Verify that passing a file instead of a directory is rejected."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"content")
        f_path = f.name
    try:
        with pytest.raises(PathValidationError) as exc:
            PathValidator.validate_project_path(f_path)
        assert "is not a directory" in str(exc.value)
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)


def test_root_drive_rejected():
    """Verify root drives like C:\\ or D:\\ are explicitly rejected."""
    drive = "C:\\" if os.name == "nt" else "/"
    with pytest.raises(PathValidationError) as exc:
        PathValidator.validate_project_path(drive)
    assert "root" in str(exc.value).lower()




def test_windows_system_directories_rejected():
    """Verify system directories like Windows or System32 are rejected."""
    if os.name == "nt":
        windir = os.environ.get("SystemRoot", "C:\\Windows")
        if os.path.exists(windir):
            with pytest.raises(PathValidationError) as exc:
                PathValidator.validate_project_path(windir)
            assert "Forbidden" in str(exc.value) or "system directory" in str(exc.value)


def test_internal_database_path_rejected():
    """Verify internal CareerCrew database directory is rejected."""
    from app.core.config import settings
    with pytest.raises(PathValidationError) as exc:
        PathValidator.validate_project_path(str(settings.DATA_DIR))
    assert "Forbidden" in str(exc.value) or "internal" in str(exc.value).lower()



def test_relative_path_normalization():
    """Verify relative paths are canonicalized safely."""
    with tempfile.TemporaryDirectory() as tmpdir:
        sub = os.path.join(tmpdir, "child")
        os.makedirs(sub, exist_ok=True)
        # Using .. traversal that stays within tmpdir
        rel = os.path.join(sub, "..")
        res = PathValidator.validate_project_path(rel)
        assert res.resolve() == res
