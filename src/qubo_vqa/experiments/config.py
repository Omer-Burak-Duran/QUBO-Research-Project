"""Typed configuration loading for small reproducible experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(slots=True)
class ProblemConfig:
    """Problem-specific configuration."""

    name: str
    parameters: dict[str, object]


@dataclass(slots=True)
class SolverConfig:
    """Solver-specific configuration."""

    name: str
    parameters: dict[str, object]


@dataclass(slots=True)
class OutputConfig:
    """Output directory configuration."""

    directory: str = "data/results"
    tag: str = "run"


@dataclass(slots=True)
class ExperimentConfig:
    """Top-level experiment configuration."""

    experiment_name: str
    seed: int
    problem: ProblemConfig
    solver: SolverConfig
    output: OutputConfig


def load_experiment_config(path: str | Path) -> ExperimentConfig:
    """Load an experiment configuration from a YAML file."""
    raw_payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return ExperimentConfig(
        experiment_name=str(raw_payload["experiment_name"]),
        seed=int(raw_payload.get("seed", 0)),
        problem=ProblemConfig(
            name=str(raw_payload["problem"]["name"]),
            parameters=dict(raw_payload["problem"].get("parameters", {})),
        ),
        solver=SolverConfig(
            name=str(raw_payload["solver"]["name"]),
            parameters=dict(raw_payload["solver"].get("parameters", {})),
        ),
        output=OutputConfig(
            directory=str(raw_payload.get("output", {}).get("directory", "data/results")),
            tag=str(raw_payload.get("output", {}).get("tag", raw_payload["experiment_name"])),
        ),
    )
