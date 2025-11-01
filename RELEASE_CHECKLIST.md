# Verification Toolkit Release Checklist

## Pre-Release Checks

- [x] All tests pass: `pytest`
- [x] Code formatting: `black .` (if using black)
- [x] Type checking: `mypy src/` (if using mypy)
- [x] Documentation is up to date
- [x] Version number updated in `pyproject.toml`
- [x] Changelog updated (if applicable)

## Repository Setup

- [x] Git repository initialized
- [x] `.gitignore` configured
- [x] Initial commit created
- [x] GitHub repository created
- [x] Code pushed to GitHub
- [x] Default branch set to `main`
- [x] Repository description set
- [x] Repository topics/tags added (python, verification, github, batch-processing)

## GitHub Repository Configuration

- [ ] Repository visibility set (public/private)
- [ ] README.md renders correctly on GitHub
- [ ] Repository topics: `python`, `verification`, `github-api`, `batch-processing`, `swe-bench`
- [ ] Repository website: Link to documentation (if any)
- [ ] Repository license: MIT
- [ ] Branch protection rules (if needed)
- [ ] Issues enabled
- [ ] Wiki disabled (use README/docs)
- [ ] Projects disabled (for now)
- [ ] Sponsorship disabled

## Package Publishing

- [ ] PyPI account configured
- [ ] Package builds correctly: `python -m build`
- [ ] Package can be installed: `pip install dist/*.whl`
- [ ] Package imports correctly
- [ ] CLI tools work: `verification-demo --help`, `batch-workflow --help`

## Post-Release

- [ ] Release created on GitHub
- [ ] Release notes written
- [ ] Package published to PyPI: `twine upload dist/*`
- [ ] Announcement made (if applicable)
- [ ] Documentation website updated (if applicable)