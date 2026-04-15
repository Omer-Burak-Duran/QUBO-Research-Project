"""Tests for the cross-solver comparison workflow."""

from __future__ import annotations

import json

import pytest

pytest.importorskip("openjij")
pytest.importorskip("qiskit")

from qubo_vqa.experiments.solver_comparison import run_solver_comparison


def test_solver_comparison_creates_summary_tables_and_plots(
    solver_comparison_config_path,
    tmp_path,
) -> None:
    """The solver comparison workflow should save summary tables and plots."""
    run_directory = run_solver_comparison(
        solver_comparison_config_path,
        output_directory=tmp_path,
    )

    assert (run_directory / "config.json").exists()
    assert (run_directory / "summary.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "tables" / "run_metrics.csv").exists()
    assert (run_directory / "tables" / "aggregate_metrics.csv").exists()
    assert (run_directory / "traces" / "brute_force-trial0.json").exists()
    assert (run_directory / "traces" / "openjij-trial0.json").exists()
    assert (run_directory / "traces" / "qaoa-trial0.json").exists()
    assert (run_directory / "traces" / "vqe-trial0.json").exists()
    assert (run_directory / "plots" / "objective_value_by_solver.png").exists()
    assert (run_directory / "plots" / "best_energy_by_solver.png").exists()
    assert (run_directory / "plots" / "runtime_by_solver.png").exists()
    assert (run_directory / "plots" / "approximation_ratio_by_solver.png").exists()

    summary = json.loads((run_directory / "summary.json").read_text(encoding="utf-8"))
    assert summary["exact_reference"]["objective_value"] == 4.0
    assert len(summary["runs"]) == 4
    labels = {record["solver_label"] for record in summary["runs"]}
    assert labels == {"brute_force", "openjij", "qaoa", "vqe"}
