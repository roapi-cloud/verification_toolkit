# Verification Toolkit

A self-contained GitHub issue verification toolkit extracted from the Lingxi
project. It prepares repositories for evaluation and defines a tiny protocol so
any autonomous agent can run verification workflows without the rest of the
Lingxi stack.

## Features

- Minimal dependency surface (`requests` and `GitPython`).
- Flexible runtime directory configuration via environment variables.
- Protocol-based agent interface (`VerificationAgent`).
- Ready-to-use GitHub preparer and evaluation runner.
- **Batch workflow support** for running multiple verification jobs.

## Installation

```bash
pip install .
```

Use `pip install .[dev]` to grab optional testing dependencies.

## Quickstart

```python
from verification_toolkit import GitHubEvaluationRunner, EvaluationResult, VerificationAgent


class MyVerifier:
    def run_verification(self, context) -> EvaluationResult:
        # Perform your evaluation here using context.repo_path, etc.
        return EvaluationResult(success=True, details="Checks passed")


runner = GitHubEvaluationRunner()
result = runner.run("https://github.com/org/repo/issues/123", MyVerifier())
print(result)
```

## Batch Workflows

Run multiple verification jobs in batch:

```python
from verification_toolkit.batch_workflow import BatchRunner, load_runbook

# Load configuration
runbook = load_runbook("runbook.yaml")

# Create and run batch
runner = BatchRunner(runbook)
report = runner.run_batch_sync()  # or run_batch_parallel()
report.print_summary()
```

Or use the CLI:

```bash
batch-workflow runbook.yaml --mode parallel --max-workers 4
```

## Demo Agent

A minimal end-to-end example lives under `examples/demo_agent.py`. After
installing the package (editable install recommended during development), run:

```bash
python verification_toolkit/examples/demo_agent.py https://github.com/octocat/Hello-World/issues/1
```

This downloads the repository to `$LINGXI_RUNTIME_DIR`, prints basic context
information, and pretends to execute tests. You can extend `DemoVerificationAgent`
to run real checks or integrate with your own pipeline. A console script named
`verification-demo` is also provided once the package is installed.

## Environment Variables

- `LINGXI_RUNTIME_DIR` – directory where repositories will be cloned
  (defaults to `~/.lingxi/runtime`).
- `GITHUB_TOKEN` – optional token for authenticated GitHub API access.
- `LINGXI_GITHUB_TIMEOUT` – request timeout in seconds (default `30`).

## Testing

```bash
pytest
```

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Commit your changes
7. Push to your fork
8. Create a Pull Request

## Publishing to GitHub

To publish this project as a new GitHub repository:

### Option 1: Using the Setup Script (Recommended)

1. Install GitHub CLI: `brew install gh` (macOS) or visit [cli.github.com](https://cli.github.com/)
2. Login to GitHub: `gh auth login`
3. Run the setup script: `./setup_github.sh`
4. Follow the prompts to create your repository

### Option 2: Manual Setup

1. Create a new repository on GitHub (don't initialize with README)
2. Add the remote: `git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git`
3. Push the code: `git push -u origin main`

### Option 3: Using GitHub CLI

```bash
# Create repository
gh repo create verification-toolkit --public --description "Standalone verification toolkit with batch workflow support"

# Push code
git push -u origin main
```
