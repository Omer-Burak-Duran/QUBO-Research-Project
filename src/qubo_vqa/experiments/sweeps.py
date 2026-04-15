"""Config-driven benchmark campaigns for Milestones 14 and 15."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from itertools import product
from pathlib import Path
from typing import Any

import yaml

from qubo_vqa.analysis.campaign_summary import (
    aggregate_benchmark_case_metrics,
    aggregate_benchmark_group_metrics,
    aggregate_benchmark_solver_family_metrics,
    build_benchmark_interpretation,
    compute_optimality_ratio,
    render_benchmark_interpretation_markdown,
)
from qubo_vqa.analysis.metrics import summarize_solver_result
from qubo_vqa.analysis.plots import plot_metric_by_category
from qubo_vqa.experiments.config import (
    ExperimentConfig,
    OutputConfig,
    ProblemConfig,
    SolverConfig,
)
from qubo_vqa.experiments.logging import create_run_directory, save_run_outputs
from qubo_vqa.experiments.runner import build_problem, build_solver
from qubo_vqa.solvers.classical.brute_force import BruteForceSolver
from qubo_vqa.utils.io import write_csv_rows, write_json, write_text
from qubo_vqa.utils.random import set_global_seed


@dataclass(slots=True)
class BenchmarkProblemCase:
    """One benchmark problem instance included in a campaign."""

    label: str
    problem: ProblemConfig


@dataclass(slots=True)
class BenchmarkSolverCase:
    """One solver configuration included in a campaign."""

    label: str
    solver: SolverConfig
    trials: int = 1


@dataclass(slots=True)
class BenchmarkCampaignConfig:
    """Top-level configuration for a benchmark campaign."""

    experiment_name: str
    seed: int
    output: OutputConfig
    problems: list[BenchmarkProblemCase]
    solvers: list[BenchmarkSolverCase]
    exact_reference_max_variables: int = 20
    allow_missing_exact_reference: bool = False
    linked_landscape_summaries: list[dict[str, str]] = field(default_factory=list)


@dataclass(slots=True)
class _ProblemCarrier:
    """Minimal wrapper used to reuse the standard problem builder."""

    seed: int
    problem: ProblemConfig


@dataclass(slots=True)
class _SolverCarrier:
    """Minimal wrapper used to reuse the standard solver builder."""

    seed: int
    solver: SolverConfig


def _nested_dict(value: object) -> dict[str, Any]:
    """Return a dictionary view for nested config sections."""
    if isinstance(value, dict):
        return dict(value)
    return {}


def _set_nested_value(payload: dict[str, Any], dotted_key: str, value: object) -> None:
    """Set a nested dictionary value addressed by a dotted key."""
    current = payload
    parts = dotted_key.split(".")
    for part in parts[:-1]:
        nested = current.get(part)
        if not isinstance(nested, dict):
            nested = {}
            current[part] = nested
        current = nested
    current[parts[-1]] = value


def _flatten_for_template(payload: dict[str, Any], *, prefix: str = "") -> dict[str, object]:
    """Flatten nested dictionaries into underscore-friendly template keys."""
    flattened: dict[str, object] = {}
    for key, value in payload.items():
        nested_key = f"{prefix}{key}"
        if isinstance(value, dict):
            flattened.update(_flatten_for_template(value, prefix=f"{nested_key}_"))
            continue
        flattened[nested_key] = value
    return flattened


def _resolve_case_label(
    *,
    case_name: str,
    parameters: dict[str, Any],
    label_template: str | None,
    default_prefix: str,
    index: int,
) -> str:
    """Build a stable case label from a template or fallback."""
    if label_template is None:
        return f"{default_prefix}-{case_name}-{index}"
    context = {"name": case_name, **_flatten_for_template(parameters)}
    return str(label_template.format(**context))


def _expand_problem_cases(campaign_payload: dict[str, Any]) -> list[BenchmarkProblemCase]:
    """Expand explicit problem cases plus sweep-defined problem cases."""
    explicit_cases = [
        BenchmarkProblemCase(
            label=str(case["label"]),
            problem=ProblemConfig(
                name=str(case["name"]),
                parameters=dict(case.get("parameters", {})),
            ),
        )
        for case in campaign_payload.get("problems", [])
    ]
    sweep_cases: list[BenchmarkProblemCase] = []
    for sweep_index, payload in enumerate(campaign_payload.get("problem_sweeps", [])):
        case_name = str(payload["name"])
        base_parameters = _nested_dict(payload.get("base_parameters"))
        sweep_parameters = _nested_dict(payload.get("sweep"))
        keys = list(sweep_parameters)
        values_by_key = [
            list(value) if isinstance(value, list | tuple) else [value]
            for value in sweep_parameters.values()
        ]
        sweep_mode = str(payload.get("mode", "product"))
        if sweep_mode == "zip":
            lengths = {len(values) for values in values_by_key}
            if len(lengths) > 1:
                msg = f"Problem sweep '{case_name}' uses zip mode with unequal value counts."
                raise ValueError(msg)
            combinations = zip(*values_by_key, strict=True)
        else:
            combinations = product(*values_by_key)
        for combination in combinations:
            parameters = deepcopy(base_parameters)
            for key, value in zip(keys, combination, strict=True):
                _set_nested_value(parameters, key, value)
            sweep_cases.append(
                BenchmarkProblemCase(
                    label=_resolve_case_label(
                        case_name=case_name,
                        parameters=parameters,
                        label_template=(
                            str(payload["label_template"])
                            if payload.get("label_template") is not None
                            else None
                        ),
                        default_prefix="problem",
                        index=sweep_index + len(sweep_cases),
                    ),
                    problem=ProblemConfig(name=case_name, parameters=parameters),
                )
            )
    cases = explicit_cases + sweep_cases
    labels = [case.label for case in cases]
    if len(labels) != len(set(labels)):
        msg = "Benchmark campaign problem labels must be unique."
        raise ValueError(msg)
    return cases


def _expand_solver_cases(campaign_payload: dict[str, Any]) -> list[BenchmarkSolverCase]:
    """Expand explicit solver cases plus sweep-defined solver cases."""
    explicit_cases = [
        BenchmarkSolverCase(
            label=str(case["label"]),
            solver=SolverConfig(
                name=str(case["name"]),
                parameters=dict(case.get("parameters", {})),
            ),
            trials=int(case.get("trials", 1)),
        )
        for case in campaign_payload.get("solvers", [])
    ]
    sweep_cases: list[BenchmarkSolverCase] = []
    for sweep_index, payload in enumerate(campaign_payload.get("solver_sweeps", [])):
        case_name = str(payload["name"])
        base_parameters = _nested_dict(payload.get("base_parameters"))
        sweep_parameters = _nested_dict(payload.get("sweep"))
        keys = list(sweep_parameters)
        values_by_key = [
            list(value) if isinstance(value, list | tuple) else [value]
            for value in sweep_parameters.values()
        ]
        sweep_mode = str(payload.get("mode", "product"))
        if sweep_mode == "zip":
            lengths = {len(values) for values in values_by_key}
            if len(lengths) > 1:
                msg = f"Solver sweep '{case_name}' uses zip mode with unequal value counts."
                raise ValueError(msg)
            combinations = zip(*values_by_key, strict=True)
        else:
            combinations = product(*values_by_key)
        for combination in combinations:
            parameters = deepcopy(base_parameters)
            for key, value in zip(keys, combination, strict=True):
                _set_nested_value(parameters, key, value)
            sweep_cases.append(
                BenchmarkSolverCase(
                    label=_resolve_case_label(
                        case_name=case_name,
                        parameters=parameters,
                        label_template=(
                            str(payload["label_template"])
                            if payload.get("label_template") is not None
                            else None
                        ),
                        default_prefix="solver",
                        index=sweep_index + len(sweep_cases),
                    ),
                    solver=SolverConfig(name=case_name, parameters=parameters),
                    trials=int(payload.get("trials", 1)),
                )
            )
    cases = explicit_cases + sweep_cases
    for case in cases:
        if case.trials <= 0:
            msg = f"campaign solver '{case.label}' must request at least one trial."
            raise ValueError(msg)
    labels = [case.label for case in cases]
    if len(labels) != len(set(labels)):
        msg = "Benchmark campaign solver labels must be unique."
        raise ValueError(msg)
    return cases


def load_benchmark_campaign_config(path: str | Path) -> BenchmarkCampaignConfig:
    """Load a benchmark campaign configuration from YAML."""
    raw_payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    campaign_payload = _nested_dict(raw_payload.get("campaign"))
    problems = _expand_problem_cases(campaign_payload)
    solvers = _expand_solver_cases(campaign_payload)
    if not problems:
        msg = "campaign.problems must contain at least one benchmark case."
        raise ValueError(msg)
    if not solvers:
        msg = "campaign.solvers must contain at least one solver case."
        raise ValueError(msg)

    return BenchmarkCampaignConfig(
        experiment_name=str(raw_payload["experiment_name"]),
        seed=int(raw_payload.get("seed", 0)),
        output=OutputConfig(
            directory=str(raw_payload.get("output", {}).get("directory", "data/results")),
            tag=str(raw_payload.get("output", {}).get("tag", raw_payload["experiment_name"])),
        ),
        problems=problems,
        solvers=solvers,
        exact_reference_max_variables=int(
            campaign_payload.get("exact_reference_max_variables", 20)
        ),
        allow_missing_exact_reference=bool(
            campaign_payload.get("allow_missing_exact_reference", False)
        ),
        linked_landscape_summaries=[
            {
                "label": str(entry["label"]),
                "path": str(entry["path"]),
            }
            for entry in campaign_payload.get("linked_landscape_summaries", [])
        ],
    )


def _solver_with_seed(*, solver_case: BenchmarkSolverCase, seed: int):
    """Construct one solver instance with deterministic seed overrides."""
    parameters = dict(solver_case.solver.parameters)
    if solver_case.solver.name == "openjij":
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


def _build_problem_artifacts(problem, qubo_model, result) -> dict[str, object]:
    """Build the same run-artifact payload used by the single-run workflow."""
    artifacts: dict[str, object] = {"qubo_model": qubo_model.as_dict()}
    if result.metadata.get("ising_model") is not None:
        artifacts["ising_model"] = result.metadata["ising_model"]
    if getattr(problem, "name", "") == "maxcut":
        artifacts.update(
            {
                "graph": problem.graph,
                "left_partition": result.decoded_solution.interpretation.get(
                    "left_partition",
                    [],
                ),
                "right_partition": result.decoded_solution.interpretation.get(
                    "right_partition",
                    [],
                ),
            }
        )
    return artifacts


def _solver_case_metadata(solver_case: BenchmarkSolverCase, result) -> dict[str, object]:
    """Extract campaign-level metadata helpful for aggregate interpretation."""
    metadata: dict[str, object] = {
        "solver_label": solver_case.label,
        "solver_name": result.solver_name,
    }
    if result.solver_name == "qaoa":
        metadata["qaoa_reps"] = int(result.metadata["reps"])
        metadata["qaoa_initialization_strategy"] = str(
            result.metadata["initialization"]["strategy"]
        )
        metadata["backend_mode"] = str(result.metadata["backend"]["mode"])
        metadata["backend_shots"] = (
            int(result.metadata["backend"]["shots"])
            if result.metadata["backend"]["shots"] is not None
            else None
        )
        metadata["noise_model_name"] = result.metadata["backend"]["noise_model_name"]
        metadata["optimizer_name"] = str(result.metadata["optimizer"]["method"])
    elif result.solver_name == "vqe":
        metadata["vqe_ansatz_family"] = str(result.metadata["ansatz"]["family"])
        metadata["vqe_ansatz_depth"] = int(result.metadata["ansatz"]["depth"])
        metadata["backend_mode"] = str(result.metadata["backend"]["mode"])
        metadata["backend_shots"] = (
            int(result.metadata["backend"]["shots"])
            if result.metadata["backend"]["shots"] is not None
            else None
        )
        metadata["noise_model_name"] = result.metadata["backend"]["noise_model_name"]
        metadata["optimizer_name"] = str(result.metadata["optimizer"]["method"])
    elif result.solver_name == "openjij":
        metadata["openjij_sampler"] = str(result.metadata["sampler"])
    return metadata


def _problem_case_metadata(problem_case: BenchmarkProblemCase, qubo_model) -> dict[str, object]:
    """Extract campaign-level metadata about the encoded benchmark case."""
    parameters = dict(problem_case.problem.parameters)
    return {
        "problem_label": problem_case.label,
        "problem_name": problem_case.problem.name,
        "graph_family": str(parameters.get("graph_family", "unknown")),
        "num_variables": qubo_model.num_variables(),
        "problem_seed": (
            int(parameters["seed"]) if parameters.get("seed") is not None else None
        ),
    }


def _exact_reference_result(
    *,
    config: BenchmarkCampaignConfig,
    qubo_model,
    decoder,
):
    """Return the exact reference result when the size cap allows it."""
    if qubo_model.num_variables() > config.exact_reference_max_variables:
        if config.allow_missing_exact_reference:
            return None
        msg = (
            "Benchmark campaign requested an exact reference for a problem "
            "larger than exact_reference_max_variables."
        )
        raise ValueError(msg)
    return BruteForceSolver(
        max_variables=max(config.exact_reference_max_variables, qubo_model.num_variables())
    ).solve(qubo_model, decoder)


def _load_linked_landscape_summaries(
    linked_summaries: list[dict[str, str]],
) -> list[dict[str, Any]]:
    """Load linked landscape-analysis summaries when provided."""
    loaded: list[dict[str, Any]] = []
    for entry in linked_summaries:
        summary_path = Path(entry["path"])
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
        loaded.append(
            {
                "label": str(entry["label"]),
                "path": str(summary_path),
                "qaoa_landscape": payload.get("qaoa_landscape"),
                "qaoa_gradient_statistics": payload.get("qaoa_gradient_statistics"),
                "vqe_gradient_statistics": payload.get("vqe_gradient_statistics"),
            }
        )
    return loaded


def run_benchmark_campaign(
    config_path: str | Path,
    output_directory: str | Path | None = None,
) -> Path:
    """Run a benchmark campaign and write aggregate outputs."""
    config = load_benchmark_campaign_config(config_path)
    if output_directory is not None:
        config.output.directory = str(output_directory)

    set_global_seed(config.seed)
    run_directory = create_run_directory(config.output.directory, config.output.tag)
    run_metrics: list[dict[str, Any]] = []
    problem_references: list[dict[str, Any]] = []

    for problem_case in config.problems:
        problem = build_problem(_ProblemCarrier(seed=config.seed, problem=problem_case.problem))
        qubo_model = problem.to_qubo_model()
        exact_reference = _exact_reference_result(
            config=config,
            qubo_model=qubo_model,
            decoder=problem.decode_bitstring,
        )
        optimum_objective_value = (
            float(exact_reference.decoded_solution.objective_value)
            if exact_reference is not None
            else None
        )
        problem_references.append(
            {
                "problem_label": problem_case.label,
                "problem_name": problem_case.problem.name,
                "graph_family": str(problem_case.problem.parameters.get("graph_family", "unknown")),
                "num_variables": qubo_model.num_variables(),
                "reference_available": exact_reference is not None,
                "optimum_objective_value": optimum_objective_value,
                "optimum_energy": (
                    exact_reference.best_energy if exact_reference is not None else None
                ),
                "optimum_bitstring": (
                    list(exact_reference.best_bitstring) if exact_reference is not None else None
                ),
            }
        )

        for solver_case in config.solvers:
            for trial_index in range(solver_case.trials):
                trial_seed = config.seed + trial_index
                solver = _solver_with_seed(solver_case=solver_case, seed=trial_seed)
                result = solver.solve(qubo_model, problem.decode_bitstring)
                subrun_directory = (
                    run_directory
                    / "runs"
                    / problem_case.label
                    / f"{solver_case.label}-trial{trial_index}"
                )
                save_run_outputs(
                    run_directory=subrun_directory,
                    config=ExperimentConfig(
                        experiment_name=(
                            f"{config.experiment_name}:{problem_case.label}:{solver_case.label}:"
                            f"trial{trial_index}"
                        ),
                        seed=trial_seed,
                        problem=problem_case.problem,
                        solver=solver_case.solver,
                        output=OutputConfig(
                            directory=str(run_directory),
                            tag=subrun_directory.name,
                        ),
                    ),
                    result=result,
                    config_path=config_path,
                    problem_artifacts=_build_problem_artifacts(problem, qubo_model, result),
                )
                metrics = summarize_solver_result(result)
                solver_success = bool(
                    result.metadata.get(
                        "optimization_success",
                        result.metadata.get("sampling_success", True),
                    )
                )
                optimizer_reported_success = result.metadata.get("optimization_success")
                optimality_ratio = (
                    compute_optimality_ratio(
                        problem_name=problem_case.problem.name,
                        objective_value=float(result.decoded_solution.objective_value),
                        optimum_objective_value=float(optimum_objective_value),
                    )
                    if optimum_objective_value is not None
                    else None
                )
                metrics.update(
                    {
                        "trial_index": trial_index,
                        "seed": trial_seed,
                        "optimum_objective_value": optimum_objective_value,
                        "reference_available": optimum_objective_value is not None,
                        "optimality_ratio": optimality_ratio,
                        "solution_quality_success": (
                            bool(optimality_ratio >= 0.999999)
                            if optimality_ratio is not None
                            else None
                        ),
                        "solver_success": solver_success,
                        "optimizer_reported_success": (
                            bool(optimizer_reported_success)
                            if optimizer_reported_success is not None
                            else None
                        ),
                        "run_completed": 1,
                        **_problem_case_metadata(problem_case, qubo_model),
                        **_solver_case_metadata(solver_case, result),
                    }
                )
                run_metrics.append(metrics)

    case_aggregates = aggregate_benchmark_case_metrics(run_metrics)
    solver_family_aggregates = aggregate_benchmark_solver_family_metrics(run_metrics)
    grouped_aggregates = {
        "problem_family": aggregate_benchmark_group_metrics(
            run_metrics,
            group_keys=["problem_name", "graph_family", "num_variables"],
            label_key="problem_group_label",
        ),
        "problem_size": aggregate_benchmark_group_metrics(
            run_metrics,
            group_keys=["problem_name", "num_variables"],
            label_key="problem_size_label",
        ),
        "backend": aggregate_benchmark_group_metrics(
            run_metrics,
            group_keys=["solver_name", "backend_mode"],
            label_key="backend_group_label",
        ),
        "qaoa_depth": aggregate_benchmark_group_metrics(
            run_metrics,
            group_keys=["problem_name", "qaoa_reps", "backend_mode"],
            label_key="qaoa_depth_label",
        ),
        "vqe_depth": aggregate_benchmark_group_metrics(
            run_metrics,
            group_keys=["problem_name", "vqe_ansatz_family", "vqe_ansatz_depth", "backend_mode"],
            label_key="vqe_depth_label",
        ),
    }
    linked_landscape_summaries = _load_linked_landscape_summaries(
        config.linked_landscape_summaries
    )
    interpretation = build_benchmark_interpretation(
        run_metrics=run_metrics,
        case_aggregates=case_aggregates,
        solver_family_aggregates=solver_family_aggregates,
        grouped_aggregates=grouped_aggregates,
        linked_landscape_summaries=linked_landscape_summaries,
    )

    write_json(run_directory / "config.json", asdict(config))
    write_json(
        run_directory / "summary.json",
        {
            "experiment_name": config.experiment_name,
            "config_path": str(config_path),
            "config": asdict(config),
            "problem_references": problem_references,
            "case_aggregates": case_aggregates,
            "solver_family_aggregates": solver_family_aggregates,
            "grouped_aggregates": grouped_aggregates,
            "linked_landscape_summaries": linked_landscape_summaries,
            "interpretation": interpretation,
        },
    )
    write_text(
        run_directory / "notes.md",
        render_benchmark_interpretation_markdown(interpretation),
    )
    write_csv_rows(run_directory / "tables" / "run_metrics.csv", run_metrics)
    write_csv_rows(run_directory / "tables" / "case_aggregates.csv", case_aggregates)
    write_csv_rows(
        run_directory / "tables" / "solver_family_aggregates.csv",
        solver_family_aggregates,
    )
    write_csv_rows(run_directory / "tables" / "problem_references.csv", problem_references)
    write_csv_rows(
        run_directory / "tables" / "problem_family_aggregates.csv",
        grouped_aggregates["problem_family"],
    )
    write_csv_rows(
        run_directory / "tables" / "problem_size_aggregates.csv",
        grouped_aggregates["problem_size"],
    )
    write_csv_rows(
        run_directory / "tables" / "backend_aggregates.csv",
        grouped_aggregates["backend"],
    )
    write_csv_rows(
        run_directory / "tables" / "qaoa_depth_aggregates.csv",
        grouped_aggregates["qaoa_depth"],
    )
    write_csv_rows(
        run_directory / "tables" / "vqe_depth_aggregates.csv",
        grouped_aggregates["vqe_depth"],
    )
    plot_metric_by_category(
        case_aggregates,
        category_key="case_label",
        metric_key="mean_optimality_ratio",
        output_path=run_directory / "plots" / "optimality_ratio_by_case.png",
        title="Mean optimality ratio by benchmark case",
        ylabel="Mean optimality ratio",
        rotation=45.0,
    )
    plot_metric_by_category(
        case_aggregates,
        category_key="case_label",
        metric_key="mean_runtime_seconds",
        output_path=run_directory / "plots" / "runtime_by_case.png",
        title="Mean runtime by benchmark case",
        ylabel="Mean runtime (s)",
        rotation=45.0,
    )
    plot_metric_by_category(
        solver_family_aggregates,
        category_key="solver_name",
        metric_key="mean_optimality_ratio",
        output_path=run_directory / "plots" / "optimality_ratio_by_solver_family.png",
        title="Mean optimality ratio by solver family",
        ylabel="Mean optimality ratio",
    )
    plot_metric_by_category(
        grouped_aggregates["problem_family"],
        category_key="problem_group_label",
        metric_key="mean_optimality_ratio",
        output_path=run_directory / "plots" / "optimality_ratio_by_problem_family.png",
        title="Mean optimality ratio by problem family",
        ylabel="Mean optimality ratio",
        rotation=45.0,
    )
    plot_metric_by_category(
        grouped_aggregates["backend"],
        category_key="backend_group_label",
        metric_key="mean_optimality_ratio",
        output_path=run_directory / "plots" / "optimality_ratio_by_backend.png",
        title="Mean optimality ratio by backend group",
        ylabel="Mean optimality ratio",
        rotation=45.0,
    )
    return run_directory
