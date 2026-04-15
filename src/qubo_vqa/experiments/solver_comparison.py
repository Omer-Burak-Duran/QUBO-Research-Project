"""Config-driven comparison workflow across classical and quantum solvers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from qubo_vqa.analysis.metrics import (
    aggregate_solver_comparison_runs,
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
class SolverComparisonCase:
    """One solver setting included in a comparison run."""

    label: str
    solver: SolverConfig
    trials: int = 1


@dataclass(slots=True)
class SolverComparisonConfig:
    """Configuration for comparing several solvers on one shared instance."""

    experiment_name: str
    seed: int
    problem: ProblemConfig
    output: OutputConfig
    solvers: list[SolverComparisonCase]


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


def load_solver_comparison_config(path: str | Path) -> SolverComparisonConfig:
    """Load a solver-comparison config from YAML."""
    raw_payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    comparison_payload = _nested_dict(raw_payload.get("comparison"))
    solver_payloads = comparison_payload.get("solvers", [])
    if not solver_payloads:
        msg = "comparison.solvers must contain at least one solver case."
        raise ValueError(msg)

    solvers = [
        SolverComparisonCase(
            label=str(case["label"]),
            solver=SolverConfig(
                name=str(case["name"]),
                parameters=dict(case.get("parameters", {})),
            ),
            trials=int(case.get("trials", 1)),
        )
        for case in solver_payloads
    ]
    for solver_case in solvers:
        if solver_case.trials <= 0:
            msg = f"comparison solver '{solver_case.label}' must request at least one trial."
            raise ValueError(msg)

    return SolverComparisonConfig(
        experiment_name=str(raw_payload["experiment_name"]),
        seed=int(raw_payload.get("seed", 0)),
        problem=ProblemConfig(
            name=str(raw_payload["problem"]["name"]),
            parameters=dict(raw_payload["problem"].get("parameters", {})),
        ),
        output=OutputConfig(
            directory=str(raw_payload.get("output", {}).get("directory", "data/results")),
            tag=str(raw_payload.get("output", {}).get("tag", raw_payload["experiment_name"])),
        ),
        solvers=solvers,
    )


def _solver_with_seed(
    *,
    solver_case: SolverComparisonCase,
    seed: int,
):
    """Construct one solver instance with a deterministic per-trial seed override."""
    parameters = dict(solver_case.solver.parameters)
    if solver_case.solver.name in {"openjij"}:
        parameters["seed"] = seed
    elif solver_case.solver.name == "qaoa":
        initialization = _nested_dict(parameters.get("initialization"))
        initialization["seed"] = seed
        parameters["initialization"] = initialization
        backend = _nested_dict(parameters.get("backend"))
        if backend.get("seed") is not None:
            backend["seed"] = seed
        parameters["backend"] = backend
    elif solver_case.solver.name == "vqe":
        initialization = _nested_dict(parameters.get("initialization"))
        initialization["seed"] = seed
        parameters["initialization"] = initialization
        backend = _nested_dict(parameters.get("backend"))
        if backend.get("seed") is not None:
            backend["seed"] = seed
        parameters["backend"] = backend

    return build_solver(
        _SolverCarrier(
            seed=seed,
            solver=SolverConfig(name=solver_case.solver.name, parameters=parameters),
        )
    )


def run_solver_comparison(
    config_path: str | Path,
    output_directory: str | Path | None = None,
) -> Path:
    """Compare several solvers on one shared benchmark instance."""
    config = load_solver_comparison_config(config_path)
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
    for solver_case in config.solvers:
        for trial_index in range(solver_case.trials):
            trial_seed = config.seed + trial_index
            solver = _solver_with_seed(solver_case=solver_case, seed=trial_seed)
            result = solver.solve(qubo_model, problem.decode_bitstring)
            label = f"{solver_case.label}-trial{trial_index}"
            write_json(
                run_directory / "traces" / f"{label}.json",
                {"label": label, "trace": result.trace_as_dicts()},
            )
            plot_energy_trace(result, run_directory / "plots" / f"{label}_energy_trace.png")
            metrics = summarize_solver_result(result)
            metrics.update(
                {
                    "solver_label": solver_case.label,
                    "solver_name": result.solver_name,
                    "trial_index": trial_index,
                    "seed": trial_seed,
                    "optimum_objective_value": optimum_objective_value,
                    "approximation_ratio": compute_approximation_ratio(
                        float(result.decoded_solution.objective_value),
                        optimum_objective_value,
                    ),
                    "solver_success": bool(
                        result.metadata.get(
                            "optimization_success",
                            result.metadata.get("sampling_success", True),
                        )
                    ),
                }
            )
            run_metrics.append(metrics)

    aggregate_metrics = aggregate_solver_comparison_runs(run_metrics)
    write_csv_rows(run_directory / "tables" / "run_metrics.csv", run_metrics)
    write_csv_rows(run_directory / "tables" / "aggregate_metrics.csv", aggregate_metrics)
    plot_metric_by_category(
        aggregate_metrics,
        category_key="solver_label",
        metric_key="mean_objective_value",
        output_path=run_directory / "plots" / "objective_value_by_solver.png",
        title="Objective value by solver",
        ylabel="Mean objective value",
    )
    plot_metric_by_category(
        aggregate_metrics,
        category_key="solver_label",
        metric_key="mean_best_energy",
        output_path=run_directory / "plots" / "best_energy_by_solver.png",
        title="Best QUBO energy by solver",
        ylabel="Mean best energy",
    )
    plot_metric_by_category(
        aggregate_metrics,
        category_key="solver_label",
        metric_key="mean_runtime_seconds",
        output_path=run_directory / "plots" / "runtime_by_solver.png",
        title="Runtime by solver",
        ylabel="Mean runtime (s)",
    )
    plot_metric_by_category(
        aggregate_metrics,
        category_key="solver_label",
        metric_key="mean_approximation_ratio",
        output_path=run_directory / "plots" / "approximation_ratio_by_solver.png",
        title="Approximation ratio by solver",
        ylabel="Mean approximation ratio",
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
