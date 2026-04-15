"""Tests for the Milestone 14/15 benchmark campaign workflow."""

from __future__ import annotations

import json

import pytest

pytest.importorskip("openjij")
pytest.importorskip("qiskit")

from qubo_vqa.experiments.sweeps import load_benchmark_campaign_config, run_benchmark_campaign


def test_benchmark_campaign_writes_tables_notes_and_run_artifacts(
    benchmark_campaign_config_path,
    tmp_path,
) -> None:
    """The benchmark campaign should emit aggregate outputs and nested run artifacts."""
    run_directory = run_benchmark_campaign(
        benchmark_campaign_config_path,
        output_directory=tmp_path,
    )

    assert (run_directory / "config.json").exists()
    assert (run_directory / "summary.json").exists()
    assert (run_directory / "notes.md").exists()
    assert (run_directory / "tables" / "run_metrics.csv").exists()
    assert (run_directory / "tables" / "case_aggregates.csv").exists()
    assert (run_directory / "tables" / "solver_family_aggregates.csv").exists()
    assert (run_directory / "tables" / "problem_references.csv").exists()
    assert (run_directory / "tables" / "problem_family_aggregates.csv").exists()
    assert (run_directory / "tables" / "problem_size_aggregates.csv").exists()
    assert (run_directory / "tables" / "backend_aggregates.csv").exists()
    assert (run_directory / "plots" / "optimality_ratio_by_problem_family.png").exists()
    assert (run_directory / "plots" / "optimality_ratio_by_case.png").exists()
    assert (run_directory / "plots" / "runtime_by_case.png").exists()
    assert (run_directory / "plots" / "optimality_ratio_by_solver_family.png").exists()
    assert (
        run_directory
        / "runs"
        / "maxcut-cycle-4"
        / "qaoa_interpolation_p1-trial0"
        / "result.json"
    ).exists()
    assert (
        run_directory
        / "runs"
        / "mvc-cycle-4"
        / "vqe_problem_aware_d1-trial0"
        / "artifacts"
        / "ising_model.json"
    ).exists()

    summary = json.loads((run_directory / "summary.json").read_text(encoding="utf-8"))
    assert len(summary["problem_references"]) == 2
    assert summary["interpretation"]["dataset"]["num_problem_cases"] == 2
    assert summary["interpretation"]["dataset"]["num_solver_cases"] == 6
    assert summary["interpretation"]["dataset"]["num_total_runs"] == 12

    notes = (run_directory / "notes.md").read_text(encoding="utf-8")
    assert "QAOA vs VQE" in notes
    assert "Structured VQE" in notes
    assert "QAOA initialization" in notes


def test_benchmark_campaign_config_supports_explicit_and_sweep_cases(
    backend_benchmark_campaign_config_path,
) -> None:
    """Benchmark configs should expand sweep-driven problem and solver cases."""
    config = load_benchmark_campaign_config(backend_benchmark_campaign_config_path)

    assert len(config.problems) == 2
    assert len(config.solvers) == 8
    labels = {solver.label for solver in config.solvers}
    assert {"qaoa_statevector", "qaoa_shot_based", "qaoa_noisy"} <= labels
    assert {"vqe_statevector", "vqe_shot_based", "vqe_noisy"} <= labels
