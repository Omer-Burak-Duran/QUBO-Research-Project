"""Traveling Salesman Problem scaffold for a later milestone."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import DecodedSolution
from qubo_vqa.core.types import Bitstring
from qubo_vqa.problems.base import ProblemInstance


@dataclass(slots=True)
class TravelingSalesmanInstance(ProblemInstance):
    """Starter interface for the optional TSP benchmark."""

    distance_matrix: np.ndarray
    name: str = "tsp"

    def num_variables(self) -> int:
        """Return the quadratic encoding size for the instance."""
        num_cities = int(self.distance_matrix.shape[0])
        return num_cities * num_cities

    def to_qubo_model(self) -> QUBOModel:
        """Encode the instance to QUBO in a later milestone."""
        msg = "TSP is intentionally deferred until the foundation is stable."
        raise NotImplementedError(msg)

    def decode_bitstring(
        self,
        bitstring: Bitstring,
        energy: float | None = None,
    ) -> DecodedSolution:
        """Decode a TSP assignment in a later milestone."""
        msg = "TSP decoding is intentionally deferred until the foundation is stable."
        raise NotImplementedError(msg)
