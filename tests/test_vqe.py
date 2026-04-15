"""Tests for the exact-statevector VQE implementation."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("qiskit")

from qubo_vqa.converters import qubo_to_ising
from qubo_vqa.solvers.quantum.ansatz import describe_vqe_ansatz
from qubo_vqa.solvers.quantum.backends import QuantumBackendConfig
from qubo_vqa.solvers.quantum.common import precompute_ising_basis_energies
from qubo_vqa.solvers.quantum.initialization import QAOAInitializationConfig
from qubo_vqa.solvers.quantum.qaoa import QAOAOptimizerConfig, QAOASolver
from qubo_vqa.solvers.quantum.vqe import (
    VQEInitializationConfig,
    VQEOptimizerConfig,
    VQESolver,
    evaluate_vqe_parameters,
)


def test_problem_aware_zero_parameters_match_uniform_expectation(cycle_maxcut_instance) -> None:
    """Zero problem-aware angles should preserve the uniform superposition average."""
    qubo_model = cycle_maxcut_instance.to_qubo_model()
    ising_model = qubo_to_ising(qubo_model)
    description = describe_vqe_ansatz(ising_model, family="problem_aware", depth=1)
    basis_energies = precompute_ising_basis_energies(ising_model)

    evaluation = evaluate_vqe_parameters(
        ising_model=ising_model,
        parameters=np.zeros(description.parameter_count, dtype=float),
        ansatz_name="problem_aware",
        ansatz_depth=1,
        basis_energies=basis_energies,
        backend_config=QuantumBackendConfig(mode="statevector"),
    )

    assert np.isclose(evaluation.expectation_energy, float(np.mean(basis_energies)))
    assert len(evaluation.dominant_bitstring) == qubo_model.num_variables()


@pytest.mark.parametrize("ansatz_name", ["hardware_efficient", "problem_aware"])
def test_vqe_solver_returns_trace_and_ansatz_metadata(
    cycle_maxcut_instance,
    ansatz_name: str,
) -> None:
    """VQE should produce a standardized result for each supported ansatz family."""
    qubo_model = cycle_maxcut_instance.to_qubo_model()
    solver = VQESolver(
        ansatz_name=ansatz_name,
        ansatz_depth=1,
        optimizer_config=VQEOptimizerConfig(method="COBYLA", maxiter=25, tol=1.0e-3),
        initialization_config=VQEInitializationConfig(
            strategy="small_random",
            seed=7,
            scale=0.2,
        ),
    )

    result = solver.solve(qubo_model, cycle_maxcut_instance.decode_bitstring)

    assert result.solver_name == "vqe"
    assert len(result.best_bitstring) == qubo_model.num_variables()
    assert result.decoded_solution.is_feasible is True
    assert len(result.trace) > 0
    assert result.metadata["ansatz"]["family"] == ansatz_name
    assert "ising_model" in result.metadata
    assert "best_expectation_energy" in result.metadata


def test_vqe_solver_finds_feasible_mvc_cover(cycle_mvc_instance) -> None:
    """VQE should return a feasible tiny MVC cover on the preserved cycle example."""
    qubo_model = cycle_mvc_instance.to_qubo_model()
    solver = VQESolver(
        ansatz_name="hardware_efficient",
        ansatz_depth=1,
        optimizer_config=VQEOptimizerConfig(method="COBYLA", maxiter=160, tol=1.0e-3),
        initialization_config=VQEInitializationConfig(
            strategy="small_random",
            seed=7,
            scale=0.2,
        ),
    )

    result = solver.solve(qubo_model, cycle_mvc_instance.decode_bitstring)

    assert result.solver_name == "vqe"
    assert result.decoded_solution.is_feasible is True
    assert result.decoded_solution.objective_value == 2.0
    assert sorted(result.decoded_solution.interpretation["selected_vertices"]) in ([0, 2], [1, 3])
    assert result.metadata["ansatz"]["family"] == "hardware_efficient"
    assert "ising_model" in result.metadata


def test_qaoa_and_vqe_results_are_comparable_on_shared_mvc_instance(cycle_mvc_instance) -> None:
    """QAOA and VQE should produce comparable standardized results on the same MVC instance."""
    qubo_model = cycle_mvc_instance.to_qubo_model()
    qaoa_solver = QAOASolver(
        reps=1,
        optimizer_config=QAOAOptimizerConfig(method="COBYLA", maxiter=120, tol=1.0e-3),
        initialization_config=QAOAInitializationConfig(strategy="interpolation", seed=7),
    )
    vqe_solver = VQESolver(
        ansatz_name="hardware_efficient",
        ansatz_depth=1,
        optimizer_config=VQEOptimizerConfig(method="COBYLA", maxiter=160, tol=1.0e-3),
        initialization_config=VQEInitializationConfig(
            strategy="small_random",
            seed=7,
            scale=0.2,
        ),
    )

    qaoa_result = qaoa_solver.solve(qubo_model, cycle_mvc_instance.decode_bitstring)
    vqe_result = vqe_solver.solve(qubo_model, cycle_mvc_instance.decode_bitstring)

    for result in (qaoa_result, vqe_result):
        assert result.decoded_solution.is_feasible is True
        assert result.decoded_solution.objective_value == 2.0
        assert len(result.trace) > 0
        assert "ising_model" in result.metadata
