"""Config-driven comparison workflow for QAOA initialization strategies."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import yaml

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
from qubo_vqa.experiments.config import OutputConfig, ProblemConfig
from qubo_vqa.experiments.logging import create_run_directory
from qubo_vqa.experiments.runner import build_problem
from qubo_vqa.solvers.classical.brute_force import BruteForceSolver
from qubo_vqa.solvers.quantum.backends import QuantumBackendConfig
from qubo_vqa.solvers.quantum.initialization import (
    SUPPORTED_QAOA_INITIALIZATIONS,
    QAOAInitializationConfig,
)
from qubo_vqa.solvers.quantum.qaoa import QAOAOptimizerConfig, QAOASolver
from qubo_vqa.utils.io import write_csv_rows, write_json
from qubo_vqa.utils.random import set_global_seed


@dataclass(slots=True)
class QAOAInitializationComparisonConfig:
    """Configuration for comparing QAOA initialization strategies."""

    experiment_name: str
    seed: int
    problem: ProblemConfig
    output: OutputConfig
    reps: list[int]
    strategies: list[str]
    random_trials: int
    warm_start_bootstrap_strategy: str
    optimizer: QAOAOptimizerConfig
    backend: QuantumBackendConfig
    max_variables: int = 12


@dataclass(slots=True)
class _ProblemCarrier:
    """Minimal config wrapper used to reuse the standard problem builder."""

    seed: int
    problem: ProblemConfig


def _nested_dict(value: object) -> dict[str, Any]:
    """Return a dictionary view for nested config sections."""
    if isinstance(value, dict):
        return dict(value)
    return {}


def _sorted_unique_reps(values: list[object]) -> list[int]:
    """Validate and normalize a list of positive QAOA depths."""
    reps = sorted({int(value) for value in values})
    if not reps or reps[0] <= 0:
        msg = "comparison.reps must contain at least one positive depth."
        raise ValueError(msg)
    return reps


def load_qaoa_initialization_comparison_config(
    path: str | Path,
) -> QAOAInitializationComparisonConfig:
    """Load the initialization-comparison config from YAML."""
    raw_payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    solver_parameters = _nested_dict(raw_payload["solver"]["parameters"])
    optimizer_parameters = _nested_dict(solver_parameters.get("optimizer"))
    backend_parameters = _nested_dict(solver_parameters.get("backend"))
    comparison_parameters = _nested_dict(raw_payload.get("comparison"))
    strategies = [str(strategy) for strategy in comparison_parameters.get("strategies", [])]

    unsupported = sorted(set(strategies) - set(SUPPORTED_QAOA_INITIALIZATIONS))
    if unsupported:
        msg = f"Unsupported initialization strategies requested: {unsupported}."
        raise ValueError(msg)

    bootstrap_strategy = str(
        comparison_parameters.get("warm_start_bootstrap_strategy", "interpolation")
    )
    if bootstrap_strategy == "warm_start":
        msg = "warm_start_bootstrap_strategy cannot itself be 'warm_start'."
        raise ValueError(msg)
    if bootstrap_strategy not in SUPPORTED_QAOA_INITIALIZATIONS:
        msg = f"Unsupported warm-start bootstrap strategy '{bootstrap_strategy}'."
        raise ValueError(msg)

    return QAOAInitializationComparisonConfig(
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
        reps=_sorted_unique_reps(list(comparison_parameters.get("reps", [1]))),
        strategies=strategies,
        random_trials=int(comparison_parameters.get("random_trials", 3)),
        warm_start_bootstrap_strategy=bootstrap_strategy,
        optimizer=QAOAOptimizerConfig(
            method=str(
                optimizer_parameters.get(
                    "name",
                    optimizer_parameters.get("method", "COBYLA"),
                )
            ),
            maxiter=int(optimizer_parameters.get("maxiter", 80)),
            tol=(
                float(optimizer_parameters["tol"])
                if optimizer_parameters.get("tol") is not None
                else None
            ),
            options=_nested_dict(optimizer_parameters.get("options")),
        ),
        backend=QuantumBackendConfig(
            mode=str(
                backend_parameters.get(
                    "mode",
                    solver_parameters.get("backend_mode", "statevector"),
                )
            ),
            shots=(
                int(backend_parameters["shots"])
                if backend_parameters.get("shots") is not None
                else None
            ),
            noise_model_name=(
                str(backend_parameters["noise_model_name"])
                if backend_parameters.get("noise_model_name") is not None
                else None
            ),
            seed=(
                int(backend_parameters["seed"])
                if backend_parameters.get("seed") is not None
                else int(raw_payload.get("seed", 0))
            ),
        ),
        max_variables=int(solver_parameters.get("max_variables", 12)),
    )


def _run_single_qaoa_strategy(
    *,
    problem,
    qubo_model,
    optimum_objective_value: float,
    rep: int,
    requested_strategy: str,
    initialization_strategy: str,
    seed: int,
    optimizer_config: QAOAOptimizerConfig,
    backend_config: QuantumBackendConfig,
    max_variables: int,
    run_directory: Path,
    trial_index: int,
    previous_parameters: np.ndarray | None = None,
) -> dict[str, Any]:
    """Execute one QAOA run and save its trace artifacts."""
    label = f"{requested_strategy}-rep{rep}-trial{trial_index}"
    solver = QAOASolver(
        reps=rep,
        backend_config=backend_config,
        optimizer_config=optimizer_config,
        initialization_config=QAOAInitializationConfig(
            strategy=initialization_strategy,
            seed=seed,
        ),
        previous_parameters=previous_parameters,
        max_variables=max_variables,
    )
    result = solver.solve(qubo_model, problem.decode_bitstring)
    write_json(run_directory / "traces" / f"{label}.json", {"trace": result.trace_as_dicts()})
    plot_energy_trace(result, run_directory / "plots" / f"{label}_energy_trace.png")

    metrics = summarize_solver_result(result)
    metrics.update(
        {
            "label": label,
            "rep": rep,
            "requested_strategy": requested_strategy,
            "initialization_strategy_used": initialization_strategy,
            "trial_index": trial_index,
            "seed": seed,
            "previous_parameter_count": (
                0 if previous_parameters is None else int(previous_parameters.size)
            ),
            "parameter_count": len(result.metadata["final_parameters"]),
            "optimum_objective_value": optimum_objective_value,
            "approximation_ratio": compute_approximation_ratio(
                float(result.decoded_solution.objective_value),
                optimum_objective_value,
            ),
            "final_parameters": list(result.metadata["final_parameters"]),
            "initial_parameters": list(result.metadata["initial_parameters"]),
            "optimization_success": bool(result.metadata["optimization_success"]),
        }
    )
    return metrics


def run_qaoa_initialization_comparison(
    config_path: str | Path,
    output_directory: str | Path | None = None,
) -> Path:
    """Compare QAOA initialization strategies on the current MaxCut path."""
    config = load_qaoa_initialization_comparison_config(config_path)
    if output_directory is not None:
        config.output.directory = str(output_directory)

    set_global_seed(config.seed)
    problem = build_problem(_ProblemCarrier(seed=config.seed, problem=config.problem))
    qubo_model = problem.to_qubo_model()
    exact_result = BruteForceSolver(
        max_variables=max(config.max_variables, qubo_model.num_variables())
    ).solve(qubo_model, problem.decode_bitstring)
    optimum_objective_value = float(exact_result.decoded_solution.objective_value)
    run_directory = create_run_directory(config.output.directory, config.output.tag)

    run_metrics: list[dict[str, Any]] = []
    for strategy in config.strategies:
        if strategy == "random":
            for rep in config.reps:
                for trial_index in range(config.random_trials):
                    run_metrics.append(
                        _run_single_qaoa_strategy(
                            problem=problem,
                            qubo_model=qubo_model,
                            optimum_objective_value=optimum_objective_value,
                            rep=rep,
                            requested_strategy="random",
                            initialization_strategy="random",
                            seed=config.seed + trial_index,
                            optimizer_config=config.optimizer,
                            backend_config=config.backend,
                            max_variables=config.max_variables,
                            run_directory=run_directory,
                            trial_index=trial_index,
                        )
                    )
            continue

        if strategy == "warm_start":
            previous_parameters: np.ndarray | None = None
            for rep in config.reps:
                initialization_strategy = (
                    config.warm_start_bootstrap_strategy
                    if previous_parameters is None
                    else "warm_start"
                )
                metrics = _run_single_qaoa_strategy(
                    problem=problem,
                    qubo_model=qubo_model,
                    optimum_objective_value=optimum_objective_value,
                    rep=rep,
                    requested_strategy="warm_start",
                    initialization_strategy=initialization_strategy,
                    seed=config.seed,
                    optimizer_config=config.optimizer,
                    backend_config=config.backend,
                    max_variables=config.max_variables,
                    run_directory=run_directory,
                    trial_index=0,
                    previous_parameters=previous_parameters,
                )
                run_metrics.append(metrics)
                previous_parameters = np.asarray(metrics["final_parameters"], dtype=float)
            continue

        for rep in config.reps:
            run_metrics.append(
                _run_single_qaoa_strategy(
                    problem=problem,
                    qubo_model=qubo_model,
                    optimum_objective_value=optimum_objective_value,
                    rep=rep,
                    requested_strategy=strategy,
                    initialization_strategy=strategy,
                    seed=config.seed,
                    optimizer_config=config.optimizer,
                    backend_config=config.backend,
                    max_variables=config.max_variables,
                    run_directory=run_directory,
                    trial_index=0,
                )
            )

    aggregate_metrics = aggregate_qaoa_initialization_runs(run_metrics)
    write_csv_rows(run_directory / "tables" / "run_metrics.csv", run_metrics)
    write_csv_rows(run_directory / "tables" / "aggregate_metrics.csv", aggregate_metrics)
    plot_metric_by_depth(
        aggregate_metrics,
        metric_key="mean_approximation_ratio",
        output_path=run_directory / "plots" / "approximation_ratio_vs_depth.png",
        title="QAOA approximation ratio vs depth",
        ylabel="Mean approximation ratio",
    )
    plot_metric_by_depth(
        aggregate_metrics,
        metric_key="mean_best_expectation_energy",
        output_path=run_directory / "plots" / "best_expectation_energy_vs_depth.png",
        title="QAOA expectation energy vs depth",
        ylabel="Mean best expectation energy",
    )
    plot_metric_by_depth(
        aggregate_metrics,
        metric_key="mean_runtime_seconds",
        output_path=run_directory / "plots" / "runtime_vs_depth.png",
        title="QAOA runtime vs depth",
        ylabel="Mean runtime (s)",
    )
    plot_metric_by_depth(
        aggregate_metrics,
        metric_key="mean_evaluations",
        output_path=run_directory / "plots" / "evaluations_vs_depth.png",
        title="QAOA evaluations vs depth",
        ylabel="Mean function evaluations",
    )
    plot_qaoa_parameter_values_by_depth(run_metrics, run_directory / "plots")

    summary = {
        "experiment_name": config.experiment_name,
        "config_path": str(config_path),
        "config": asdict(config),
        "exact_reference": {
            "best_bitstring": list(exact_result.best_bitstring),
            "best_energy": exact_result.best_energy,
            "objective_value": optimum_objective_value,
            "solver_name": exact_result.solver_name,
        },
        "aggregates": aggregate_metrics,
        "runs": run_metrics,
    }
    write_json(run_directory / "config.json", asdict(config))
    write_json(run_directory / "summary.json", summary)
    write_json(run_directory / "artifacts" / "qubo_model.json", qubo_model.as_dict())
    return run_directory
