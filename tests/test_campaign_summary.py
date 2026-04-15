"""Unit tests for benchmark campaign aggregation and interpretation."""

from __future__ import annotations

import json

from qubo_vqa.analysis.campaign_summary import (
    aggregate_benchmark_case_metrics,
    aggregate_benchmark_group_metrics,
    build_benchmark_interpretation,
    compute_optimality_ratio,
    render_benchmark_interpretation_markdown,
)


def test_compute_optimality_ratio_handles_max_and_min_objectives() -> None:
    """Optimality ratio should normalize max and min problems to the same scale."""
    assert compute_optimality_ratio(
        problem_name="maxcut",
        objective_value=4.0,
        optimum_objective_value=4.0,
    ) == 1.0
    assert compute_optimality_ratio(
        problem_name="minimum_vertex_cover",
        objective_value=2.0,
        optimum_objective_value=2.0,
    ) == 1.0
    assert compute_optimality_ratio(
        problem_name="minimum_vertex_cover",
        objective_value=4.0,
        optimum_objective_value=2.0,
    ) == 0.5


def test_campaign_aggregation_tracks_status_quality_gap() -> None:
    """Case aggregates should separate optimizer status from solution quality."""
    run_metrics = [
        {
            "problem_label": "maxcut-cycle-4",
            "problem_name": "maxcut",
            "graph_family": "cycle",
            "num_variables": 4,
            "solver_label": "vqe_problem_aware_d1",
            "solver_name": "vqe",
            "objective_value": 4.0,
            "optimality_ratio": 1.0,
            "best_energy": -4.0,
            "runtime_seconds": 0.1,
            "evaluations": 60,
            "is_feasible": 1,
            "solver_success": True,
            "optimizer_reported_success": False,
            "solution_quality_success": True,
            "reference_available": True,
            "optimum_objective_value": 4.0,
        }
    ]

    aggregates = aggregate_benchmark_case_metrics(run_metrics)
    assert len(aggregates) == 1
    assert aggregates[0]["solution_quality_rate"] == 1.0
    assert aggregates[0]["optimizer_success_rate"] == 0.0
    assert aggregates[0]["status_quality_gap"] == 1.0


def test_group_aggregation_supports_backend_slices() -> None:
    """Arbitrary group slices should be emitted for backend-oriented summaries."""
    grouped = aggregate_benchmark_group_metrics(
        [
            {
                "problem_name": "maxcut",
                "graph_family": "cycle",
                "num_variables": 4,
                "solver_name": "qaoa",
                "backend_mode": "statevector",
                "objective_value": 4.0,
                "optimality_ratio": 1.0,
                "best_energy": -4.0,
                "runtime_seconds": 0.1,
                "evaluations": 30,
                "is_feasible": 1,
                "solver_success": True,
                "optimizer_reported_success": True,
                "solution_quality_success": True,
                "reference_available": True,
            },
            {
                "problem_name": "maxcut",
                "graph_family": "cycle",
                "num_variables": 4,
                "solver_name": "qaoa",
                "backend_mode": "shot_based",
                "objective_value": 4.0,
                "optimality_ratio": 1.0,
                "best_energy": -4.0,
                "runtime_seconds": 0.2,
                "evaluations": 35,
                "is_feasible": 1,
                "solver_success": True,
                "optimizer_reported_success": True,
                "solution_quality_success": True,
                "reference_available": True,
            },
        ],
        group_keys=["solver_name", "backend_mode"],
        label_key="backend_group_label",
    )

    labels = {record["backend_group_label"] for record in grouped}
    assert labels == {
        "solver_name=qaoa|backend_mode=shot_based",
        "solver_name=qaoa|backend_mode=statevector",
    }


def test_interpretation_renders_ties_and_landscape_context(tmp_path) -> None:
    """Interpretation should preserve ties and show linked landscape context."""
    linked_summary = {
        "label": "starter-landscape",
        "path": str(tmp_path / "summary.json"),
        "qaoa_gradient_statistics": {"mean_gradient_norm": 2.0},
        "vqe_gradient_statistics": {"mean_gradient_norm": 0.5},
    }
    (tmp_path / "summary.json").write_text(json.dumps({"ok": True}), encoding="utf-8")

    run_metrics = [
        {
            "problem_label": "maxcut-cycle-4",
            "problem_name": "maxcut",
            "graph_family": "cycle",
            "num_variables": 4,
            "solver_label": "qaoa_p1",
            "solver_name": "qaoa",
            "qaoa_initialization_strategy": "interpolation",
            "objective_value": 4.0,
            "optimality_ratio": 1.0,
            "best_energy": -4.0,
            "runtime_seconds": 0.1,
            "evaluations": 30,
            "is_feasible": 1,
            "solver_success": True,
            "optimizer_reported_success": True,
            "solution_quality_success": True,
            "reference_available": True,
        },
        {
            "problem_label": "maxcut-cycle-4",
            "problem_name": "maxcut",
            "graph_family": "cycle",
            "num_variables": 4,
            "solver_label": "vqe_problem_aware_d1",
            "solver_name": "vqe",
            "vqe_ansatz_family": "problem_aware",
            "objective_value": 4.0,
            "optimality_ratio": 1.0,
            "best_energy": -4.0,
            "runtime_seconds": 0.1,
            "evaluations": 40,
            "is_feasible": 1,
            "solver_success": True,
            "optimizer_reported_success": False,
            "solution_quality_success": True,
            "reference_available": True,
        },
    ]
    case_aggregates = aggregate_benchmark_case_metrics(run_metrics)
    solver_family_aggregates = aggregate_benchmark_group_metrics(
        run_metrics,
        group_keys=["solver_name"],
        label_key="solver_family_label",
    )

    interpretation = build_benchmark_interpretation(
        run_metrics=run_metrics,
        case_aggregates=case_aggregates,
        solver_family_aggregates=solver_family_aggregates,
        grouped_aggregates={},
        linked_landscape_summaries=[linked_summary],
    )
    notes = render_benchmark_interpretation_markdown(interpretation)

    assert interpretation["qaoa_vs_vqe"][0]["winner"] == "tie"
    assert "Landscape context" in notes
    assert "winner=tie" in notes
