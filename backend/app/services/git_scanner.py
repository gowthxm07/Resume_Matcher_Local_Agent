"""
Safe Git repository scanner for CareerCrew.
Uses GitPython strictly in read-only mode without executing arbitrary shell strings.
Extracts commit history, author statistics, branch names, and HEAD metadata.
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import git
from git.exc import InvalidGitRepositoryError, NoSuchPathError, GitCommandError
from app.core.logging import logger
from app.schemas.evidence import GitMetadata, GitCommitSummary


def sanitize_remote_url(url: Optional[str]) -> Optional[str]:
    """
    Remove embedded authentication tokens or credentials from git remote URLs.
    Example: https://oauth2:token123@github.com/user/repo.git -> https://github.com/user/repo.git
    """
    if not url:
        return None
    return re.sub(r"://[^@]+@", "://", url)


class GitScanner:
    """
    Read-only Git metadata and history scanner.
    Safely inspects local repositories without checking out branches, running hooks, or modifying state.
    """

    @staticmethod
    def _sanitize_remote_url(url: Optional[str]) -> Optional[str]:
        return sanitize_remote_url(url)

    @classmethod
    def scan_repository(
        cls, repo_path: Union[str, Path], max_recent_commits: int = 15
    ) -> GitMetadata:
        """
        Inspect a repository directory and extract structured Git metadata.
        Falls back cleanly if the directory is not a Git repository or has 0 commits.
        """
        path = Path(repo_path)
        repo_name = path.name

        try:
            repo = git.Repo(path, search_parent_directories=False)
        except (InvalidGitRepositoryError, NoSuchPathError):
            logger.info(f"Directory '{path}' is not a Git repository; treating as non-git project.")
            return GitMetadata(
                repo_name=repo_name,
                is_git_repo=False,
            )
        except Exception as exc:
            logger.warning(f"Error accessing git repo at '{path}': {exc}")
            return GitMetadata(
                repo_name=repo_name,
                is_git_repo=False,
            )

        try:
            # 1. Branch name
            branch_name = None
            try:
                if not repo.head.is_detached:
                    branch_name = repo.active_branch.name
                else:
                    branch_name = "DETACHED_HEAD"
            except (TypeError, ValueError, GitCommandError):
                branch_name = "unknown"

            # 2. Check if repository is empty (has no commits)
            try:
                has_commits = bool(repo.heads) or bool(list(repo.iter_commits(max_count=1)))
            except (GitCommandError, ValueError):
                has_commits = False

            if not has_commits:
                return GitMetadata(
                    repo_name=repo_name,
                    is_git_repo=True,
                    branch=branch_name or "main",
                    commit_count=0,
                )

            # 3. Remote URL
            remote_url = None
            try:
                if repo.remotes:
                    origin = repo.remotes.origin if "origin" in repo.remotes else repo.remotes[0]
                    remote_url = sanitize_remote_url(origin.url)
            except Exception:
                pass

            # 4. HEAD commit
            head_commit_hash = None
            try:
                head_commit = repo.head.commit
                head_commit_hash = head_commit.hexsha
            except Exception:
                head_commit_hash = None

            # 5. Commit statistics and recent commits
            recent_commits: List[GitCommitSummary] = []
            author_stats: Dict[str, int] = {}
            first_commit_date: Optional[str] = None
            last_commit_date: Optional[str] = None
            total_commit_count = 0

            try:
                all_commits = list(repo.iter_commits(max_count=200))
                total_commit_count = len(all_commits)

                if all_commits:
                    last_commit = all_commits[0]
                    last_commit_date = datetime.fromtimestamp(
                        last_commit.committed_date, tz=timezone.utc
                    ).isoformat()

                    first_commit = all_commits[-1]
                    first_commit_date = datetime.fromtimestamp(
                        first_commit.committed_date, tz=timezone.utc
                    ).isoformat()

                    for c in all_commits:
                        author_name = c.author.name or "Unknown"
                        author_stats[author_name] = author_stats.get(author_name, 0) + 1

                    for c in all_commits[:max_recent_commits]:
                        changed_files = []
                        additions = 0
                        deletions = 0
                        try:
                            stats = c.stats.total
                            additions = stats.get("insertions", 0)
                            deletions = stats.get("deletions", 0)
                            changed_files = list(c.stats.files.keys())[:10]
                        except Exception:
                            pass

                        recent_commits.append(
                            GitCommitSummary(
                                commit_hash=c.hexsha,
                                date=datetime.fromtimestamp(
                                    c.committed_date, tz=timezone.utc
                                ).isoformat(),
                                author=c.author.name or "Unknown",
                                subject=c.summary[:120] if c.summary else "No commit message",
                                changed_file_count=len(changed_files),
                                additions=additions,
                                deletions=deletions,
                                changed_files=changed_files,
                            )
                        )

            except Exception as exc:
                logger.warning(f"Error parsing commits for '{path}': {exc}")

            return GitMetadata(
                repo_name=repo_name,
                is_git_repo=True,
                branch=branch_name,
                head_commit=head_commit_hash,
                commit_count=total_commit_count,
                first_commit_date=first_commit_date,
                last_commit_date=last_commit_date,
                remote_url=remote_url,
                author_stats=author_stats,
                recent_commits=recent_commits,
            )
        finally:
            try:
                repo.close()
            except Exception:
                pass

    @classmethod
    def extract_commit_history(
        cls, repo_path: Union[str, Path], max_commits: int = 15
    ) -> List[GitCommitSummary]:
        """
        Extract recent commit history without diff blobs.
        """
        path = Path(repo_path)
        try:
            repo = git.Repo(path, search_parent_directories=False)
        except Exception as exc:
            logger.warning(f"Error opening repo at '{path}': {exc}")
            return []

        try:
            commits = list(repo.iter_commits(max_count=max_commits))
            results = []
            for c in commits:
                changed_files = []
                additions = 0
                deletions = 0
                try:
                    stats = c.stats.total
                    additions = stats.get("insertions", 0)
                    deletions = stats.get("deletions", 0)
                    changed_files = list(c.stats.files.keys())[:10]
                except Exception:
                    pass

                results.append(
                    GitCommitSummary(
                        commit_hash=c.hexsha,
                        date=datetime.fromtimestamp(
                            c.committed_date, tz=timezone.utc
                        ).isoformat(),
                        author=c.author.name or "Unknown",
                        subject=c.summary[:120] if c.summary else "No commit message",
                        changed_file_count=len(changed_files),
                        additions=additions,
                        deletions=deletions,
                        changed_files=changed_files,
                    )
                )
            return results
        except Exception as exc:
            logger.warning(f"Error extracting commits for '{path}': {exc}")
            return []
        finally:
            try:
                repo.close()
            except Exception:
                pass


git_scanner = GitScanner()
