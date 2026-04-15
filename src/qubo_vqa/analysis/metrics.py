"""Common metrics extracted from solver results."""

from __future__ import annotations

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
