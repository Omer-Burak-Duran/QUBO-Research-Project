"""Tests for the Milestone 12 landscape-analysis workflow."""

from __future__ import annotations

import json

import numpy as np
import pytest

from qubo_vqa.analysis.barren_plateau import finite_difference_gradient
from qubo_vqa.analysis.landscape import landscape_records_to_matrix
from qubo_vqa.experiments.landscape_analysis import run_landscape_analysis


def test_finite_difference_gradient_matches_quadratic_objective() -> None:
    """Central differences should recover the gradient of a simple quadratic."""
    parameters = np.asarray([1.5, -2.0], dtype=float)

    gradient = finite_difference_gradient(
        objective=lambda values: float(values[0] ** 2 + 3.0 * values[1] ** 2),
        parameters=parameters,
        epsilon=1.0e-5,
    )

    assert np.allclose(gradient, np.asarray([3.0, -12.0], dtype=float), atol=1.0e-3)


def test_landscape_records_to_matrix_preserves_grid_layout() -> None:
    """Flat landscape records should be reshaped into the expected dense matrix."""
    rows, columns, matrix = landscape_records_to_matrix(
        [
            {"beta": 0.0, "gamma": 0.0, "expectation_energy": -1.0},
            {"beta": 0.0, "gamma": 1.0, "expectation_energy": -2.0},
            {"beta": 0.5, "gamma": 0.0, "expectation_energy": -3.0},
            {"beta": 0.5, "gamma": 1.0, "expectation_energy": -4.0},
        ],
        row_key="beta",
        column_key="gamma",
        value_key="expectation_energy",
    )

    assert np.allclose(rows, np.asarray([0.0, 0.5], dtype=float))
    assert np.allclose(columns, np.asarray([0.0, 1.0], dtype=float))
    assert np.allclose(matrix, np.asarray([[-1.0, -2.0], [-3.0, -4.0]], dtype=float))


def test_landscape_analysis_creates_expected_outputs(
    qaoa_landscape_analysis_config_path,
    tmp_path,
) -> None:
    """The landscape workflow should save the expected tables, plots, and summary."""
    pytest.importorskip("qiskit")

    run_directory = run_landscape_analysis(
        qaoa_landscape_analysis_config_path,
        output_directory=tmp_path,
    )

    assert (run_directory / "config.json").exists()
    assert (run_directory / "summary.json").exists()
    assert (run_directory / "artifacts" / "qubo_model.json").exists()
    assert (run_directory / "artifacts" / "ising_model.json").exists()
    assert (run_directory / "tables" / "qaoa_p1_landscape.csv").exists()
    assert (run_directory / "tables" / "qaoa_multistart_runs.csv").exists()
    assert (run_directory / "tables" / "qaoa_gradient_statistics.csv").exists()
    assert (run_directory / "tables" / "vqe_gradient_statistics.csv").exists()
    assert (run_directory / "traces" / "qaoa-multistart-trial0.json").exists()
    assert (run_directory / "plots" / "qaoa_p1_landscape_energy.png").exists()
    assert (run_directory / "plots" / "qaoa_p1_landscape_objective.png").exists()
    assert (run_directory / "plots" / "qaoa_multistart_convergence.png").exists()
    assert (run_directory / "plots" / "qaoa_gradient_norms.png").exists()
    assert (run_directory / "plots" / "vqe_gradient_norms.png").exists()

    summary = json.loads((run_directory / "summary.json").read_text(encoding="utf-8"))
    assert summary["exact_reference"]["objective_value"] == 4.0
    assert summary["qaoa_landscape"]["num_points"] == 441
    assert summary["qaoa_multistart"]["num_runs"] == 4
