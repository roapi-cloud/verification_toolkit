"""GitHub-aware verification helpers exposed as a standalone toolkit."""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests
from git import Repo

from .interfaces import EvaluationResult, VerificationAgent

LOGGER = logging.getLogger(__name__)
DEFAULT_RUNTIME_DIR = Path(os.environ.get("LINGXI_RUNTIME_DIR", Path.home() / ".lingxi" / "runtime"))
DEFAULT_REQUEST_TIMEOUT = float(os.environ.get("LINGXI_GITHUB_TIMEOUT", "30"))


@dataclass(slots=True)
class GitHubIssueContext:
    """Concrete repository context produced by :class:`GitHubIssuePreparer`."""

    issue_url: str
    owner: str
    project: str
    issue_number: str
    repo_path: str
    current_commit: str
    closing_commit: Optional[str]
    issue_description: Optional[str]

    def as_dict(self) -> dict[str, Optional[str]]:
        """Return a JSON-serialisable representation of the context."""

        return {
            "issue_url": self.issue_url,
            "owner": self.owner,
            "project": self.project,
            "issue_number": self.issue_number,
            "repo_path": self.repo_path,
            "current_commit": self.current_commit,
            "closing_commit": self.closing_commit,
            "issue_description": self.issue_description,
        }


class GitHubIssuePreparer:
    """Prepare GitHub repositories for verification workflows."""

    def __init__(
        self,
        runtime_dir: str | os.PathLike[str] | None = None,
        github_token: Optional[str] = None,
        request_timeout: float = DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        self.runtime_dir = Path(runtime_dir) if runtime_dir else DEFAULT_RUNTIME_DIR
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.request_timeout = request_timeout

    def prepare(self, issue_url: str, checkout_parent: bool = True) -> GitHubIssueContext:
        """Produce a :class:`GitHubIssueContext` for the given issue URL."""

        owner, project, issue_number = self._parse_issue_url(issue_url)
        if not owner:
            raise ValueError(f"Invalid GitHub issue URL: {issue_url}")

        repo_path = self._materialise_repository(owner, project)
        repo = Repo(repo_path)
        self._reset_repository(repo)

        issue_description = self._fetch_issue_description(owner, project, issue_number)
        closing_commit = self._fetch_closing_commit(owner, project, issue_number)
        current_commit = repo.commit().hexsha

        if closing_commit:
            try:
                repo.git.checkout(closing_commit)
                current_commit = repo.commit().hexsha
                if checkout_parent and repo.commit().parents:
                    repo.git.checkout(repo.commit().parents[0].hexsha)
                    current_commit = repo.commit().hexsha
            except Exception as exc:  # pragma: no cover - defensive logging
                LOGGER.warning(
                    "Unable to checkout closing commit %s for %s/%s: %s",
                    closing_commit,
                    owner,
                    project,
                    exc,
                )

        self._reset_repository(repo)

        return GitHubIssueContext(
            issue_url=issue_url,
            owner=owner,
            project=project,
            issue_number=issue_number,
            repo_path=str(repo_path),
            current_commit=repo.commit().hexsha,
            closing_commit=closing_commit,
            issue_description=issue_description,
        )

    def run_with_agent(
        self,
        issue_url: str,
        agent: VerificationAgent,
        checkout_parent: bool = True,
    ) -> EvaluationResult:
        """Shortcut to prepare the repo then invoke the supplied agent."""

        context = self.prepare(issue_url, checkout_parent=checkout_parent)
        return agent.run_verification(context)

    def _parse_issue_url(self, issue_url: str) -> tuple[str, str, str]:
        pattern = r"https://github\.com/([^/]+)/([^/]+)/issues/(\d+)"
        match = re.match(pattern, issue_url)
        if not match:
            return "", "", ""
        return match.group(1), match.group(2), match.group(3)

    def _materialise_repository(self, owner: str, project: str) -> Path:
        repo_path = self.runtime_dir / owner / project
        if not repo_path.exists():
            git_url = f"https://github.com/{owner}/{project}"
            LOGGER.info("Cloning %s into %s", git_url, repo_path)
            repo_path.parent.mkdir(parents=True, exist_ok=True)
            Repo.clone_from(git_url, repo_path)
        return repo_path

    def _reset_repository(self, repo: Repo) -> None:
        repo.git.reset("--hard")
        repo.git.clean("-xdf")

    def _request_headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        token = self.github_token
        if token:
            headers["Authorization"] = f"token {token}"
        return headers

    def _fetch_issue_description(self, owner: str, project: str, issue_number: str) -> Optional[str]:
        issue_api_url = f"https://api.github.com/repos/{owner}/{project}/issues/{issue_number}"
        response = requests.get(
            issue_api_url,
            headers=self._request_headers(),
            timeout=self.request_timeout,
        )
        if response.status_code == 200:
            return response.json().get("body")
        LOGGER.warning(
            "Unable to fetch issue description for %s/%s#%s (status %s)",
            owner,
            project,
            issue_number,
            response.status_code,
        )
        return None

    def _fetch_issue_events(self, owner: str, project: str, issue_number: str) -> list[dict[str, object]]:
        event_url = f"https://api.github.com/repos/{owner}/{project}/issues/{issue_number}/events"
        response = requests.get(
            event_url,
            headers=self._request_headers(),
            timeout=self.request_timeout,
        )
        response.raise_for_status()
        return response.json()

    def _fetch_closing_commit(self, owner: str, project: str, issue_number: str) -> Optional[str]:
        try:
            events = self._fetch_issue_events(owner, project, issue_number)
        except requests.HTTPError as exc:
            LOGGER.warning(
                "Unable to fetch issue events for %s/%s#%s: %s",
                owner,
                project,
                issue_number,
                exc,
            )
            return None

        for event in events:
            if event.get("event") == "closed":
                if commit_id := event.get("commit_id"):
                    return str(commit_id)
                pull_request = event.get("pull_request")
                if isinstance(pull_request, dict) and pull_request.get("url"):
                    LOGGER.info(
                        "Issue %s/%s#%s closed via PR %s",
                        owner,
                        project,
                        issue_number,
                        pull_request["url"],
                    )
        return None


class GitHubEvaluationRunner:
    """High-level helper that wires a verification agent with the preparer."""

    def __init__(self, preparer: GitHubIssuePreparer | None = None) -> None:
        self.preparer = preparer or GitHubIssuePreparer()

    def run(
        self,
        issue_url: str,
        agent: VerificationAgent,
        checkout_parent: bool = True,
    ) -> EvaluationResult:
        """Prepare the repository then hand off to the provided agent."""

        return self.preparer.run_with_agent(issue_url, agent, checkout_parent=checkout_parent)
