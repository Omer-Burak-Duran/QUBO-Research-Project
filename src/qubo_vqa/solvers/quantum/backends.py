"""Backend abstractions for exact, shot-based, and noisy quantum evaluation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from qiskit import QuantumCircuit


@dataclass(slots=True)
class QuantumBackendConfig:
    """Minimal backend descriptor for exact and finite-shot evaluation modes."""

    mode: str = "statevector"
    shots: int | None = None
    noise_model_name: str | None = None
    seed: int | None = None


class QuantumBackend(ABC):
    """Abstract backend interface returning computational basis probabilities."""

    mode: str

    @abstractmethod
    def bitstring_probabilities(self, circuit: QuantumCircuit) -> np.ndarray:
        """Return the computational-basis probabilities for a circuit."""


@dataclass(slots=True)
class ExactStatevectorBackend(QuantumBackend):
    """Exact statevector backend for noiseless variational evaluation."""

    mode: str = "statevector"

    def bitstring_probabilities(self, circuit: QuantumCircuit) -> np.ndarray:
        """Return exact computational basis probabilities from the statevector."""
        try:
            from qiskit.quantum_info import Statevector
        except ImportError as error:
            msg = "Qiskit is required for the exact-statevector QAOA backend."
            raise ImportError(msg) from error

        statevector = Statevector.from_instruction(circuit)
        return np.asarray(statevector.probabilities(), dtype=float)


def _counts_to_probability_vector(
    counts: dict[str, int],
    num_variables: int,
    shots: int,
) -> np.ndarray:
    """Convert Qiskit count labels into a probability vector indexed by qubit order."""
    probabilities = np.zeros(2**num_variables, dtype=float)
    for label, count in counts.items():
        compact_label = label.replace(" ", "")
        index = sum(int(bit) << position for position, bit in enumerate(reversed(compact_label)))
        probabilities[index] = int(count) / float(shots)
    return probabilities


@dataclass(slots=True)
class ShotBasedSamplingBackend(QuantumBackend):
    """Finite-shot backend that samples from the exact noiseless distribution."""

    shots: int
    seed: int | None = None
    mode: str = "shot_based"

    def bitstring_probabilities(self, circuit: QuantumCircuit) -> np.ndarray:
        """Estimate computational-basis probabilities from finite measurement shots."""
        if self.shots <= 0:
            msg = "Shot-based evaluation requires a positive integer number of shots."
            raise ValueError(msg)

        exact_probabilities = ExactStatevectorBackend().bitstring_probabilities(circuit)
        rng = np.random.default_rng(self.seed)
        sampled_counts = rng.multinomial(self.shots, exact_probabilities)
        return sampled_counts.astype(float) / float(self.shots)


def build_noise_model(name: str):
    """Build one of the small named Aer noise models used in Milestone 11."""
    try:
        from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error
    except ImportError as error:
        msg = "qiskit-aer is required for noisy backend execution."
        raise ImportError(msg) from error

    noise_model = NoiseModel()
    if name == "depolarizing_readout":
        one_qubit_error = depolarizing_error(0.002, 1)
        two_qubit_error = depolarizing_error(0.02, 2)
        readout_error = ReadoutError([[0.985, 0.015], [0.02, 0.98]])
    elif name == "light_depolarizing":
        one_qubit_error = depolarizing_error(0.001, 1)
        two_qubit_error = depolarizing_error(0.01, 2)
        readout_error = ReadoutError([[0.992, 0.008], [0.01, 0.99]])
    else:
        msg = f"Unsupported noise model '{name}'."
        raise ValueError(msg)

    for gate_name in ("h", "rx", "ry", "rz", "x", "sx"):
        noise_model.add_all_qubit_quantum_error(one_qubit_error, [gate_name])
    for gate_name in ("cx", "cz", "rzz"):
        noise_model.add_all_qubit_quantum_error(two_qubit_error, [gate_name])
    noise_model.add_all_qubit_readout_error(readout_error)
    return noise_model


@dataclass(slots=True)
class NoisyAerSamplingBackend(QuantumBackend):
    """Finite-shot backend evaluated with an Aer noise model."""

    shots: int
    noise_model_name: str
    seed: int | None = None
    mode: str = "noisy"

    def bitstring_probabilities(self, circuit: QuantumCircuit) -> np.ndarray:
        """Estimate probabilities from a noisy Aer simulation with measurement."""
        if self.shots <= 0:
            msg = "Noisy evaluation requires a positive integer number of shots."
            raise ValueError(msg)

        try:
            from qiskit import transpile
            from qiskit_aer import AerSimulator
        except ImportError as error:
            msg = "qiskit-aer is required for noisy backend execution."
            raise ImportError(msg) from error

        simulator = AerSimulator(noise_model=build_noise_model(self.noise_model_name))
        measured_circuit = circuit.measure_all(inplace=False)
        transpiled_circuit = transpile(
            measured_circuit,
            simulator,
            optimization_level=0,
            seed_transpiler=self.seed,
        )
        result = simulator.run(
            transpiled_circuit,
            shots=self.shots,
            seed_simulator=self.seed,
        ).result()
        counts = result.get_counts()
        return _counts_to_probability_vector(
            counts=counts,
            num_variables=circuit.num_qubits,
            shots=self.shots,
        )


def build_backend(config: QuantumBackendConfig) -> QuantumBackend:
    """Construct the backend requested by the solver configuration."""
    if config.mode == "statevector":
        if config.noise_model_name is not None:
            msg = "statevector mode does not accept a noise model."
            raise ValueError(msg)
        return ExactStatevectorBackend()
    if config.mode in {"shot_based", "shots"}:
        if config.shots is None:
            msg = "Shot-based evaluation requires backend.shots in the experiment config."
            raise ValueError(msg)
        if config.noise_model_name is not None:
            msg = "shot_based mode does not accept a noise model."
            raise ValueError(msg)
        return ShotBasedSamplingBackend(shots=config.shots, seed=config.seed)
    if config.mode in {"noisy", "noisy_shot_based"}:
        if config.shots is None:
            msg = "Noisy evaluation requires backend.shots in the experiment config."
            raise ValueError(msg)
        if config.noise_model_name is None:
            msg = "Noisy evaluation requires backend.noise_model_name in the experiment config."
            raise ValueError(msg)
        return NoisyAerSamplingBackend(
            shots=config.shots,
            noise_model_name=config.noise_model_name,
            seed=config.seed,
        )

    msg = f"Unsupported quantum backend mode '{config.mode}' in the current implementation pass."
    raise NotImplementedError(msg)
