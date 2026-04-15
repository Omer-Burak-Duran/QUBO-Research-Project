"""Plotting helpers for early experiment outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

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


def plot_metric_by_depth(
    aggregate_records: list[dict[str, Any]],
    metric_key: str,
    output_path: Path,
    title: str,
    ylabel: str,
) -> None:
    """Plot one aggregate metric against QAOA depth for each strategy."""
    ensure_directory(output_path.parent)
    strategies = sorted({str(record["strategy"]) for record in aggregate_records})

    fig, axis = plt.subplots(figsize=(6.5, 4.5))
    for strategy in strategies:
        records = sorted(
            (
                record
                for record in aggregate_records
                if str(record["strategy"]) == strategy and metric_key in record
            ),
            key=lambda record: int(record["rep"]),
        )
        if not records:
            continue
        axis.plot(
            [int(record["rep"]) for record in records],
            [float(record[metric_key]) for record in records],
            marker="o",
            label=strategy,
        )

    axis.set_title(title)
    axis.set_xlabel("QAOA depth (p)")
    axis.set_ylabel(ylabel)
    axis.grid(True, alpha=0.3)
    axis.legend()
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_qaoa_parameter_values_by_depth(
    run_metrics: list[dict[str, Any]],
    output_directory: Path,
) -> None:
    """Plot final gamma and beta values for the best run at each depth."""
    ensure_directory(output_directory)
    strategies = sorted({str(record["requested_strategy"]) for record in run_metrics})

    for strategy in strategies:
        strategy_records = [
            record for record in run_metrics if record["requested_strategy"] == strategy
        ]
        reps = sorted({int(record["rep"]) for record in strategy_records})
        if not reps:
            continue

        fig, axes = plt.subplots(2, 1, figsize=(7, 6), sharex=False)
        plotted_any = False
        for rep in reps:
            rep_records = [record for record in strategy_records if int(record["rep"]) == rep]
            best_record = min(
                rep_records,
                key=lambda record: float(
                    record.get("best_expectation_energy", record["best_energy"])
                ),
            )
            parameters = np.asarray(best_record["final_parameters"], dtype=float)
            gammas = parameters[:rep]
            betas = parameters[rep:]
            layers = np.arange(1, rep + 1, dtype=int)
            axes[0].plot(layers, gammas, marker="o", label=f"p={rep}")
            axes[1].plot(layers, betas, marker="o", label=f"p={rep}")
            plotted_any = True

        if not plotted_any:
            plt.close(fig)
            continue

        axes[0].set_title(f"{strategy} final gamma values by depth")
        axes[0].set_ylabel("gamma")
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()

        axes[1].set_title(f"{strategy} final beta values by depth")
        axes[1].set_xlabel("Layer index")
        axes[1].set_ylabel("beta")
        axes[1].grid(True, alpha=0.3)
        axes[1].legend()

        fig.tight_layout()
        fig.savefig(output_directory / f"final_parameters_{strategy}.png")
        plt.close(fig)


def plot_metric_by_category(
    aggregate_records: list[dict[str, Any]],
    category_key: str,
    metric_key: str,
    output_path: Path,
    title: str,
    ylabel: str,
    rotation: float = 0.0,
) -> None:
    """Plot one metric as a bar chart across categorical experiment groups."""
    ensure_directory(output_path.parent)
    records = [
        record
        for record in aggregate_records
        if metric_key in record and category_key in record
    ]
    if not records:
        return

    labels = [str(record[category_key]) for record in records]
    values = [float(record[metric_key]) for record in records]

    figure_width = max(7.0, 0.55 * len(labels))
    fig, axis = plt.subplots(figsize=(figure_width, 4.5))
    axis.bar(labels, values)
    axis.set_title(title)
    axis.set_xlabel(category_key.replace("_", " ").title())
    axis.set_ylabel(ylabel)
    if rotation != 0.0:
        axis.tick_params(axis="x", labelrotation=rotation)
        fig.subplots_adjust(bottom=0.3)
    axis.grid(True, axis="y", alpha=0.3)
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def plot_heatmap(
    *,
    x_values: np.ndarray,
    y_values: np.ndarray,
    matrix: np.ndarray,
    output_path: Path,
    title: str,
    xlabel: str,
    ylabel: str,
    colorbar_label: str,
) -> None:
    """Plot a dense 2D heatmap over two sampled parameter axes."""
    ensure_directory(output_path.parent)
    fig, axis = plt.subplots(figsize=(6.5, 5.0))
    image = axis.imshow(
        matrix,
        origin="lower",
        aspect="auto",
        extent=[x_values[0], x_values[-1], y_values[0], y_values[-1]],
        cmap="viridis",
    )
    axis.set_title(title)
    axis.set_xlabel(xlabel)
    axis.set_ylabel(ylabel)
    colorbar = fig.colorbar(image, ax=axis)
    colorbar.set_label(colorbar_label)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_multistart_energy_traces(
    trace_records: list[dict[str, Any]],
    output_path: Path,
    *,
    title: str,
) -> None:
    """Plot energy traces from multiple optimization runs on one axis."""
    ensure_directory(output_path.parent)
    fig, axis = plt.subplots(figsize=(7, 4.5))
    for record in trace_records:
        steps = [int(point["step"]) for point in record["trace"]]
        energies = [float(point["energy"]) for point in record["trace"]]
        axis.plot(steps, energies, alpha=0.8, label=str(record["label"]))
    axis.set_title(title)
    axis.set_xlabel("Evaluation")
    axis.set_ylabel("Expectation energy")
    axis.grid(True, alpha=0.3)
    axis.legend()
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_gradient_norm_histogram(
    gradient_samples: list[dict[str, Any]],
    output_path: Path,
    *,
    title: str,
) -> None:
    """Plot the distribution of finite-difference gradient norms."""
    ensure_directory(output_path.parent)
    gradient_norms = [float(sample["gradient_norm"]) for sample in gradient_samples]
    fig, axis = plt.subplots(figsize=(6.5, 4.5))
    axis.hist(gradient_norms, bins=min(10, max(3, len(gradient_norms))), edgecolor="black")
    axis.set_title(title)
    axis.set_xlabel("Gradient norm")
    axis.set_ylabel("Frequency")
    axis.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
