"""Analysis helpers and future landscape tooling."""

from qubo_vqa.analysis.barren_plateau import (
    finite_difference_gradient,
    sample_gradient_statistics,
    summarize_gradient_samples,
)
from qubo_vqa.analysis.landscape import (
    ParameterGrid,
    evaluate_qaoa_p1_landscape,
    landscape_records_to_matrix,
    summarize_landscape,
)
from qubo_vqa.analysis.metrics import (
    aggregate_qaoa_initialization_runs,
    compute_approximation_ratio,
    summarize_solver_result,
)
from qubo_vqa.analysis.plots import (
    plot_energy_trace,
    plot_gradient_norm_histogram,
    plot_heatmap,
    plot_metric_by_depth,
    plot_multistart_energy_traces,
    plot_qaoa_parameter_values_by_depth,
)

__all__ = [
    "ParameterGrid",
    "aggregate_qaoa_initialization_runs",
    "compute_approximation_ratio",
    "evaluate_qaoa_p1_landscape",
    "finite_difference_gradient",
    "plot_energy_trace",
    "plot_gradient_norm_histogram",
    "plot_heatmap",
    "plot_metric_by_depth",
    "plot_multistart_energy_traces",
    "plot_qaoa_parameter_values_by_depth",
    "landscape_records_to_matrix",
    "sample_gradient_statistics",
    "summarize_solver_result",
    "summarize_gradient_samples",
    "summarize_landscape",
]
