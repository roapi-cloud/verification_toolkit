"""Configuration models for batch workflow runbooks."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class JobConfig:
    """Configuration for a single verification job."""

    id: str
    type: str  # "github" or "swerex"
    agent: str  # Agent name to use

    # GitHub-specific fields
    issue_url: Optional[str] = None

    # SWEREX-specific fields
    instance_id: Optional[str] = None
    checkout_commit: Optional[str] = None

    # Additional custom fields
    extra: Optional[Dict[str, Any]] = None
    agent_kwargs: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.type == "github" and not self.issue_url:
            raise ValueError(f"Job {self.id}: issue_url required for github type")
        if self.type == "swerex" and not self.instance_id:
            raise ValueError(f"Job {self.id}: instance_id required for swerex type")


@dataclass
class Runbook:
    """Configuration for a batch workflow run."""

    name: str
    jobs: List[JobConfig]
    max_parallel: int = 1
    output_dir: str = "./runs/batch_output"

    def __post_init__(self):
        self.output_dir = str(Path(self.output_dir).resolve())

    @classmethod
    def from_yaml(cls, path: str | Path) -> Runbook:
        """Load runbook from YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data)

    @classmethod
    def from_json(cls, path: str | Path) -> Runbook:
        """Load runbook from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Runbook:
        """Create runbook from dictionary."""
        jobs_data = data.get("jobs", [])
        jobs = [JobConfig(**job) for job in jobs_data]
        return cls(
            name=data.get("name", "unnamed-runbook"),
            jobs=jobs,
            max_parallel=data.get("max_parallel", 1),
            output_dir=data.get("output_dir", "./runs/batch_output"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert runbook to dictionary."""
        return {
            "name": self.name,
            "jobs": [job.__dict__ for job in self.jobs],
            "max_parallel": self.max_parallel,
            "output_dir": self.output_dir,
        }


def load_runbook(path: str | Path) -> Runbook:
    """Load a runbook from YAML or JSON file."""
    path = Path(path)
    if path.suffix.lower() in ('.yaml', '.yml'):
        return Runbook.from_yaml(path)
    elif path.suffix.lower() == '.json':
        return Runbook.from_json(path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")