"""Plotting helpers for early experiment outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from qubo_vqa.core.result import SolverResult
from qubo_vqa.utils.io import ensure_directory


def plot_energy_trace(result: SolverResult, output_path: Path) -> None:
    """Plot solver energy over evaluation steps."""
    ensure_directory(output_path.parent)
    fig, axis = plt.subplots(figsize=(6, 4))
    axis.plot(
        [entry.step for entry in result.trace],
        [entry.energy for entry in result.trace],
        marker="o",
    )
    axis.set_title(f"{result.solver_name} energy trace")
    axis.set_xlabel("Evaluation")
    axis.set_ylabel("QUBO energy")
    axis.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
