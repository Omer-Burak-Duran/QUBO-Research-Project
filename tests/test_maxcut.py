"""Tests for the first benchmark problem."""

from __future__ import annotations

from qubo_vqa.solvers.classical.brute_force import BruteForceSolver


def test_maxcut_cycle_graph_optimum_matches_expected_value(cycle_maxcut_instance) -> None:
    """A 4-cycle has a cut of 4 when alternating labels are selected."""
    qubo_model = cycle_maxcut_instance.to_qubo_model()
    solver = BruteForceSolver()
    result = solver.solve(qubo_model, cycle_maxcut_instance.decode_bitstring)

    assert result.best_energy == -4.0
    assert result.decoded_solution.objective_value == 4.0
    assert result.decoded_solution.is_feasible is True
