"""Tests for the OpenJij classical sampling baseline."""

from __future__ import annotations

import pytest

pytest.importorskip("openjij")

from qubo_vqa.solvers.classical.openjij_solver import OpenJijSolver


def test_openjij_solver_recovers_optimal_maxcut_on_starter_cycle(
    cycle_maxcut_instance,
) -> None:
    """OpenJij should recover the preserved MaxCut optimum on the tiny starter instance."""
    qubo_model = cycle_maxcut_instance.to_qubo_model()
    solver = OpenJijSolver(sampler="sa", num_reads=64, num_sweeps=1000, seed=7)

    result = solver.solve(qubo_model, cycle_maxcut_instance.decode_bitstring)

    assert result.solver_name == "openjij"
    assert result.decoded_solution.is_feasible is True
    assert result.decoded_solution.objective_value == 4.0
    assert result.metadata["sampler"] == "sa"
    assert result.metadata["num_reads"] == 64
    assert len(result.trace) == 64


def test_openjij_solver_finds_feasible_mvc_cover(cycle_mvc_instance) -> None:
    """OpenJij should return a feasible tiny MVC cover on the preserved cycle example."""
    qubo_model = cycle_mvc_instance.to_qubo_model()
    solver = OpenJijSolver(sampler="sa", num_reads=64, num_sweeps=1000, seed=7)

    result = solver.solve(qubo_model, cycle_mvc_instance.decode_bitstring)

    assert result.solver_name == "openjij"
    assert result.decoded_solution.is_feasible is True
    assert result.decoded_solution.objective_value == 2.0
    assert sorted(result.decoded_solution.interpretation["selected_vertices"]) in ([0, 2], [1, 3])
