"""Backend abstractions for exact and future noisy quantum evaluation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from qiskit import QuantumCircuit


@dataclass(slots=True)
class QuantumBackendConfig:
    """Minimal backend descriptor for future exact, shot-based, and noisy modes."""

    mode: str = "statevector"
    shots: int | None = None
    noise_model_name: str | None = None


class QuantumBackend(ABC):
    """Abstract backend interface returning computational basis probabilities."""

    mode: str

    @abstractmethod
    def bitstring_probabilities(self, circuit: QuantumCircuit) -> np.ndarray:
        """Return the computational-basis probabilities for a circuit."""


@dataclass(slots=True)
class ExactStatevectorBackend(QuantumBackend):
    """Exact statevector backend used for the first QAOA milestone."""

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


def build_backend(config: QuantumBackendConfig) -> QuantumBackend:
    """Construct the backend requested by the solver configuration."""
    if config.mode == "statevector":
        return ExactStatevectorBackend()

    msg = f"Unsupported quantum backend mode '{config.mode}' in the current implementation pass."
    raise NotImplementedError(msg)
