"""Config-driven comparison workflow for exact, shot-based, and noisy backends."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from qubo_vqa.analysis.metrics import (
    aggregate_backend_comparison_runs,
    compute_approximation_ratio,
    summarize_solver_result,
)
from qubo_vqa.analysis.plots import plot_energy_trace, plot_metric_by_category
from qubo_vqa.experiments.config import OutputConfig, ProblemConfig, SolverConfig
from qubo_vqa.experiments.logging import create_run_directory
from qubo_vqa.experiments.runner import build_problem, build_solver
from qubo_vqa.solvers.classical.brute_force import BruteForceSolver
from qubo_vqa.utils.io import write_csv_rows, write_json
from qubo_vqa.utils.random import set_global_seed


@dataclass(slots=True)
class BackendComparisonCase:
    """One backend setting included in a comparison run."""

    label: str
    mode: str
    shots: int | None = None
    noise_model_name: str | None = None
    trials: int = 1


@dataclass(slots=True)
class QuantumBackendComparisonConfig:
    """Configuration for comparing multiple backend modes on one solver path."""

    experiment_name: str
    seed: int
    problem: ProblemConfig
    solver: SolverConfig
    output: OutputConfig
    backends: list[BackendComparisonCase]


@dataclass(slots=True)
class _ProblemCarrier:
    """Minimal config wrapper used to reuse the standard problem builder."""

    seed: int
    problem: ProblemConfig


@dataclass(slots=True)
class _SolverCarrier:
    """Minimal config wrapper used to reuse the standard solver builder."""

    seed: int
    solver: SolverConfig


def _nested_dict(value: object) -> dict[str, Any]:
    """Return a dictionary view for nested config sections."""
    if isinstance(value, dict):
        return dict(value)
    return {}


def load_backend_comparison_config(path: str | Path) -> QuantumBackendComparisonConfig:
    """Load a backend comparison configuration from YAML."""
    raw_payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    comparison_parameters = _nested_dict(raw_payload.get("comparison"))
    backend_payloads = comparison_parameters.get("backends", [])
    if not backend_payloads:
        msg = "comparison.backends must contain at least one backend case."
        raise ValueError(msg)

    backends = [
        BackendComparisonCase(
            label=str(backend["label"]),
            mode=str(backend["mode"]),
            shots=int(backend["shots"]) if backend.get("shots") is not None else None,
            noise_model_name=(
                str(backend["noise_model_name"])
                if backend.get("noise_model_name") is not None
                else None
            ),
            trials=int(backend.get("trials", 1)),
        )
        for backend in backend_payloads
    ]
    for backend in backends:
        if backend.trials <= 0:
            msg = f"comparison backend '{backend.label}' must request at least one trial."
            raise ValueError(msg)

    return QuantumBackendComparisonConfig(
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
        backends=backends,
    )


def _solver_with_backend_override(
    *,
    config: QuantumBackendComparisonConfig,
    backend_case: BackendComparisonCase,
    seed: int,
):
    """Construct one solver instance with an overridden backend section."""
    solver_parameters = dict(config.solver.parameters)
    backend_parameters = _nested_dict(solver_parameters.get("backend"))
    backend_parameters.update(
        {
            "mode": backend_case.mode,
            "shots": backend_case.shots,
            "noise_model_name": backend_case.noise_model_name,
            "seed": seed,
        }
    )
    solver_parameters["backend"] = backend_parameters
    return build_solver(
        _SolverCarrier(
            seed=seed,
            solver=SolverConfig(name=config.solver.name, parameters=solver_parameters),
        )
    )


def run_quantum_backend_comparison(
    config_path: str | Path,
    output_directory: str | Path | None = None,
) -> Path:
    """Compare exact, shot-based, and noisy backends on one problem/solver path."""
    config = load_backend_comparison_config(config_path)
    if output_directory is not None:
        config.output.directory = str(output_directory)

    set_global_seed(config.seed)
    problem = build_problem(_ProblemCarrier(seed=config.seed, problem=config.problem))
    qubo_model = problem.to_qubo_model()
    exact_reference = BruteForceSolver(max_variables=max(20, qubo_model.num_variables())).solve(
        qubo_model,
        problem.decode_bitstring,
    )
    optimum_objective_value = float(exact_reference.decoded_solution.objective_value)
    run_directory = create_run_directory(config.output.directory, config.output.tag)

    run_metrics: list[dict[str, Any]] = []
    for backend_case in config.backends:
        for trial_index in range(backend_case.trials):
            trial_seed = config.seed + trial_index
            solver = _solver_with_backend_override(
                config=config,
                backend_case=backend_case,
                seed=trial_seed,
            )
            result = solver.solve(qubo_model, problem.decode_bitstring)
            label = f"{backend_case.label}-trial{trial_index}"
            write_json(
                run_directory / "traces" / f"{label}.json",
                {"trace": result.trace_as_dicts()},
            )
            plot_energy_trace(result, run_directory / "plots" / f"{label}_energy_trace.png")

            metrics = summarize_solver_result(result)
            metrics.update(
                {
                    "backend_label": backend_case.label,
                    "mode": backend_case.mode,
                    "shots": backend_case.shots if backend_case.shots is not None else "",
                    "noise_model_name": backend_case.noise_model_name or "",
                    "trial_index": trial_index,
                    "seed": trial_seed,
                    "optimum_objective_value": optimum_objective_value,
                    "approximation_ratio": compute_approximation_ratio(
                        float(result.decoded_solution.objective_value),
                        optimum_objective_value,
                    ),
                    "optimization_success": bool(result.metadata["optimization_success"]),
                }
            )
            run_metrics.append(metrics)

    aggregate_metrics = aggregate_backend_comparison_runs(run_metrics)
    write_csv_rows(run_directory / "tables" / "run_metrics.csv", run_metrics)
    write_csv_rows(run_directory / "tables" / "aggregate_metrics.csv", aggregate_metrics)
    plot_metric_by_category(
        aggregate_metrics,
        category_key="backend_label",
        metric_key="mean_objective_value",
        output_path=run_directory / "plots" / "objective_value_by_backend.png",
        title="Objective value by backend",
        ylabel="Mean objective value",
    )
    plot_metric_by_category(
        aggregate_metrics,
        category_key="backend_label",
        metric_key="mean_best_expectation_energy",
        output_path=run_directory / "plots" / "best_expectation_energy_by_backend.png",
        title="Expectation energy by backend",
        ylabel="Mean best expectation energy",
    )
    plot_metric_by_category(
        aggregate_metrics,
        category_key="backend_label",
        metric_key="mean_runtime_seconds",
        output_path=run_directory / "plots" / "runtime_by_backend.png",
        title="Runtime by backend",
        ylabel="Mean runtime (s)",
    )
    plot_metric_by_category(
        aggregate_metrics,
        category_key="backend_label",
        metric_key="success_rate",
        output_path=run_directory / "plots" / "success_rate_by_backend.png",
        title="Optimization success rate by backend",
        ylabel="Success rate",
    )

    summary = {
        "experiment_name": config.experiment_name,
        "config_path": str(config_path),
        "config": asdict(config),
        "exact_reference": {
            "best_bitstring": list(exact_reference.best_bitstring),
            "best_energy": exact_reference.best_energy,
            "objective_value": optimum_objective_value,
            "solver_name": exact_reference.solver_name,
        },
        "aggregates": aggregate_metrics,
        "runs": run_metrics,
    }
    write_json(run_directory / "config.json", asdict(config))
    write_json(run_directory / "summary.json", summary)
    write_json(run_directory / "artifacts" / "qubo_model.json", qubo_model.as_dict())
    return run_directory
