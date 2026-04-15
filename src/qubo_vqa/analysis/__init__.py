"""Analysis helpers and future landscape tooling."""

from qubo_vqa.analysis.metrics import (
    aggregate_qaoa_initialization_runs,
    compute_approximation_ratio,
    summarize_solver_result,
)
from qubo_vqa.analysis.plots import (
    plot_energy_trace,
    plot_metric_by_depth,
    plot_qaoa_parameter_values_by_depth,
)

__all__ = [
    "aggregate_qaoa_initialization_runs",
    "compute_approximation_ratio",
    "plot_energy_trace",
    "plot_metric_by_depth",
    "plot_qaoa_parameter_values_by_depth",
    "summarize_solver_result",
]
