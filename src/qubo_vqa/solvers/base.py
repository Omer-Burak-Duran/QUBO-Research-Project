"""Shared solver interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import DecodedSolution, SolverResult
from qubo_vqa.core.types import Bitstring

Decoder = Callable[[Bitstring, float | None], DecodedSolution]


class Solver(ABC):
    """Abstract solver interface shared by classical and quantum modules."""

    name: str

    @abstractmethod
    def solve(self, qubo_model: QUBOModel, decoder: Decoder) -> SolverResult:
        """Solve a QUBO model and return a standardized result."""
