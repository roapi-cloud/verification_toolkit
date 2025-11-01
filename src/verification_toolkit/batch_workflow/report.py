"""Batch execution reports."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from verification_toolkit import EvaluationResult


@dataclass
class JobResult:
    """Result of a single job execution."""
    job_id: str
    issue_url: str
    success: bool
    error: Optional[str]
    result: Optional[EvaluationResult]


@dataclass
class BatchReport:
    """Report for a batch execution."""
    runbook_name: str
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    results: List[JobResult]

    @property
    def success_rate(self) -> float:
        """Calculate success rate as a percentage."""
        if self.total_jobs == 0:
            return 0.0
        return (self.successful_jobs / self.total_jobs) * 100.0

    def print_summary(self) -> None:
        """Print a summary of the batch execution."""
        print(f"Batch Report: {self.runbook_name}")
        print(f"Total Jobs: {self.total_jobs}")
        print(f"Successful: {self.successful_jobs}")
        print(f"Failed: {self.failed_jobs}")
        print(".1f")
        print("\nJob Details:")
        for result in self.results:
            status = "✓" if result.success else "✗"
            print(f"{status} {result.job_id}: {result.issue_url}")
            if result.error:
                print(f"  Error: {result.error}")