"""Shared helpers for small variational solvers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qubo_vqa.core.ising import IsingModel
from qubo_vqa.solvers.quantum.backends import QuantumBackendConfig, build_backend


@dataclass(slots=True)
class VariationalEvaluation:
    """One evaluated parameter vector and its basis-state distribution."""

    parameters: np.ndarray
    expectation_energy: float
    dominant_bitstring: tuple[int, ...]
    dominant_probability: float
    dominant_bitstring_energy: float
    probabilities: np.ndarray


def index_to_bitstring(index: int, num_variables: int) -> tuple[int, ...]:
    """Convert a basis-state index to a bitstring ordered by qubit index."""
    return tuple((index >> qubit) & 1 for qubit in range(num_variables))


def bitstring_to_spins(bitstring: tuple[int, ...]) -> tuple[int, ...]:
    """Map a binary bitstring to Ising spins with 0 -> +1 and 1 -> -1."""
    return tuple(1 - 2 * bit for bit in bitstring)


def precompute_ising_basis_energies(ising_model: IsingModel) -> np.ndarray:
    """Precompute the Ising energy of every computational basis state."""
    num_variables = ising_model.num_variables()
    return np.asarray(
        [
            ising_model.energy(bitstring_to_spins(index_to_bitstring(index, num_variables)))
            for index in range(2**num_variables)
        ],
        dtype=float,
    )


def evaluate_variational_circuit(
    *,
    circuit,
    parameters: np.ndarray,
    basis_energies: np.ndarray,
    backend_config: QuantumBackendConfig,
) -> VariationalEvaluation:
    """Evaluate one variational circuit in the computational basis."""
    backend = build_backend(backend_config)
    probabilities = backend.bitstring_probabilities(circuit)
    expectation_energy = float(np.dot(probabilities, basis_energies))
    dominant_index = int(np.argmax(probabilities))
    dominant_bitstring = index_to_bitstring(dominant_index, int(np.log2(len(probabilities))))

    return VariationalEvaluation(
        parameters=np.asarray(parameters, dtype=float),
        expectation_energy=expectation_energy,
        dominant_bitstring=dominant_bitstring,
        dominant_probability=float(probabilities[dominant_index]),
        dominant_bitstring_energy=float(basis_energies[dominant_index]),
        probabilities=probabilities,
    )


def evaluate_statevector_circuit(
    *,
    circuit,
    parameters: np.ndarray,
    basis_energies: np.ndarray,
    backend_config: QuantumBackendConfig,
) -> VariationalEvaluation:
    """Backward-compatible alias for the generic circuit evaluator."""
    return evaluate_variational_circuit(
        circuit=circuit,
        parameters=parameters,
        basis_energies=basis_energies,
        backend_config=backend_config,
    )


def top_basis_probabilities(
    probabilities: np.ndarray,
    basis_energies: np.ndarray,
    limit: int = 5,
) -> list[dict[str, object]]:
    """Summarize the most probable basis states for logging."""
    num_variables = int(np.log2(len(probabilities)))
    ranked_indices = np.argsort(probabilities)[::-1][:limit]
    return [
        {
            "bitstring": list(index_to_bitstring(int(index), num_variables)),
            "probability": float(probabilities[index]),
            "energy": float(basis_energies[index]),
        }
        for index in ranked_indices
    ]
