"""Job executor for running verification jobs."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from verification_toolkit import EvaluationResult, VerificationAgent

from .agents.registry import get_agent
from .config import JobConfig
from .context.github import GitHubContextProvider


class JobExecutor:
    """Executes a single verification job."""

    def __init__(self, config: JobConfig):
        self.config = config
        self.context_provider = GitHubContextProvider()
        self.agent: VerificationAgent = get_agent(
            config.agent,
            **(config.agent_kwargs or {})
        )

    async def execute(self) -> EvaluationResult:
        """Execute the job and return results."""
        # Prepare context
        context = await self.context_provider.prepare_context(
            self.config
        )

        # Run verification
        result = self.agent.run_verification(context)

        return result

    def execute_sync(self) -> EvaluationResult:
        """Synchronous wrapper for execute."""
        return asyncio.run(self.execute())