"""Minimal demo agent showcasing the Verification Toolkit."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from verification_toolkit import EvaluationResult, GitHubEvaluationRunner, VerificationAgent


@dataclass
class DemoAgentConfig:
    command: str = "pytest"
    extra_args: Optional[list[str]] = None


class DemoVerificationAgent(VerificationAgent):
    """A toy agent that simply prints repo info and pretends tests passed."""

    def __init__(self, config: DemoAgentConfig | None = None) -> None:
        self.config = config or DemoAgentConfig()

    def run_verification(self, context) -> EvaluationResult:
        repo_path = Path(context.repo_path)
        summary = [
            f"Repository: {context.owner}/{context.project}",
            f"Issue #{context.issue_number}",
            f"Current commit: {context.current_commit}",
        ]
        if context.closing_commit:
            summary.append(f"Closing commit: {context.closing_commit}")
        if context.issue_description:
            summary.append("Description:\n" + context.issue_description[:200] + "...")

        summary.append(f"Repo location: {repo_path}")
        summary.append("Pretending to run tests... (skipped in demo)")

        return EvaluationResult(success=True, details="\n".join(summary), artifacts={"repo_path": str(repo_path)})


def main(issue_url: str) -> EvaluationResult:
    agent = DemoVerificationAgent()
    runner = GitHubEvaluationRunner()
    return runner.run(issue_url, agent)


def cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run the demo verification agent")
    parser.add_argument("issue_url", help="GitHub issue URL")
    args = parser.parse_args()

    result = main(args.issue_url)
    print("Success:" if result.success else "Failure:", result.details)


if __name__ == "__main__":
    cli()
