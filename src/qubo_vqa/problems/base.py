"""Base problem interfaces used by benchmark encoders."""

from __future__ import annotations

from abc import ABC, abstractmethod

from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import DecodedSolution
from qubo_vqa.core.types import Bitstring


class ProblemInstance(ABC):
    """Abstract problem instance with encoding and decoding hooks."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the benchmark family name."""

    @abstractmethod
    def num_variables(self) -> int:
        """Return the number of binary variables in the encoding."""

    @abstractmethod
    def to_qubo_model(self) -> QUBOModel:
        """Encode the instance into the canonical QUBO representation."""

    @abstractmethod
    def decode_bitstring(
        self,
        bitstring: Bitstring,
        energy: float | None = None,
    ) -> DecodedSolution:
        """Map a raw bitstring back to a semantic solution."""
