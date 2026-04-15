"""Benchmark-campaign aggregation and interpretation helpers."""

from __future__ import annotations

from collections import defaultdict
from math import sqrt
from typing import Any


def objective_sense(problem_name: str) -> str:
    """Return whether the semantic objective is minimized or maximized."""
    if problem_name == "minimum_vertex_cover":
        return "min"
    return "max"


def compute_optimality_ratio(
    *,
    problem_name: str,
    objective_value: float,
    optimum_objective_value: float,
) -> float:
    """Normalize semantic objective quality so 1.0 means optimal."""
    if optimum_objective_value <= 0.0:
        msg = "optimum_objective_value must be positive."
        raise ValueError(msg)
    if objective_value <= 0.0:
        return 0.0
    if objective_sense(problem_name) == "min":
        return float(optimum_objective_value / objective_value)
    return float(objective_value / optimum_objective_value)


def _best_objective(problem_name: str, values: list[float]) -> float:
    """Return the best semantic objective value for one problem family."""
    if objective_sense(problem_name) == "min":
        return min(values)
    return max(values)


def _numeric_values(values: list[object]) -> list[float]:
    """Return numeric values, dropping empty placeholders."""
    numeric: list[float] = []
    for value in values:
        if value in (None, ""):
            continue
        numeric.append(float(value))
    return numeric


def _mean(values: list[float]) -> float | None:
    """Return the arithmetic mean when values exist."""
    if not values:
        return None
    return float(sum(values) / len(values))


def _std(values: list[float]) -> float | None:
    """Return the population standard deviation when values exist."""
    if not values:
        return None
    mean_value = _mean(values)
    if mean_value is None:
        return None
    variance = sum((value - mean_value) ** 2 for value in values) / len(values)
    return float(sqrt(variance))


def _rate(values: list[bool | int | float]) -> float | None:
    """Return the mean of boolean-like values."""
    if not values:
        return None
    return float(sum(bool(value) for value in values) / len(values))


def _stats(prefix: str, values: list[object]) -> dict[str, float | None]:
    """Return a standard set of numeric summary fields."""
    numeric = _numeric_values(values)
    if not numeric:
        return {
            f"mean_{prefix}": None,
            f"std_{prefix}": None,
            f"min_{prefix}": None,
            f"max_{prefix}": None,
        }
    return {
        f"mean_{prefix}": _mean(numeric),
        f"std_{prefix}": _std(numeric),
        f"min_{prefix}": float(min(numeric)),
        f"max_{prefix}": float(max(numeric)),
    }


def _group_label(record: dict[str, Any], group_keys: list[str]) -> str:
    """Build a readable group label from selected keys."""
    return "|".join(f"{key}={record[key]}" for key in group_keys)


