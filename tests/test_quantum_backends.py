"""Tests for shot-based quantum backend support."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("qiskit")

from qubo_vqa.converters import qubo_to_ising
from qubo_vqa.solvers.quantum.ansatz import describe_vqe_ansatz
from qubo_vqa.solvers.quantum.backends import (
    QuantumBackendConfig,
    build_backend,
    build_noise_model,
)
from qubo_vqa.solvers.quantum.common import precompute_ising_basis_energies
from qubo_vqa.solvers.quantum.qaoa import evaluate_qaoa_parameters
from qubo_vqa.solvers.quantum.vqe import evaluate_vqe_parameters


def test_shot_based_backend_requires_shots() -> None:
    """Shot-based mode should reject configs that omit the shot count."""
    with pytest.raises(ValueError, match="backend.shots"):
        build_backend(QuantumBackendConfig(mode="shot_based"))


def test_qaoa_shot_based_evaluation_is_reproducible(cycle_maxcut_instance) -> None:
    """Shot-based QAOA evaluation should be deterministic for a fixed backend seed."""
    qubo_model = cycle_maxcut_instance.to_qubo_model()
    ising_model = qubo_to_ising(qubo_model)
    basis_energies = precompute_ising_basis_energies(ising_model)
    backend_config = QuantumBackendConfig(mode="shot_based", shots=4096, seed=11)

    first = evaluate_qaoa_parameters(
        ising_model=ising_model,
        parameters=np.zeros(2, dtype=float),
        reps=1,
        basis_energies=basis_energies,
        backend_config=backend_config,
    )
    second = evaluate_qaoa_parameters(
        ising_model=ising_model,
        parameters=np.zeros(2, dtype=float),
        reps=1,
        basis_energies=basis_energies,
        backend_config=backend_config,
    )

    assert np.array_equal(first.probabilities, second.probabilities)
    assert first.expectation_energy == second.expectation_energy
    assert np.isclose(first.expectation_energy, float(np.mean(basis_energies)), atol=0.15)


def test_vqe_shot_based_evaluation_tracks_uniform_reference(cycle_maxcut_instance) -> None:
    """Zero-parameter shot-based VQE should stay close to the uniform expectation."""
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
        backend_config=QuantumBackendConfig(mode="shot_based", shots=4096, seed=17),
    )

    assert np.isclose(evaluation.expectation_energy, float(np.mean(basis_energies)), atol=0.15)
    assert np.isclose(float(np.sum(evaluation.probabilities)), 1.0)


def test_noisy_backend_requires_noise_model_name() -> None:
    """Noisy mode should reject configs that omit the named noise model."""
    with pytest.raises(ValueError, match="noise_model_name"):
        build_backend(QuantumBackendConfig(mode="noisy", shots=1024))


def test_noise_model_registry_supports_expected_name() -> None:
    """The default named noise model should be constructible when Aer is installed."""
    pytest.importorskip("qiskit_aer")
    noise_model = build_noise_model("depolarizing_readout")
    assert noise_model is not None


def test_qaoa_noisy_evaluation_is_reproducible(cycle_maxcut_instance) -> None:
    """Noisy Aer evaluation should be deterministic for a fixed simulator seed."""
    pytest.importorskip("qiskit_aer")

    qubo_model = cycle_maxcut_instance.to_qubo_model()
    ising_model = qubo_to_ising(qubo_model)
    basis_energies = precompute_ising_basis_energies(ising_model)
    backend_config = QuantumBackendConfig(
        mode="noisy",
        shots=2048,
        noise_model_name="depolarizing_readout",
        seed=19,
    )

    first = evaluate_qaoa_parameters(
        ising_model=ising_model,
        parameters=np.zeros(2, dtype=float),
        reps=1,
        basis_energies=basis_energies,
        backend_config=backend_config,
    )
    second = evaluate_qaoa_parameters(
        ising_model=ising_model,
        parameters=np.zeros(2, dtype=float),
        reps=1,
        basis_energies=basis_energies,
        backend_config=backend_config,
    )

    assert np.array_equal(first.probabilities, second.probabilities)
    assert np.isclose(float(np.sum(first.probabilities)), 1.0)
    assert first.expectation_energy == second.expectation_energy
