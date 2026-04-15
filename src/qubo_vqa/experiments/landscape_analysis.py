"""Config-driven landscape analysis workflow for Milestone 12."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from qubo_vqa.analysis.barren_plateau import (
    sample_gradient_statistics,
    summarize_gradient_samples,
)
from qubo_vqa.analysis.landscape import (
    ParameterGrid,
    evaluate_qaoa_p1_landscape,
    landscape_records_to_matrix,
    summarize_landscape,
)
from qubo_vqa.analysis.metrics import compute_approximation_ratio, summarize_solver_result
from qubo_vqa.analysis.plots import (
    plot_gradient_norm_histogram,
    plot_heatmap,
    plot_multistart_energy_traces,
)
from qubo_vqa.converters import qubo_to_ising
from qubo_vqa.experiments.config import OutputConfig, ProblemConfig
from qubo_vqa.experiments.logging import create_run_directory
from qubo_vqa.experiments.runner import build_problem
from qubo_vqa.solvers.classical.brute_force import BruteForceSolver
from qubo_vqa.solvers.quantum.ansatz import describe_vqe_ansatz
from qubo_vqa.solvers.quantum.backends import QuantumBackendConfig
from qubo_vqa.solvers.quantum.common import precompute_ising_basis_energies
from qubo_vqa.solvers.quantum.initialization import (
    QAOAInitializationConfig,
    initialize_qaoa_parameters,
)
from qubo_vqa.solvers.quantum.qaoa import (
    QAOAOptimizerConfig,
    QAOASolver,
    evaluate_qaoa_parameters,
)
from qubo_vqa.solvers.quantum.vqe import (
    VQEInitializationConfig,
    VQEOptimizerConfig,
    evaluate_vqe_parameters,
    initialize_vqe_parameters,
)
from qubo_vqa.utils.io import write_csv_rows, write_json
from qubo_vqa.utils.random import set_global_seed


@dataclass(slots=True)
class LandscapeGridConfig:
    """Sampling resolution for the QAOA p=1 landscape heatmap."""

    gamma_bounds: tuple[float, float]
    gamma_points: int
    beta_bounds: tuple[float, float]
    beta_points: int


@dataclass(slots=True)
class GradientConfig:
    """Finite-difference gradient-sampling settings."""

    samples: int
    epsilon: float


@dataclass(slots=True)
class MultiStartConfig:
    """Repeated optimizer runs from different initializations."""

    trials: int


@dataclass(slots=True)
class QAOALandscapeConfig:
    """QAOA settings used by the landscape workflow."""

    reps: int
    max_variables: int
    optimizer: QAOAOptimizerConfig
    backend: QuantumBackendConfig
    landscape: LandscapeGridConfig
    multi_start: MultiStartConfig
    gradient_statistics: GradientConfig


@dataclass(slots=True)
class VQELandscapeConfig:
    """VQE settings used for the trainability side of the workflow."""

    ansatz_family: str
    ansatz_depth: int
    max_variables: int
    optimizer: VQEOptimizerConfig
    backend: QuantumBackendConfig
    initialization: VQEInitializationConfig
    gradient_statistics: GradientConfig


@dataclass(slots=True)
class LandscapeAnalysisConfig:
    """Top-level landscape-analysis configuration."""

    experiment_name: str
    seed: int
    problem: ProblemConfig
    output: OutputConfig
    qaoa: QAOALandscapeConfig
    vqe: VQELandscapeConfig


@dataclass(slots=True)
class _ProblemCarrier:
    """Minimal wrapper for reusing the standard problem builder."""

    seed: int
    problem: ProblemConfig


def _nested_dict(value: object) -> dict[str, Any]:
    """Return a dictionary view for nested config sections."""
    if isinstance(value, dict):
        return dict(value)
    return {}


def _as_backend_config(parameters: dict[str, Any], seed: int) -> QuantumBackendConfig:
    """Build a backend config from a nested YAML section."""
    return QuantumBackendConfig(
        mode=str(parameters.get("mode", "statevector")),
        shots=int(parameters["shots"]) if parameters.get("shots") is not None else None,
        noise_model_name=(
            str(parameters["noise_model_name"])
            if parameters.get("noise_model_name") is not None
            else None
        ),
        seed=int(parameters.get("seed", seed)),
    )


def _parse_bounds(values: object, *, default: tuple[float, float]) -> tuple[float, float]:
    """Normalize a two-value numeric bounds section."""
    if not isinstance(values, list | tuple) or len(values) != 2:
        return default
    return float(values[0]), float(values[1])


def load_landscape_analysis_config(path: str | Path) -> LandscapeAnalysisConfig:
    """Load the landscape-analysis configuration from YAML."""
    raw_payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    qaoa_payload = _nested_dict(raw_payload.get("qaoa"))
    vqe_payload = _nested_dict(raw_payload.get("vqe"))
    qaoa_optimizer = _nested_dict(qaoa_payload.get("optimizer"))
    vqe_optimizer = _nested_dict(vqe_payload.get("optimizer"))
    qaoa_backend = _nested_dict(qaoa_payload.get("backend"))
    vqe_backend = _nested_dict(vqe_payload.get("backend"))
    qaoa_landscape = _nested_dict(qaoa_payload.get("landscape"))
    qaoa_multistart = _nested_dict(qaoa_payload.get("multi_start"))
    qaoa_gradients = _nested_dict(qaoa_payload.get("gradient_statistics"))
    vqe_ansatz = _nested_dict(vqe_payload.get("ansatz"))
    vqe_initialization = _nested_dict(vqe_payload.get("initialization"))
    vqe_gradients = _nested_dict(vqe_payload.get("gradient_statistics"))
    seed = int(raw_payload.get("seed", 0))

    return LandscapeAnalysisConfig(
        experiment_name=str(raw_payload["experiment_name"]),
        seed=seed,
        problem=ProblemConfig(
            name=str(raw_payload["problem"]["name"]),
            parameters=dict(raw_payload["problem"].get("parameters", {})),
        ),
        output=OutputConfig(
            directory=str(raw_payload.get("output", {}).get("directory", "data/results")),
            tag=str(raw_payload.get("output", {}).get("tag", raw_payload["experiment_name"])),
        ),
        qaoa=QAOALandscapeConfig(
            reps=int(qaoa_payload.get("reps", 1)),
            max_variables=int(qaoa_payload.get("max_variables", 12)),
            optimizer=QAOAOptimizerConfig(
                method=str(qaoa_optimizer.get("name", qaoa_optimizer.get("method", "COBYLA"))),
                maxiter=int(qaoa_optimizer.get("maxiter", 60)),
                tol=float(qaoa_optimizer["tol"]) if qaoa_optimizer.get("tol") is not None else None,
                options=_nested_dict(qaoa_optimizer.get("options")),
            ),
            backend=_as_backend_config(qaoa_backend, seed),
            landscape=LandscapeGridConfig(
                gamma_bounds=_parse_bounds(
                    qaoa_landscape.get("gamma_bounds"),
                    default=(0.0, np.pi),
                ),
                gamma_points=int(qaoa_landscape.get("gamma_points", 25)),
                beta_bounds=_parse_bounds(
                    qaoa_landscape.get("beta_bounds"),
                    default=(0.0, np.pi / 2.0),
                ),
                beta_points=int(qaoa_landscape.get("beta_points", 25)),
            ),
            multi_start=MultiStartConfig(trials=int(qaoa_multistart.get("trials", 4))),
            gradient_statistics=GradientConfig(
                samples=int(qaoa_gradients.get("samples", 8)),
                epsilon=float(qaoa_gradients.get("epsilon", 1.0e-2)),
            ),
        ),
        vqe=VQELandscapeConfig(
            ansatz_family=str(vqe_ansatz.get("family", "hardware_efficient")),
            ansatz_depth=int(vqe_ansatz.get("depth", 1)),
            max_variables=int(vqe_payload.get("max_variables", 12)),
            optimizer=VQEOptimizerConfig(
                method=str(vqe_optimizer.get("name", vqe_optimizer.get("method", "COBYLA"))),
                maxiter=int(vqe_optimizer.get("maxiter", 60)),
                tol=float(vqe_optimizer["tol"]) if vqe_optimizer.get("tol") is not None else None,
                options=_nested_dict(vqe_optimizer.get("options")),
            ),
            backend=_as_backend_config(vqe_backend, seed),
            initialization=VQEInitializationConfig(
                strategy=str(vqe_initialization.get("strategy", "uniform")),
                seed=int(vqe_initialization.get("seed", seed)),
                scale=float(vqe_initialization.get("scale", 0.2)),
            ),
            gradient_statistics=GradientConfig(
                samples=int(vqe_gradients.get("samples", 8)),
                epsilon=float(vqe_gradients.get("epsilon", 1.0e-2)),
            ),
        ),
    )


def _sample_qaoa_parameters(sample_count: int, seed: int) -> list[np.ndarray]:
    """Create deterministic random QAOA p=1 parameter samples."""
    return [
        initialize_qaoa_parameters(
            reps=1,
            config=QAOAInitializationConfig(strategy="random", seed=seed + sample_index),
        )
        for sample_index in range(sample_count)
    ]


def _sample_vqe_parameters(
    *,
    sample_count: int,
    parameter_count: int,
    initialization: VQEInitializationConfig,
) -> list[np.ndarray]:
    """Create deterministic VQE parameter samples."""
    return [
        initialize_vqe_parameters(
            parameter_count=parameter_count,
            config=VQEInitializationConfig(
                strategy=initialization.strategy,
                seed=(None if initialization.seed is None else initialization.seed + sample_index),
                scale=initialization.scale,
            ),
        )
        for sample_index in range(sample_count)
    ]


def run_landscape_analysis(
    config_path: str | Path,
    output_directory: str | Path | None = None,
) -> Path:
    """Run the first preserved landscape-analysis workflow."""
    config = load_landscape_analysis_config(config_path)
    if output_directory is not None:
        config.output.directory = str(output_directory)
    if config.qaoa.reps != 1:
        msg = "The preserved landscape workflow currently requires qaoa.reps = 1."
        raise ValueError(msg)

    set_global_seed(config.seed)
    problem = build_problem(_ProblemCarrier(seed=config.seed, problem=config.problem))
    qubo_model = problem.to_qubo_model()
    if qubo_model.num_variables() > config.qaoa.max_variables:
        msg = "The preserved QAOA landscape workflow is limited to small instances."
        raise ValueError(msg)
    if qubo_model.num_variables() > config.vqe.max_variables:
        msg = "The preserved VQE gradient workflow is limited to small instances."
        raise ValueError(msg)
    ising_model = qubo_to_ising(qubo_model)
    basis_energies = precompute_ising_basis_energies(ising_model)
    exact_reference = BruteForceSolver(max_variables=max(20, qubo_model.num_variables())).solve(
        qubo_model,
        problem.decode_bitstring,
    )
    optimum_objective_value = float(exact_reference.decoded_solution.objective_value)
    run_directory = create_run_directory(config.output.directory, config.output.tag)

    landscape_records = evaluate_qaoa_p1_landscape(
        ising_model=ising_model,
        gamma_grid=ParameterGrid(
            *config.qaoa.landscape.gamma_bounds,
            config.qaoa.landscape.gamma_points,
        ),
        beta_grid=ParameterGrid(
            *config.qaoa.landscape.beta_bounds,
            config.qaoa.landscape.beta_points,
        ),
        backend_config=config.qaoa.backend,
    )
    for record in landscape_records:
        decoded = problem.decode_bitstring(tuple(int(bit) for bit in record["dominant_bitstring"]))
        record["objective_value"] = float(decoded.objective_value)
        record["approximation_ratio"] = compute_approximation_ratio(
            float(decoded.objective_value),
            optimum_objective_value,
        )
    write_csv_rows(run_directory / "tables" / "qaoa_p1_landscape.csv", landscape_records)

    beta_values, gamma_values, expectation_matrix = landscape_records_to_matrix(
        landscape_records,
        row_key="beta",
        column_key="gamma",
        value_key="expectation_energy",
    )
    _, _, objective_matrix = landscape_records_to_matrix(
        landscape_records,
        row_key="beta",
        column_key="gamma",
        value_key="objective_value",
    )
    plot_heatmap(
        x_values=gamma_values,
        y_values=beta_values,
        matrix=expectation_matrix,
        output_path=run_directory / "plots" / "qaoa_p1_landscape_energy.png",
        title="QAOA p=1 expectation landscape",
        xlabel="gamma",
        ylabel="beta",
        colorbar_label="Expectation energy",
    )
    plot_heatmap(
        x_values=gamma_values,
        y_values=beta_values,
        matrix=objective_matrix,
        output_path=run_directory / "plots" / "qaoa_p1_landscape_objective.png",
        title="QAOA p=1 dominant-objective landscape",
        xlabel="gamma",
        ylabel="beta",
        colorbar_label="Decoded objective value",
    )

    multi_start_metrics: list[dict[str, Any]] = []
    trace_records: list[dict[str, Any]] = []
    for trial_index in range(config.qaoa.multi_start.trials):
        solver = QAOASolver(
            reps=1,
            backend_config=config.qaoa.backend,
            optimizer_config=config.qaoa.optimizer,
            initialization_config=QAOAInitializationConfig(
                strategy="random",
                seed=config.seed + trial_index,
            ),
            max_variables=config.qaoa.max_variables,
        )
        result = solver.solve(qubo_model, problem.decode_bitstring)
        label = f"qaoa-multistart-trial{trial_index}"
        trace_payload = {"label": label, "trace": result.trace_as_dicts()}
        trace_records.append(trace_payload)
        write_json(run_directory / "traces" / f"{label}.json", trace_payload)
        metrics = summarize_solver_result(result)
        metrics.update(
            {
                "label": label,
                "trial_index": trial_index,
                "seed": config.seed + trial_index,
                "approximation_ratio": compute_approximation_ratio(
                    float(result.decoded_solution.objective_value),
                    optimum_objective_value,
                ),
                "optimization_success": bool(result.metadata["optimization_success"]),
            }
        )
        multi_start_metrics.append(metrics)
    write_csv_rows(run_directory / "tables" / "qaoa_multistart_runs.csv", multi_start_metrics)
    plot_multistart_energy_traces(
        trace_records,
        run_directory / "plots" / "qaoa_multistart_convergence.png",
        title="QAOA multi-start convergence",
    )

    def qaoa_objective(parameters: np.ndarray) -> float:
        """Evaluate one QAOA parameter vector for gradient estimation."""
        return evaluate_qaoa_parameters(
            ising_model=ising_model,
            parameters=parameters,
            reps=1,
            basis_energies=basis_energies,
            backend_config=config.qaoa.backend,
        ).expectation_energy

    qaoa_gradient_samples = sample_gradient_statistics(
        objective=qaoa_objective,
        parameter_samples=_sample_qaoa_parameters(
            config.qaoa.gradient_statistics.samples,
            config.seed + 100,
        ),
        epsilon=config.qaoa.gradient_statistics.epsilon,
    )
    qaoa_gradient_rows = [sample.as_dict() for sample in qaoa_gradient_samples]
    write_csv_rows(run_directory / "tables" / "qaoa_gradient_statistics.csv", qaoa_gradient_rows)
    plot_gradient_norm_histogram(
        qaoa_gradient_rows,
        run_directory / "plots" / "qaoa_gradient_norms.png",
        title="QAOA finite-difference gradient norms",
    )

    ansatz_description = describe_vqe_ansatz(
        ising_model=ising_model,
        family=config.vqe.ansatz_family,
        depth=config.vqe.ansatz_depth,
    )
    def vqe_objective(parameters: np.ndarray) -> float:
        """Evaluate one VQE parameter vector for gradient estimation."""
        return evaluate_vqe_parameters(
            ising_model=ising_model,
            parameters=parameters,
            ansatz_name=config.vqe.ansatz_family,
            ansatz_depth=config.vqe.ansatz_depth,
            basis_energies=basis_energies,
            backend_config=config.vqe.backend,
        ).expectation_energy

    vqe_gradient_samples = sample_gradient_statistics(
        objective=vqe_objective,
        parameter_samples=_sample_vqe_parameters(
            sample_count=config.vqe.gradient_statistics.samples,
            parameter_count=ansatz_description.parameter_count,
            initialization=config.vqe.initialization,
        ),
        epsilon=config.vqe.gradient_statistics.epsilon,
    )
    vqe_gradient_rows = [sample.as_dict() for sample in vqe_gradient_samples]
    write_csv_rows(run_directory / "tables" / "vqe_gradient_statistics.csv", vqe_gradient_rows)
    plot_gradient_norm_histogram(
        vqe_gradient_rows,
        run_directory / "plots" / "vqe_gradient_norms.png",
        title="VQE finite-difference gradient norms",
    )

    summary = {
        "experiment_name": config.experiment_name,
        "config_path": str(config_path),
        "config": asdict(config),
        "exact_reference": {
            "objective_value": optimum_objective_value,
            "best_energy": exact_reference.best_energy,
            "best_bitstring": list(exact_reference.best_bitstring),
        },
        "qaoa_landscape": summarize_landscape(landscape_records),
        "qaoa_multistart": {
            "num_runs": len(multi_start_metrics),
            "best_objective_value": max(
                float(record["objective_value"]) for record in multi_start_metrics
            ),
            "mean_best_expectation_energy": sum(
                float(record.get("best_expectation_energy", record["best_energy"]))
                for record in multi_start_metrics
            )
            / len(multi_start_metrics),
        },
        "qaoa_gradient_statistics": summarize_gradient_samples(qaoa_gradient_samples),
        "vqe_gradient_statistics": summarize_gradient_samples(vqe_gradient_samples),
    }
    write_json(run_directory / "config.json", asdict(config))
    write_json(run_directory / "summary.json", summary)
    write_json(run_directory / "artifacts" / "qubo_model.json", qubo_model.as_dict())
    write_json(run_directory / "artifacts" / "ising_model.json", ising_model.as_dict())
    return run_directory