def _aggregate_group(
    *,
    records: list[dict[str, Any]],
    group_keys: list[str],
    label_key: str,
) -> dict[str, Any]:
    """Aggregate one group of benchmark run metrics."""
    first = records[0]
    problem_name = str(first["problem_name"])
    objective_values = [float(record["objective_value"]) for record in records]
    optimality_ratios = _numeric_values([record.get("optimality_ratio") for record in records])
    runtimes = [float(record["runtime_seconds"]) for record in records]
    evaluations = [float(record["evaluations"]) for record in records]
    expectation_energies = _numeric_values(
        [record.get("best_expectation_energy") for record in records]
    )
    feasibility = [int(record["is_feasible"]) for record in records]
    solver_success = [bool(record.get("solver_success", True)) for record in records]
    optimizer_success = [
        bool(record["optimizer_reported_success"])
        for record in records
        if record.get("optimizer_reported_success") not in (None, "")
    ]
    solution_quality_success = [
        bool(record["solution_quality_success"])
        for record in records
        if record.get("solution_quality_success") not in (None, "")
    ]
    reference_available = [
        bool(record["reference_available"])
        for record in records
        if record.get("reference_available") not in (None, "")
    ]

    aggregate: dict[str, Any] = {key: first[key] for key in group_keys}
    aggregate[label_key] = _group_label(first, group_keys)
    aggregate["num_runs"] = len(records)
    aggregate["best_objective_value"] = _best_objective(problem_name, objective_values)
    aggregate["best_energy"] = min(float(record["best_energy"]) for record in records)
    aggregate["num_reference_runs"] = sum(reference_available)
    aggregate["reference_available_rate"] = _rate(reference_available)
    aggregate["feasibility_rate"] = _rate(feasibility)
    aggregate["success_rate"] = _rate(solver_success)
    aggregate["optimizer_success_rate"] = _rate(optimizer_success)
    aggregate["solution_quality_rate"] = _rate(solution_quality_success)
    if (
        aggregate["solution_quality_rate"] is not None
        and aggregate["optimizer_success_rate"] is not None
    ):
        aggregate["status_quality_gap"] = float(
            aggregate["solution_quality_rate"] - aggregate["optimizer_success_rate"]
        )
    else:
        aggregate["status_quality_gap"] = None
    aggregate.update(_stats("objective_value", objective_values))
    aggregate.update(_stats("optimality_ratio", optimality_ratios))
    aggregate.update(_stats("runtime_seconds", runtimes))
    aggregate.update(_stats("evaluations", evaluations))
    aggregate.update(_stats("best_expectation_energy", expectation_energies))

    optimum_values = _numeric_values([record.get("optimum_objective_value") for record in records])
    aggregate["optimum_objective_value"] = optimum_values[0] if optimum_values else None
    return aggregate


def aggregate_benchmark_group_metrics(
    run_metrics: list[dict[str, Any]],
    *,
    group_keys: list[str],
    label_key: str,
) -> list[dict[str, Any]]:
    """Aggregate benchmark runs across an arbitrary set of grouping keys."""
    grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in run_metrics:
        if any(record.get(key) in (None, "") for key in group_keys):
            continue
        grouped[tuple(str(record[key]) for key in group_keys)].append(record)

    return [
        _aggregate_group(records=records, group_keys=group_keys, label_key=label_key)
        for _, records in sorted(grouped.items())
    ]


