"""Standardized result containers for solver outputs and decoded solutions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from qubo_vqa.core.types import Bitstring, Metadata


@dataclass(slots=True)
class DecodedSolution:
    """Semantic interpretation of a solver bitstring."""

    bitstring: Bitstring
    is_feasible: bool
    objective_value: float
    penalty: float
    total_energy: float
    interpretation: Metadata = field(default_factory=dict)

    def as_dict(self) -> Metadata:
        """Return a JSON-friendly dictionary representation."""
        payload = asdict(self)
        payload["bitstring"] = list(self.bitstring)
        return payload


@dataclass(slots=True)
class SolverTraceEntry:
    """Single iteration or evaluation entry recorded by a solver."""

    step: int
    energy: float
    metadata: Metadata = field(default_factory=dict)


@dataclass(slots=True)
class SolverResult:
    """Standard result object returned by all solver implementations."""

    solver_name: str
    best_bitstring: Bitstring
    best_energy: float
    decoded_solution: DecodedSolution
    runtime_seconds: float
    trace: list[SolverTraceEntry] = field(default_factory=list)
    metadata: Metadata = field(default_factory=dict)

    def trace_as_dicts(self) -> list[Metadata]:
        """Return the solver trace in a JSON-friendly format."""
        return [asdict(entry) for entry in self.trace]

    def as_dict(self) -> Metadata:
        """Return a JSON-friendly dictionary representation."""
        payload = asdict(self)
        payload["best_bitstring"] = list(self.best_bitstring)
        payload["decoded_solution"] = self.decoded_solution.as_dict()
        return payload
