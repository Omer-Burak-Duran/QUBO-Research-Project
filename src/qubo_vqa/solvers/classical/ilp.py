"""ILP solver scaffold for later exact-baseline work."""

from __future__ import annotations

from dataclasses import dataclass

from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import SolverResult
from qubo_vqa.solvers.base import Decoder, Solver


@dataclass(slots=True)
class ILPSolver(Solver):
    """Placeholder interface for a later ILP-backed exact solver."""

    name: str = "ilp"

    def solve(self, qubo_model: QUBOModel, decoder: Decoder) -> SolverResult:
        """Solve the QUBO with an ILP backend in a later milestone."""
        msg = "The ILP baseline is planned for a later implementation pass."
        raise NotImplementedError(msg)