def aggregate_benchmark_case_metrics(
    run_metrics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggregate benchmark runs by problem case and solver label."""
    return aggregate_benchmark_group_metrics(
        run_metrics,
        group_keys=[
            "problem_label",
            "problem_name",
            "graph_family",
            "num_variables",
            "solver_label",
            "solver_name",
        ],
        label_key="case_label",
    )


def aggregate_benchmark_solver_family_metrics(
    run_metrics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Aggregate benchmark runs by solver family across all problem cases."""
    return aggregate_benchmark_group_metrics(
        run_metrics,
        group_keys=["solver_name"],
        label_key="solver_family_label",
    )


def _best_record(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Pick the strongest record using quality, then status, then runtime."""
    return max(
        records,
        key=lambda record: (
            float(record["mean_optimality_ratio"] or 0.0),
            float(record["solution_quality_rate"] or 0.0),
            float(record["optimizer_success_rate"] or 0.0),
            -float(record["mean_runtime_seconds"] or 0.0),
        ),
    )


def build_benchmark_interpretation(
    *,
    run_metrics: list[dict[str, Any]],
    case_aggregates: list[dict[str, Any]],
    solver_family_aggregates: list[dict[str, Any]],
    grouped_aggregates: dict[str, list[dict[str, Any]]] | None = None,
    linked_landscape_summaries: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Summarize benchmark results into handoff-friendly interpretation fields."""
    grouped_aggregates = grouped_aggregates or {}
    linked_landscape_summaries = linked_landscape_summaries or []
    problem_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in case_aggregates:
        problem_groups[str(record["problem_label"])].append(record)

    best_solver_per_problem: list[dict[str, Any]] = []
    encoding_stability: list[dict[str, Any]] = []
    qaoa_vs_vqe: list[dict[str, Any]] = []
    structured_vqe: list[dict[str, Any]] = []
    qaoa_initialization: list[dict[str, Any]] = []

    for problem_label in sorted(problem_groups):
        records = problem_groups[problem_label]
        best_record = _best_record(records)
        best_solver_per_problem.append(
            {
                "problem_label": problem_label,
                "problem_name": str(best_record["problem_name"]),
                "solver_label": str(best_record["solver_label"]),
                "solver_name": str(best_record["solver_name"]),
                "mean_optimality_ratio": float(best_record["mean_optimality_ratio"] or 0.0),
                "solution_quality_rate": float(best_record["solution_quality_rate"] or 0.0),
            }
        )
        encoding_stability.append(
            {
                "problem_label": problem_label,
                "problem_name": str(records[0]["problem_name"]),
                "solver_case_count": len(records),
                "all_solver_runs_feasible": all(
                    float(record["feasibility_rate"] or 0.0) == 1.0 for record in records
                ),
                "best_solver_label": str(best_record["solver_label"]),
                "lowest_mean_optimality_ratio": min(
                    float(record["mean_optimality_ratio"] or 0.0) for record in records
                ),
                "lowest_solution_quality_rate": min(
                    float(record["solution_quality_rate"] or 0.0) for record in records
                ),
            }
        )

        qaoa_records = [record for record in records if str(record["solver_name"]) == "qaoa"]
        vqe_records = [record for record in records if str(record["solver_name"]) == "vqe"]
        if qaoa_records and vqe_records:
            best_qaoa = _best_record(qaoa_records)
            best_vqe = _best_record(vqe_records)
            qaoa_ratio = float(best_qaoa["mean_optimality_ratio"] or 0.0)
            vqe_ratio = float(best_vqe["mean_optimality_ratio"] or 0.0)
            winner = "tie"
            if qaoa_ratio > vqe_ratio:
                winner = "qaoa"
            elif vqe_ratio > qaoa_ratio:
                winner = "vqe"
            qaoa_vs_vqe.append(
                {
                    "problem_label": problem_label,
                    "winner": winner,
                    "qaoa_solver_label": str(best_qaoa["solver_label"]),
                    "qaoa_mean_optimality_ratio": qaoa_ratio,
                    "qaoa_solution_quality_rate": float(
                        best_qaoa["solution_quality_rate"] or 0.0
                    ),
                    "vqe_solver_label": str(best_vqe["solver_label"]),
                    "vqe_mean_optimality_ratio": vqe_ratio,
                    "vqe_solution_quality_rate": float(best_vqe["solution_quality_rate"] or 0.0),
                }
            )

        problem_run_metrics = [
            record for record in run_metrics if record["problem_label"] == problem_label
        ]
        problem_aware = [
            record
            for record in problem_run_metrics
            if record.get("vqe_ansatz_family") == "problem_aware"
            and record.get("optimality_ratio") not in (None, "")
        ]
        hardware_efficient = [
            record
            for record in problem_run_metrics
            if record.get("vqe_ansatz_family") == "hardware_efficient"
            and record.get("optimality_ratio") not in (None, "")
        ]
        if problem_aware and hardware_efficient:
            structured_vqe.append(
                {
                    "problem_label": problem_label,
                    "problem_aware_mean_optimality_ratio": _mean(
                        [float(record["optimality_ratio"]) for record in problem_aware]
                    ),
                    "hardware_efficient_mean_optimality_ratio": _mean(
                        [float(record["optimality_ratio"]) for record in hardware_efficient]
                    ),
                }
            )

        interpolation = [
            record
            for record in problem_run_metrics
            if record.get("qaoa_initialization_strategy") == "interpolation"
            and record.get("optimality_ratio") not in (None, "")
        ]
        random = [
            record
            for record in problem_run_metrics
            if record.get("qaoa_initialization_strategy") == "random"
            and record.get("optimality_ratio") not in (None, "")
        ]
        if interpolation and random:
            qaoa_initialization.append(
                {
                    "problem_label": problem_label,
                    "interpolation_mean_optimality_ratio": _mean(
                        [float(record["optimality_ratio"]) for record in interpolation]
                    ),
                    "random_mean_optimality_ratio": _mean(
                        [float(record["optimality_ratio"]) for record in random]
                    ),
                }
            )

    status_quality_gaps = sorted(
        (
            {
                "problem_label": str(record["problem_label"]),
                "solver_label": str(record["solver_label"]),
                "solution_quality_rate": float(record["solution_quality_rate"] or 0.0),
                "optimizer_success_rate": float(record["optimizer_success_rate"] or 0.0),
                "status_quality_gap": float(record["status_quality_gap"] or 0.0),
            }
            for record in case_aggregates
            if record.get("status_quality_gap") not in (None, "")
        ),
        key=lambda record: record["status_quality_gap"],
        reverse=True,
    )[:5]

    bottlenecks = sorted(
        (
            {
                "problem_label": str(record["problem_label"]),
                "solver_label": str(record["solver_label"]),
                "mean_optimality_ratio": float(record["mean_optimality_ratio"] or 0.0),
                "solution_quality_rate": float(record["solution_quality_rate"] or 0.0),
                "optimizer_success_rate": float(record["optimizer_success_rate"] or 0.0),
                "feasibility_rate": float(record["feasibility_rate"] or 0.0),
            }
            for record in case_aggregates
        ),
        key=lambda record: (
            record["mean_optimality_ratio"],
            record["solution_quality_rate"],
            record["optimizer_success_rate"],
            record["feasibility_rate"],
        ),
    )[:5]

    reference_runs = sum(
        bool(record["reference_available"])
        for record in run_metrics
        if record.get("reference_available") not in (None, "")
    )

    return {
        "dataset": {
            "num_problem_cases": len(problem_groups),
            "num_solver_cases": len({str(record["solver_label"]) for record in case_aggregates}),
            "num_total_runs": len(run_metrics),
            "num_reference_runs": reference_runs,
        },
        "encoding_stability": encoding_stability,
        "best_solver_per_problem": best_solver_per_problem,
        "qaoa_vs_vqe": qaoa_vs_vqe,
        "structured_vqe": structured_vqe,
        "qaoa_initialization": qaoa_initialization,
        "solver_family_aggregates": solver_family_aggregates,
        "problem_size_scaling": grouped_aggregates.get("problem_size", []),
        "backend_effects": grouped_aggregates.get("backend", []),
        "qaoa_depth_effects": grouped_aggregates.get("qaoa_depth", []),
        "vqe_depth_effects": grouped_aggregates.get("vqe_depth", []),
        "linked_landscape_summaries": linked_landscape_summaries,
        "status_quality_gaps": status_quality_gaps,
        "bottlenecks": bottlenecks,
    }


def render_benchmark_interpretation_markdown(summary: dict[str, Any]) -> str:
    """Render the benchmark interpretation summary as concise markdown notes."""
    lines = [
        "# Benchmark Campaign Notes",
        "",
        "## Dataset",
        f"- Problem cases: {summary['dataset']['num_problem_cases']}",
        f"- Solver cases: {summary['dataset']['num_solver_cases']}",
        f"- Total runs: {summary['dataset']['num_total_runs']}",
        f"- Runs with exact references: {summary['dataset']['num_reference_runs']}",
        "",
        "## Encoding stability",
    ]
    for record in summary["encoding_stability"]:
        lines.append(
            "- "
            f"{record['problem_label']}: "
            f"all_solver_runs_feasible={record['all_solver_runs_feasible']}, "
            f"best_solver={record['best_solver_label']}, "
            f"lowest_mean_optimality_ratio={record['lowest_mean_optimality_ratio']:.4f}, "
            f"lowest_solution_quality_rate={record['lowest_solution_quality_rate']:.4f}"
        )

    lines.extend(["", "## Best solver per problem"])
    for record in summary["best_solver_per_problem"]:
        lines.append(
            f"- {record['problem_label']}: {record['solver_label']} "
            "("
            f"{record['solver_name']}, "
            f"mean_optimality_ratio={record['mean_optimality_ratio']:.4f}, "
            f"solution_quality_rate={record['solution_quality_rate']:.4f}"
            ")"
        )

    if summary["qaoa_vs_vqe"]:
        lines.extend(["", "## QAOA vs VQE"])
        for record in summary["qaoa_vs_vqe"]:
            lines.append(
                f"- {record['problem_label']}: winner={record['winner']} "
                f"(QAOA={record['qaoa_mean_optimality_ratio']:.4f}, "
                f"VQE={record['vqe_mean_optimality_ratio']:.4f})"
            )

    if summary["structured_vqe"]:
        lines.extend(["", "## Structured VQE"])
        for record in summary["structured_vqe"]:
            lines.append(
                f"- {record['problem_label']}: problem_aware="
                f"{record['problem_aware_mean_optimality_ratio']:.4f}, "
                f"hardware_efficient={record['hardware_efficient_mean_optimality_ratio']:.4f}"
            )

    if summary["qaoa_initialization"]:
        lines.extend(["", "## QAOA initialization"])
        for record in summary["qaoa_initialization"]:
            lines.append(
                f"- {record['problem_label']}: interpolation="
                f"{record['interpolation_mean_optimality_ratio']:.4f}, "
                f"random={record['random_mean_optimality_ratio']:.4f}"
            )

    if summary["problem_size_scaling"]:
        lines.extend(["", "## Problem-size scaling"])
        for record in summary["problem_size_scaling"]:
            lines.append(
                f"- {record['problem_name']} size={int(record['num_variables'])}: "
                f"mean_optimality_ratio={float(record['mean_optimality_ratio'] or 0.0):.4f}, "
                f"mean_runtime_seconds={float(record['mean_runtime_seconds'] or 0.0):.4f}"
            )

    if summary["backend_effects"]:
        lines.extend(["", "## Backend effects"])
        for record in summary["backend_effects"]:
            lines.append(
                f"- {record['backend_group_label']}: "
                f"mean_optimality_ratio={float(record['mean_optimality_ratio'] or 0.0):.4f}, "
                f"optimizer_success_rate={float(record['optimizer_success_rate'] or 0.0):.4f}"
            )

    if summary["linked_landscape_summaries"]:
        lines.extend(["", "## Landscape context"])
        for record in summary["linked_landscape_summaries"]:
            qaoa_gradients = record.get("qaoa_gradient_statistics") or {}
            vqe_gradients = record.get("vqe_gradient_statistics") or {}
            lines.append(
                f"- {record['label']}: "
                f"qaoa_mean_gradient_norm="
                f"{float(qaoa_gradients.get('mean_gradient_norm', 0.0)):.4f}, "
                f"vqe_mean_gradient_norm="
                f"{float(vqe_gradients.get('mean_gradient_norm', 0.0)):.4f}"
            )

    if summary["status_quality_gaps"]:
        lines.extend(["", "## Status-quality gaps"])
        for record in summary["status_quality_gaps"]:
            lines.append(
                f"- {record['problem_label']} / {record['solver_label']}: "
                f"solution_quality_rate={record['solution_quality_rate']:.4f}, "
                f"optimizer_success_rate={record['optimizer_success_rate']:.4f}, "
                f"gap={record['status_quality_gap']:.4f}"
            )

    lines.extend(["", "## Bottlenecks"])
    for record in summary["bottlenecks"]:
        lines.append(
            f"- {record['problem_label']} / {record['solver_label']}: "
            f"mean_optimality_ratio={record['mean_optimality_ratio']:.4f}, "
            f"solution_quality_rate={record['solution_quality_rate']:.4f}, "
            f"optimizer_success_rate={record['optimizer_success_rate']:.4f}, "
            f"feasibility_rate={record['feasibility_rate']:.4f}"
        )
    return "\n".join(lines) + "\n"
