"""Tests for the Minimum Vertex Cover benchmark problem."""

from __future__ import annotations

import itertools

from qubo_vqa.solvers.classical.brute_force import BruteForceSolver


def test_mvc_path_graph_optimum_matches_expected_value(path_mvc_instance) -> None:
    """A 4-node path has a minimum vertex cover of size 2."""
    qubo_model = path_mvc_instance.to_qubo_model()
    solver = BruteForceSolver()
    result = solver.solve(qubo_model, path_mvc_instance.decode_bitstring)

    assert result.best_energy == 2.0
    assert result.decoded_solution.objective_value == 2.0
    assert result.decoded_solution.is_feasible is True
    assert result.decoded_solution.interpretation["uncovered_edge_count"] == 0


def test_mvc_decode_reports_objective_and_penalty_consistently(path_mvc_instance) -> None:
    """Decoded MVC metrics should match the intended objective-plus-penalty model."""
    qubo_model = path_mvc_instance.to_qubo_model()

    for bitstring in itertools.product((0, 1), repeat=qubo_model.num_variables()):
        decoded = path_mvc_instance.decode_bitstring(bitstring)
        uncovered_edge_count = int(decoded.interpretation["uncovered_edge_count"])
        expected_objective = float(sum(bitstring))
        expected_penalty = float(path_mvc_instance.penalty_strength * uncovered_edge_count)

        assert decoded.objective_value == expected_objective
        assert decoded.penalty == expected_penalty
        assert decoded.total_energy == qubo_model.energy(bitstring)
        assert decoded.total_energy == expected_objective + expected_penalty
