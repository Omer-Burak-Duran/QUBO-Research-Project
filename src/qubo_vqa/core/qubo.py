"""Canonical QUBO representation used across benchmark problems."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from qubo_vqa.core.types import Bitstring, Metadata


@dataclass(slots=True)
class QUBOModel:
    """Upper-triangular QUBO model with a minimization-oriented energy interface."""

    q_matrix: np.ndarray
    offset: float = 0.0
    sense: str = "min"
    variable_names: list[str] = field(default_factory=list)
    metadata: Metadata = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate shape and normalize metadata."""
        matrix = np.asarray(self.q_matrix, dtype=float)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            msg = "QUBO q_matrix must be a square matrix."
            raise ValueError(msg)
        if self.sense not in {"min", "max"}:
            msg = "QUBO sense must be either 'min' or 'max'."
            raise ValueError(msg)
        if not self.variable_names:
            self.variable_names = [f"x_{index}" for index in range(matrix.shape[0])]
        if len(self.variable_names) != matrix.shape[0]:
            msg = "variable_names length must match the QUBO dimension."
            raise ValueError(msg)
        self.q_matrix = np.triu(matrix)

    def num_variables(self) -> int:
        """Return the number of binary decision variables."""
        return int(self.q_matrix.shape[0])

    def energy(self, bitstring: Bitstring) -> float:
        """Evaluate the QUBO energy for a binary assignment."""
        vector = np.asarray(bitstring, dtype=int)
        if vector.shape != (self.num_variables(),):
            msg = "Bitstring length does not match the QUBO dimension."
            raise ValueError(msg)

        diagonal_energy = float(np.dot(np.diag(self.q_matrix), vector))
        upper_rows, upper_cols = np.triu_indices(self.num_variables(), k=1)
        pairwise_energy = float(
            np.sum(self.q_matrix[upper_rows, upper_cols] * vector[upper_rows] * vector[upper_cols])
        )
        return self.offset + diagonal_energy + pairwise_energy

    def as_dict(self) -> Metadata:
        """Convert the model to a JSON-friendly dictionary."""
        return {
            "q_matrix": self.q_matrix.tolist(),
            "offset": self.offset,
            "sense": self.sense,
            "variable_names": list(self.variable_names),
            "metadata": dict(self.metadata),
        }
