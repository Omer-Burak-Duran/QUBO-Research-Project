"""Tests for QAOA initialization helpers and comparison workflow."""

from __future__ import annotations

import json

import numpy as np
import pytest

from qubo_vqa.experiments.qaoa_initialization import run_qaoa_initialization_comparison
from qubo_vqa.solvers.quantum.initialization import (
    QAOAInitializationConfig,
    initialize_qaoa_parameters,
)


def test_warm_start_interpolates_from_any_lower_depth() -> None:
    """Warm-start should interpolate from any smaller QAOA depth."""
    previous_parameters = np.array([0.1, 0.9, 0.2, 0.4], dtype=float)

    parameters = initialize_qaoa_parameters(
        reps=4,
        config=QAOAInitializationConfig(strategy="warm_start"),
        previous_parameters=previous_parameters,
    )

    assert parameters.shape == (8,)
    assert np.isclose(parameters[0], 0.1)
    assert np.isclose(parameters[3], 0.9)
    assert np.isclose(parameters[4], 0.2)
    assert np.isclose(parameters[7], 0.4)


def test_initialization_comparison_creates_summary_artifacts(
    qaoa_initialization_comparison_config_path,
    tmp_path,
) -> None:
    """The comparison workflow should save summary, traces, and plots."""
    pytest.importorskip("qiskit")

    run_directory = run_qaoa_initialization_comparison(
        qaoa_initialization_comparison_config_path,
        output_directory=tmp_path,
    )

    assert (run_directory / "config.json").exists()
    assert (run_directory / "summary.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "tables" / "run_metrics.csv").exists()
    assert (run_directory / "tables" / "aggregate_metrics.csv").exists()
    assert (run_directory / "traces" / "warm_start-rep2-trial0.json").exists()
    assert (run_directory / "plots" / "warm_start-rep2-trial0_energy_trace.png").exists()
    assert (run_directory / "plots" / "approximation_ratio_vs_depth.png").exists()
    assert (run_directory / "plots" / "runtime_vs_depth.png").exists()
    assert (run_directory / "plots" / "evaluations_vs_depth.png").exists()
    assert (run_directory / "plots" / "best_expectation_energy_vs_depth.png").exists()
    assert (run_directory / "plots" / "final_parameters_warm_start.png").exists()

    summary = json.loads((run_directory / "summary.json").read_text(encoding="utf-8"))
    assert summary["exact_reference"]["objective_value"] == 4.0
    assert len(summary["runs"]) == 8
    warm_start_rep2 = next(
        record
        for record in summary["runs"]
        if record["requested_strategy"] == "warm_start" and record["rep"] == 2
    )
    assert warm_start_rep2["initialization_strategy_used"] == "warm_start"
    assert warm_start_rep2["previous_parameter_count"] == 2
    assert warm_start_rep2["approximation_ratio"] == 1.0
