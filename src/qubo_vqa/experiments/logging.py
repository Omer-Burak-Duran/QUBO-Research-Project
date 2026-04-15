"""Result serialization helpers for reproducible experiment folders."""

from __future__ import annotations

import platform
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from qubo_vqa.analysis.metrics import summarize_solver_result
from qubo_vqa.analysis.plots import plot_energy_trace
from qubo_vqa.core.result import SolverResult
from qubo_vqa.experiments.config import ExperimentConfig
from qubo_vqa.utils.io import ensure_directory, write_json
from qubo_vqa.visualization.graphs import plot_maxcut_partition


def create_run_directory(base_directory: str | Path, tag: str) -> Path:
    """Create a timestamped output directory for one experiment run."""
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return ensure_directory(Path(base_directory) / f"{tag}-{timestamp}")


def _safe_package_version(distribution_name: str) -> str | None:
    """Return an installed package version when available."""
    try:
        return version(distribution_name)
    except PackageNotFoundError:
        return None


def build_run_metadata(
    run_directory: Path,
    config: ExperimentConfig,
    result: SolverResult,
    config_path: str | Path | None,
) -> dict[str, object]:
    """Build reproducibility metadata for one run."""
    return {
        "run_id": run_directory.name,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "experiment_name": config.experiment_name,
        "config_path": str(config_path) if config_path is not None else None,
        "seed": config.seed,
        "problem_name": config.problem.name,
        "solver_name": result.solver_name,
        "runtime_seconds": result.runtime_seconds,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "package_versions": {
            "numpy": _safe_package_version("numpy"),
            "scipy": _safe_package_version("scipy"),
            "qiskit": _safe_package_version("qiskit"),
            "qiskit-aer": _safe_package_version("qiskit-aer"),
        },
    }


def save_run_outputs(
    run_directory: Path,
    config: ExperimentConfig,
    result: SolverResult,
    config_path: str | Path | None,
    problem_artifacts: dict[str, object],
) -> None:
    """Write standard artifacts for a completed experiment run."""
    write_json(run_directory / "config.json", asdict(config))
    write_json(run_directory / "result.json", result.as_dict())
    write_json(run_directory / "metrics.json", summarize_solver_result(result))
    write_json(
        run_directory / "run_metadata.json",
        build_run_metadata(
            run_directory=run_directory,
            config=config,
            result=result,
            config_path=config_path,
        ),
    )
    write_json(run_directory / "trace.json", {"trace": result.trace_as_dicts()})
    plot_energy_trace(result, run_directory / "plots" / "energy_trace.png")

    if "qubo_model" in problem_artifacts:
        write_json(
            run_directory / "artifacts" / "qubo_model.json",
            problem_artifacts["qubo_model"],
        )

    if problem_artifacts.get("ising_model") is not None:
        write_json(
            run_directory / "artifacts" / "ising_model.json",
            problem_artifacts["ising_model"],
        )

    if {"graph", "left_partition", "right_partition"} <= problem_artifacts.keys():
        plot_maxcut_partition(
            graph=problem_artifacts["graph"],
            left_partition=list(problem_artifacts["left_partition"]),
            right_partition=list(problem_artifacts["right_partition"]),
            output_path=run_directory / "plots" / "maxcut_partition.png",
        )
