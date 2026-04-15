"""Tests for the backend comparison workflow."""

from __future__ import annotations

import json

import pytest

from qubo_vqa.experiments.backend_comparison import run_quantum_backend_comparison


def test_backend_comparison_creates_summary_tables_and_plots(
    backend_comparison_config_path,
    tmp_path,
) -> None:
    """The backend comparison workflow should save summary tables and plots."""
    pytest.importorskip("qiskit")
    pytest.importorskip("qiskit_aer")

    run_directory = run_quantum_backend_comparison(
        backend_comparison_config_path,
        output_directory=tmp_path,
    )

    assert (run_directory / "config.json").exists()
    assert (run_directory / "summary.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "tables" / "run_metrics.csv").exists()
    assert (run_directory / "tables" / "aggregate_metrics.csv").exists()
    assert (run_directory / "traces" / "statevector-trial0.json").exists()
    assert (run_directory / "traces" / "shot_based-trial0.json").exists()
    assert (run_directory / "traces" / "noisy-trial0.json").exists()
    assert (run_directory / "plots" / "objective_value_by_backend.png").exists()
    assert (run_directory / "plots" / "best_expectation_energy_by_backend.png").exists()
    assert (run_directory / "plots" / "runtime_by_backend.png").exists()
    assert (run_directory / "plots" / "success_rate_by_backend.png").exists()

    summary = json.loads((run_directory / "summary.json").read_text(encoding="utf-8"))
    assert summary["exact_reference"]["objective_value"] == 4.0
    assert len(summary["runs"]) == 3
    labels = {record["backend_label"] for record in summary["runs"]}
    assert labels == {"statevector", "shot_based", "noisy"}
