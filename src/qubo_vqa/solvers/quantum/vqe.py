"""VQE solver scaffold for a later milestone."""

from __future__ import annotations

from dataclasses import dataclass, field

from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import SolverResult
from qubo_vqa.solvers.base import Decoder, Solver


@dataclass(slots=True)
class VQESolver(Solver):
    """Starter VQE interface reserved for the quantum milestone."""

    ansatz_name: str = "hardware_efficient"
    backend_mode: str = "statevector"
    optimizer_name: str = "COBYLA"
    name: str = "vqe"
    metadata: dict[str, object] = field(default_factory=dict)

    def solve(self, qubo_model: QUBOModel, decoder: Decoder) -> SolverResult:
        """Run VQE in a later milestone."""
        msg = "VQE is scaffolded now and will be implemented after the classical vertical slice."
        raise NotImplementedError(msg)
