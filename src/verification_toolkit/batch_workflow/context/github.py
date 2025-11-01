"""GitHub context provider for batch workflow."""

from __future__ import annotations

from typing import Protocol

from verification_toolkit import GitHubIssuePreparer, GitHubIssueContext


class ContextProvider(Protocol):
    """Protocol for providing repository context."""

    def prepare_context(self, job_config) -> GitHubIssueContext:
        """Prepare repository context for the given job."""


class GitHubContextProvider:
    """Context provider for GitHub issues."""

    def __init__(self, preparer: GitHubIssuePreparer | None = None):
        self.preparer = preparer or GitHubIssuePreparer()

    def prepare_context(self, job_config) -> GitHubIssueContext:
        """Prepare GitHub issue context."""
        if not job_config.issue_url:
            raise ValueError(f"Job {job_config.id} missing issue_url")
        return self.preparer.prepare(job_config.issue_url)