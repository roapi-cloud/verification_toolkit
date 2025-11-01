"""Batch runner for executing multiple verification jobs."""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List

from .config import Runbook
from .executor import JobExecutor
from .report import BatchReport, JobResult


class BatchRunner:
    """Runs multiple verification jobs in batch."""

    def __init__(self, runbook: Runbook, max_workers: int = 4):
        self.runbook = runbook
        self.max_workers = max_workers

    async def run_batch_async(self) -> BatchReport:
        """Run all jobs in the runbook asynchronously."""
        jobs = []
        for job_config in self.runbook.jobs:
            executor = JobExecutor(job_config)
            jobs.append(executor.execute())

        # Run all jobs concurrently
        results = await asyncio.gather(*jobs, return_exceptions=True)

        # Process results
        job_results = []
        for i, result in enumerate(results):
            job_config = self.runbook.jobs[i]
            if isinstance(result, Exception):
                job_result = JobResult(
                    job_id=job_config.id,
                    issue_url=job_config.issue_url,
                    success=False,
                    error=str(result),
                    result=None
                )
            else:
                job_result = JobResult(
                    job_id=job_config.id,
                    issue_url=job_config.issue_url,
                    success=True,
                    error=None,
                    result=result
                )
            job_results.append(job_result)

        return BatchReport(
            runbook_name=self.runbook.name,
            total_jobs=len(job_results),
            successful_jobs=sum(1 for r in job_results if r.success),
            failed_jobs=sum(1 for r in job_results if not r.success),
            results=job_results
        )

    def run_batch_sync(self) -> BatchReport:
        """Run all jobs in the runbook synchronously."""
        job_results = []

        for job_config in self.runbook.jobs:
            try:
                executor = JobExecutor(job_config)
                result = executor.execute_sync()
                job_result = JobResult(
                    job_id=job_config.id,
                    issue_url=job_config.issue_url,
                    success=result.success,
                    error=None,
                    result=result
                )
            except Exception as e:
                job_result = JobResult(
                    job_id=job_config.id,
                    issue_url=job_config.issue_url,
                    success=False,
                    error=str(e),
                    result=None
                )
            job_results.append(job_result)

        return BatchReport(
            runbook_name=self.runbook.name,
            total_jobs=len(job_results),
            successful_jobs=sum(1 for r in job_results if r.success),
            failed_jobs=sum(1 for r in job_results if not r.success),
            results=job_results
        )

    def run_batch_parallel(self) -> BatchReport:
        """Run jobs in parallel using thread pool."""
        job_results = []

        def run_job(job_config):
            try:
                executor = JobExecutor(job_config)
                result = executor.execute_sync()
                return JobResult(
                    job_id=job_config.id,
                    issue_url=job_config.issue_url,
                    success=result.success,
                    error=None,
                    result=result
                )
            except Exception as e:
                return JobResult(
                    job_id=job_config.id,
                    issue_url=job_config.issue_url,
                    success=False,
                    error=str(e),
                    result=None
                )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(run_job, job) for job in self.runbook.jobs]
            for future in futures:
                job_results.append(future.result())

        return BatchReport(
            runbook_name=self.runbook.name,
            total_jobs=len(job_results),
            successful_jobs=sum(1 for r in job_results if r.success),
            failed_jobs=sum(1 for r in job_results if not r.success),
            results=job_results
        )