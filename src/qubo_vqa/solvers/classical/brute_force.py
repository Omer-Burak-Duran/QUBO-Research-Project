"""Exact brute-force baseline for tiny QUBO models."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from time import perf_counter

from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import SolverResult, SolverTraceEntry
from qubo_vqa.solvers.base import Decoder, Solver


@dataclass(slots=True)
class BruteForceSolver(Solver):
    """Enumerate all bitstrings to recover the exact optimum."""

    max_variables: int = 20
    name: str = "brute_force"

    def solve(self, qubo_model: QUBOModel, decoder: Decoder) -> SolverResult:
        """Solve a small QUBO by exhaustive enumeration."""
        if qubo_model.num_variables() > self.max_variables:
            msg = "Brute-force solving is only intended for tiny benchmark instances."
            raise ValueError(msg)

        started_at = perf_counter()
        best_bitstring: tuple[int, ...] | None = None
        best_energy = float("inf")
        trace: list[SolverTraceEntry] = []

        for step, assignment in enumerate(product((0, 1), repeat=qubo_model.num_variables())):
            bitstring = tuple(int(bit) for bit in assignment)
            energy = qubo_model.energy(bitstring)
            trace.append(SolverTraceEntry(step=step, energy=energy))
            if energy < best_energy:
                best_energy = energy
                best_bitstring = bitstring

        if best_bitstring is None:
            msg = "Brute-force solver found no assignments."
            raise RuntimeError(msg)

        runtime_seconds = perf_counter() - started_at
        decoded_solution = decoder(best_bitstring, best_energy)
        return SolverResult(
            solver_name=self.name,
            best_bitstring=best_bitstring,
            best_energy=best_energy,
            decoded_solution=decoded_solution,
            runtime_seconds=runtime_seconds,
            trace=trace,
            metadata={"evaluations": len(trace)},
        )
