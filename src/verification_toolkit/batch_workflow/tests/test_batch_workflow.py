"""Tests for batch workflow."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ..config import JobConfig, Runbook
from ..executor import JobExecutor
from ..report import BatchReport, JobResult
from ..runner import BatchRunner
from verification_toolkit import EvaluationResult


class TestJobExecutor:
    """Test JobExecutor."""

    @patch('verification_toolkit.batch_workflow.executor.GitHubContextProvider')
    @patch('verification_toolkit.batch_workflow.agents.registry.get_agent')
    def test_execute_sync(self, mock_get_agent, mock_context_provider_class):
        """Test synchronous job execution."""
        # Setup mocks
        mock_agent = Mock()
        mock_agent.run_verification.return_value = EvaluationResult(
            success=True,
            details="Test passed with score 0.95",
            artifacts={"test": "passed", "score": 0.95}
        )
        mock_get_agent.return_value = mock_agent

        mock_context_provider = Mock()
        mock_context = Mock()
        mock_context.repo_path = "/tmp/test-repo"
        mock_context.owner = "test"
        mock_context.project = "repo"
        mock_context.issue_number = "1"
        mock_context.current_commit = "abc123"
        mock_context.closing_commit = None
        mock_context.issue_description = "Test issue"
        async def mock_prepare_context(job_config):
            return mock_context
        mock_context_provider.prepare_context = mock_prepare_context
        mock_context_provider_class.return_value = mock_context_provider

        # Create executor
        config = JobConfig(
            id="test-job",
            type="github",
            agent="demo",
            issue_url="https://github.com/test/repo/issues/1",
            agent_kwargs={}
        )
        executor = JobExecutor(config)

        # Execute
        result = executor.execute_sync()

        # Verify
        assert result.success is True
        assert "Repository: test/repo" in result.details


class TestBatchRunner:
    """Test BatchRunner."""

    def test_run_batch_sync(self):
        """Test synchronous batch execution."""
        # Create runbook
        runbook = Runbook(
            name="test-runbook",
            jobs=[
                JobConfig(
                    id="job1",
                    type="github",
                    agent="demo",
                    issue_url="https://github.com/test/repo/issues/1",
                    agent_kwargs={}
                ),
                JobConfig(
                    id="job2",
                    type="github",
                    agent="demo",
                    issue_url="https://github.com/test/repo/issues/2",
                    agent_kwargs={}
                )
            ]
        )

        # Mock executor
        with patch('verification_toolkit.batch_workflow.runner.JobExecutor') as mock_executor_class:
            mock_executor1 = Mock()
            mock_executor1.execute_sync.return_value = EvaluationResult(
                success=True,
                details="Test successful",
                artifacts={"score": 1.0}
            )
            mock_executor2 = Mock()
            mock_executor2.execute_sync.return_value = EvaluationResult(
                success=False,
                details="Test failed",
                artifacts={"error": "failed"}
            )

            mock_executor_class.side_effect = [mock_executor1, mock_executor2]

            runner = BatchRunner(runbook)
            report = runner.run_batch_sync()

            assert isinstance(report, BatchReport)
            assert report.runbook_name == "test-runbook"
            assert report.total_jobs == 2
            assert report.successful_jobs == 1
            assert report.failed_jobs == 1
            assert len(report.results) == 2

    def test_run_batch_parallel(self):
        """Test parallel batch execution."""
        # Similar to sync test but with parallel execution
        runbook = Runbook(
            name="test-runbook",
            jobs=[
                JobConfig(
                    id="job1",
                    type="github",
                    agent="demo",
                    issue_url="https://github.com/test/repo/issues/1",
                    agent_kwargs={}
                )
            ]
        )

        with patch('verification_toolkit.batch_workflow.runner.JobExecutor') as mock_executor_class:
            mock_executor = Mock()
            mock_executor.execute_sync.return_value = EvaluationResult(
                success=True,
                details="Test successful",
                artifacts={"score": 1.0}
            )
            mock_executor_class.return_value = mock_executor

            runner = BatchRunner(runbook)
            report = runner.run_batch_parallel()

            assert isinstance(report, BatchReport)
            assert report.total_jobs == 1
            assert report.successful_jobs == 1
            assert report.failed_jobs == 0


class TestBatchReport:
    """Test BatchReport."""

    def test_success_rate(self):
        """Test success rate calculation."""
        report = BatchReport(
            runbook_name="test",
            total_jobs=4,
            successful_jobs=3,
            failed_jobs=1,
            results=[]
        )
        assert report.success_rate == 75.0

    def test_success_rate_empty(self):
        """Test success rate with no jobs."""
        report = BatchReport(
            runbook_name="test",
            total_jobs=0,
            successful_jobs=0,
            failed_jobs=0,
            results=[]
        )
        assert report.success_rate == 0.0