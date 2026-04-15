"""Common metrics extracted from solver results."""

from __future__ import annotations

from typing import Any

from qubo_vqa.core.result import SolverResult


def summarize_solver_result(result: SolverResult) -> dict[str, float | int | str]:
    """Create a compact metrics record for logging and CSV-like export."""
    metrics: dict[str, float | int | str] = {
        "solver_name": result.solver_name,
        "best_energy": result.best_energy,
        "objective_value": result.decoded_solution.objective_value,
        "is_feasible": int(result.decoded_solution.is_feasible),
        "runtime_seconds": result.runtime_seconds,
        "evaluations": int(result.metadata.get("evaluations", len(result.trace))),
        "trace_length": len(result.trace),
    }
    if "best_expectation_energy" in result.metadata:
        metrics["best_expectation_energy"] = float(result.metadata["best_expectation_energy"])
    if "best_dominant_probability" in result.metadata:
        metrics["best_dominant_probability"] = float(result.metadata["best_dominant_probability"])
    return metrics


def compute_approximation_ratio(
    objective_value: float,
    optimum_objective_value: float,
) -> float:
    """Return the approximation ratio against a positive optimum objective."""
    if optimum_objective_value <= 0.0:
        msg = "optimum_objective_value must be positive to compute an approximation ratio."
        raise ValueError(msg)
    return float(objective_value / optimum_objective_value)


def aggregate_qaoa_initialization_runs(
    run_metrics: list[dict[str, Any]],
) -> list[dict[str, float | int | str]]:
    """Aggregate QAOA initialization runs by strategy and QAOA depth."""
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for record in run_metrics:
        key = (str(record["requested_strategy"]), int(record["rep"]))
        grouped.setdefault(key, []).append(record)

    aggregates: list[dict[str, float | int | str]] = []
    for strategy, rep in sorted(grouped):
        records = grouped[(strategy, rep)]
        objective_values = [float(record["objective_value"]) for record in records]
        approximation_ratios = [float(record["approximation_ratio"]) for record in records]
        evaluations = [int(record["evaluations"]) for record in records]
        runtimes = [float(record["runtime_seconds"]) for record in records]
        best_expectations = [
            float(record.get("best_expectation_energy", record["best_energy"]))
            for record in records
        ]
        aggregates.append(
            {
                "strategy": strategy,
                "rep": rep,
                "num_runs": len(records),
                "best_objective_value": max(objective_values),
                "mean_objective_value": sum(objective_values) / len(objective_values),
                "best_approximation_ratio": max(approximation_ratios),
                "mean_approximation_ratio": sum(approximation_ratios) / len(approximation_ratios),
                "best_energy": min(float(record["best_energy"]) for record in records),
                "mean_best_expectation_energy": sum(best_expectations) / len(best_expectations),
                "mean_evaluations": sum(evaluations) / len(evaluations),
                "mean_runtime_seconds": sum(runtimes) / len(runtimes),
                "success_rate": sum(bool(record["optimization_success"]) for record in records)
                / len(records),
            }
        )
    return aggregates


def aggregate_backend_comparison_runs(
    run_metrics: list[dict[str, Any]],
) -> list[dict[str, float | int | str]]:
    """Aggregate backend comparison runs by backend label."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in run_metrics:
        grouped.setdefault(str(record["backend_label"]), []).append(record)

    aggregates: list[dict[str, float | int | str]] = []
    for backend_label in sorted(grouped):
        records = grouped[backend_label]
        objective_values = [float(record["objective_value"]) for record in records]
        approximation_ratios = [float(record["approximation_ratio"]) for record in records]
        best_expectations = [
            float(record.get("best_expectation_energy", record["best_energy"]))
            for record in records
        ]
        runtimes = [float(record["runtime_seconds"]) for record in records]
        evaluations = [int(record["evaluations"]) for record in records]

        aggregates.append(
            {
                "backend_label": backend_label,
                "mode": str(records[0]["mode"]),
                "noise_model_name": str(records[0]["noise_model_name"]),
                "num_runs": len(records),
                "best_objective_value": max(objective_values),
                "mean_objective_value": sum(objective_values) / len(objective_values),
                "best_approximation_ratio": max(approximation_ratios),
                "mean_approximation_ratio": sum(approximation_ratios) / len(approximation_ratios),
                "best_energy": min(float(record["best_energy"]) for record in records),
                "mean_best_expectation_energy": sum(best_expectations) / len(best_expectations),
                "mean_runtime_seconds": sum(runtimes) / len(runtimes),
                "mean_evaluations": sum(evaluations) / len(evaluations),
                "success_rate": sum(bool(record["optimization_success"]) for record in records)
                / len(records),
            }
        )
    return aggregates
