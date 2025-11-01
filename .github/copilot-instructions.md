# Copilot Instructions for Verification Toolkit

## Project Overview

This is a standalone toolkit for running verification workflows against GitHub repositories/issues. Extracted from the Lingxi agent stack, it follows a protocol-based architecture where any agent implementing `VerificationAgent` can run automated checks.

## Key Architecture Patterns

### Protocol-Based Agent Interface
- All verification agents must implement `VerificationAgent.run_verification(context) -> EvaluationResult`
- `RepositoryContext` provides standardized access to repo state (path, commits, issue details)
- Return `EvaluationResult(success=bool, details=str, artifacts=dict)` for all agent outputs

### Core Components Structure
- `src/verification_toolkit/interfaces.py` - Protocol definitions (modify these carefully)
- `src/verification_toolkit/github.py` - GitHub-specific implementation with repo preparation
- `src/verification_toolkit/batch_workflow/` - Parallel job execution system
- `examples/demo_agent.py` - Reference implementation pattern

### GitHub Workflow Pattern
```python
# Standard verification flow
preparer = GitHubIssuePreparer()  # Handles cloning, checkout, API calls
context = preparer.prepare(issue_url, checkout_parent=True)  # Sets up repo state
result = agent.run_verification(context)  # Agent does the work
```

## Development Conventions

### Environment Configuration
- Use `LINGXI_RUNTIME_DIR` (default `~/.lingxi/runtime`) for repo clones
- `GITHUB_TOKEN` for authenticated API access
- `LINGXI_GITHUB_TIMEOUT` for request timeouts
- All paths should be absolute; use `Path.resolve()` in config classes

### Testing Patterns
- Tests manually add `src/` to `sys.path` (see `tests/test_interfaces.py`)
- Use `pytest` for all testing
- Focus on testing protocols and data structures, not external integrations

### Console Scripts
- `verification-demo` - Runs demo agent CLI
- `batch-workflow` - Runs batch job processing
- Both defined in `pyproject.toml` project.scripts section

## Batch Workflow System

### Runbook Configuration
- YAML/JSON configs define jobs with `id`, `type` (github/swerex), `agent`, and target info
- `JobConfig` validates required fields per job type
- `load_runbook(path)` auto-detects format by extension

### Agent Registry Pattern
- Agents register by name in `batch_workflow/agents/registry.py`
- Jobs reference agents by string name, not class imports
- Demo agent shows the registration pattern

## Integration Points

### External Dependencies
- `requests` for GitHub API calls with timeout/auth headers
- `GitPython` for repository operations (clone, checkout, reset)
- Minimal surface area by design - avoid adding heavy dependencies

### Repository State Management
- Always `git reset --hard && git clean -xdf` before agent execution
- Checkout parent commit of closing commit when `checkout_parent=True`
- Handle missing closing commits gracefully (issue might be open)

## Adding New Features

### New Agent Types
1. Implement `VerificationAgent` protocol
2. Register in `batch_workflow/agents/registry.py`
3. Add to demo runbook for testing

### New Job Types
1. Extend `JobConfig` with required fields
2. Add validation in `__post_init__`
3. Update `JobExecutor` to handle the new type

### API Extensions
- Keep `interfaces.py` stable - breaking changes affect all agents
- Add new optional fields to `EvaluationResult.artifacts` for extensibility
- Use composition over inheritance for new context types