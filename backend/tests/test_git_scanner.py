"""
Unit tests for the safe Git repository scanner.
Verifies git metadata extraction, commit summaries, remote sanitization,
and graceful handling of non-git directories without executing arbitrary shell commands.
"""

import os
import tempfile
import git
from app.services.git_scanner import GitScanner, git_scanner


def test_scan_non_git_directory():
    """Verify scanning a non-git directory returns is_git_repo=False safely."""
    with tempfile.TemporaryDirectory() as tmpdir:
        meta = git_scanner.scan_repository(tmpdir)
        assert meta.is_git_repo is False
        assert meta.branch is None
        assert meta.head_commit is None
        assert meta.commit_count == 0
        assert meta.recent_commits == []


def test_scan_initialized_git_repository():
    """Verify scanning a real local git repository extracts commit and branch metadata."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = git.Repo.init(tmpdir)
        try:
            repo.config_writer().set_value("user", "name", "Test Developer").release()
            repo.config_writer().set_value("user", "email", "dev@example.com").release()

            test_file = os.path.join(tmpdir, "README.md")
            with open(test_file, "w") as f:
                f.write("# Hello World\n")

            repo.index.add(["README.md"])
            commit = repo.index.commit("Initial test commit")
            commit_hash = commit.hexsha
        finally:
            repo.close()

        meta = git_scanner.scan_repository(tmpdir)
        assert meta.is_git_repo is True
        assert meta.head_commit == commit_hash
        assert meta.commit_count == 1
        assert "Test Developer" in meta.author_stats
        assert len(meta.recent_commits) == 1
        assert meta.recent_commits[0].subject == "Initial test commit"
        assert "README.md" in meta.recent_commits[0].changed_files


def test_remote_url_credential_sanitization():
    """Verify passwords, personal access tokens, and user credentials are removed from remote URLs."""
    raw_url = "https://oauth2:ghp_9948274928abcdef@github.com/user/private-repo.git"
    sanitized = git_scanner._sanitize_remote_url(raw_url)
    assert sanitized is not None
    assert "ghp_" not in sanitized
    assert "oauth2" not in sanitized
    assert "github.com/user/private-repo.git" in sanitized

    ssh_url = "git@github.com:user/repo.git"
    assert git_scanner._sanitize_remote_url(ssh_url) == "git@github.com:user/repo.git"


def test_extract_commit_history_limit():
    """Verify commit history extraction respects max_commits and handles pagination."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = git.Repo.init(tmpdir)
        try:
            repo.config_writer().set_value("user", "name", "Commiter").release()
            repo.config_writer().set_value("user", "email", "c@example.com").release()

            for i in range(5):
                fname = os.path.join(tmpdir, f"file_{i}.txt")
                with open(fname, "w") as f:
                    f.write(f"content {i}")
                repo.index.add([f"file_{i}.txt"])
                repo.index.commit(f"Commit #{i}")
        finally:
            repo.close()

        commits = git_scanner.extract_commit_history(tmpdir, max_commits=3)
        assert len(commits) == 3
        assert commits[0].subject == "Commit #4"
        assert commits[1].subject == "Commit #3"
        assert commits[2].subject == "Commit #2"
