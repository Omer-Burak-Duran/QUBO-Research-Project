"""Config-driven experiment runner for the current validated experiment paths."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qubo_vqa.experiments.config import ExperimentConfig, load_experiment_config
from qubo_vqa.experiments.logging import create_run_directory, save_run_outputs
from qubo_vqa.problems.maxcut import MaxCutInstance
from qubo_vqa.solvers.classical.brute_force import BruteForceSolver
from qubo_vqa.solvers.quantum.backends import QuantumBackendConfig
from qubo_vqa.solvers.quantum.initialization import QAOAInitializationConfig
from qubo_vqa.solvers.quantum.qaoa import QAOAOptimizerConfig, QAOASolver
from qubo_vqa.utils.random import set_global_seed


def build_problem(config: ExperimentConfig):
    """Construct the problem instance requested by the config."""
    if config.problem.name != "maxcut":
        msg = f"Unsupported problem '{config.problem.name}' in the current implementation pass."
        raise NotImplementedError(msg)

    parameters = config.problem.parameters
    graph_family = str(parameters.get("graph_family", "cycle"))

    if graph_family == "cycle":
        return MaxCutInstance.cycle_graph(
            num_nodes=int(parameters.get("num_nodes", 4)),
            weight=float(parameters.get("weight", 1.0)),
        )
    if graph_family == "erdos_renyi":
        return MaxCutInstance.erdos_renyi(
            num_nodes=int(parameters.get("num_nodes", 6)),
            edge_probability=float(parameters.get("edge_probability", 0.5)),
            seed=int(parameters.get("seed", config.seed)),
            weighted=bool(parameters.get("weighted", False)),
        )

    msg = f"Unsupported MaxCut graph_family '{graph_family}'."
    raise ValueError(msg)


def _nested_dict(value: object) -> dict[str, Any]:
    """Return a dictionary view for nested config sections."""
    if isinstance(value, dict):
        return dict(value)
    return {}


def build_solver(config: ExperimentConfig):
    """Construct the solver requested by the config."""
    if config.solver.name == "brute_force":
        return BruteForceSolver(
            max_variables=int(config.solver.parameters.get("max_variables", 20))
        )

    if config.solver.name == "qaoa":
        parameters = dict(config.solver.parameters)
        optimizer_parameters = _nested_dict(parameters.get("optimizer"))
        initialization_parameters = _nested_dict(parameters.get("initialization"))
        backend_parameters = _nested_dict(parameters.get("backend"))

        return QAOASolver(
            reps=int(parameters.get("reps", 1)),
            backend_config=QuantumBackendConfig(
                mode=str(
                    backend_parameters.get(
                        "mode",
                        parameters.get("backend_mode", "statevector"),
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
            ),
            optimizer_config=QAOAOptimizerConfig(
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
            initialization_config=QAOAInitializationConfig(
                strategy=str(initialization_parameters.get("strategy", "random")),
                seed=(
                    int(initialization_parameters["seed"])
                    if initialization_parameters.get("seed") is not None
                    else config.seed
                ),
            ),
            max_variables=int(parameters.get("max_variables", 12)),
        )

    msg = f"Unsupported solver '{config.solver.name}' in the current implementation pass."
    raise NotImplementedError(msg)


def run_experiment_from_config(
    config_path: str | Path,
    output_directory: str | Path | None = None,
) -> Path:
    """Run an experiment from a YAML config and save standard output artifacts."""
    config = load_experiment_config(config_path)
    if output_directory is not None:
        config.output.directory = str(output_directory)

    set_global_seed(config.seed)
    problem = build_problem(config)
    qubo_model = problem.to_qubo_model()
    solver = build_solver(config)
    result = solver.solve(qubo_model, problem.decode_bitstring)

    run_directory = create_run_directory(config.output.directory, config.output.tag)
    save_run_outputs(
        run_directory=run_directory,
        config=config,
        result=result,
        config_path=config_path,
        problem_artifacts={
            "graph": problem.graph,
            "qubo_model": qubo_model.as_dict(),
            "ising_model": result.metadata.get("ising_model"),
            "left_partition": result.decoded_solution.interpretation.get("left_partition", []),
            "right_partition": result.decoded_solution.interpretation.get("right_partition", []),
        },
    )
    return run_directory
