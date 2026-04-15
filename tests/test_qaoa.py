"""Tests for the exact-statevector QAOA implementation."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("qiskit")

from qubo_vqa.converters import qubo_to_ising
from qubo_vqa.solvers.quantum.backends import QuantumBackendConfig
from qubo_vqa.solvers.quantum.initialization import QAOAInitializationConfig
from qubo_vqa.solvers.quantum.qaoa import (
    QAOAOptimizerConfig,
    QAOASolver,
    evaluate_qaoa_parameters,
    precompute_ising_basis_energies,
)


def test_qaoa_zero_angles_match_uniform_expectation(cycle_maxcut_instance) -> None:
    """Zero QAOA angles should preserve the uniform superposition energy average."""
    qubo_model = cycle_maxcut_instance.to_qubo_model()
    ising_model = qubo_to_ising(qubo_model)
    basis_energies = precompute_ising_basis_energies(ising_model)

    evaluation = evaluate_qaoa_parameters(
        ising_model=ising_model,
        parameters=np.zeros(2, dtype=float),
        reps=1,
        basis_energies=basis_energies,
        backend_config=QuantumBackendConfig(mode="statevector"),
    )

    assert np.isclose(evaluation.expectation_energy, float(np.mean(basis_energies)))
    assert len(evaluation.dominant_bitstring) == qubo_model.num_variables()


def test_qaoa_solver_returns_trace_and_decoded_solution(cycle_maxcut_instance) -> None:
    """QAOA should produce a complete standardized result on a small MaxCut instance."""
    qubo_model = cycle_maxcut_instance.to_qubo_model()
    solver = QAOASolver(
        reps=1,
        optimizer_config=QAOAOptimizerConfig(method="COBYLA", maxiter=25, tol=1.0e-3),
        initialization_config=QAOAInitializationConfig(strategy="interpolation", seed=7),
    )

    result = solver.solve(qubo_model, cycle_maxcut_instance.decode_bitstring)

    assert result.solver_name == "qaoa"
    assert len(result.best_bitstring) == qubo_model.num_variables()
    assert result.decoded_solution.is_feasible is True
    assert result.decoded_solution.objective_value >= 2.0
    assert len(result.trace) > 0
    assert len(result.metadata["final_parameters"]) == 2
    assert "ising_model" in result.metadata
    assert "best_expectation_energy" in result.metadata
