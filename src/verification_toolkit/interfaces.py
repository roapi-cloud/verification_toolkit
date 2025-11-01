"""Public interfaces for running repository verification workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol


@dataclass(slots=True)
class EvaluationResult:
    """Outcome returned by a verification-capable agent."""

    success: bool
    details: str
    artifacts: Dict[str, Any] | None = None


class VerificationAgent(Protocol):
    """Protocol that any evaluation-capable agent should implement."""

    def run_verification(self, context: "RepositoryContext") -> EvaluationResult:
        """Execute verification for the provided repository context."""


class RepositoryContext(Protocol):
    """Minimal view of the repository state used during verification."""

    @property
    def issue_url(self) -> str:  # pragma: no cover - protocol definition
        ...

    @property
    def owner(self) -> str:  # pragma: no cover - protocol definition
        ...

    @property
    def project(self) -> str:  # pragma: no cover - protocol definition
        ...

    @property
    def issue_number(self) -> str:  # pragma: no cover - protocol definition
        ...

    @property
    def repo_path(self) -> str:  # pragma: no cover - protocol definition
        ...

    @property
    def current_commit(self) -> str:  # pragma: no cover - protocol definition
        ...

    @property
    def closing_commit(self) -> str | None:  # pragma: no cover - protocol definition
        ...

    @property
    def issue_description(self) -> str | None:  # pragma: no cover - protocol definition
        ...
