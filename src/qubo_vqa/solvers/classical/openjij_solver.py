"""OpenJij-based classical sampling baselines for QUBO models."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

import numpy as np

from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import SolverResult, SolverTraceEntry
from qubo_vqa.solvers.base import Decoder, Solver


def _qubo_to_openjij_dict(qubo_model: QUBOModel) -> dict[tuple[int, int], float]:
    """Convert the canonical upper-triangular QUBO matrix into OpenJij's mapping form."""
    num_variables = qubo_model.num_variables()
    qubo: dict[tuple[int, int], float] = {}
    for row in range(num_variables):
        diagonal = float(qubo_model.q_matrix[row, row])
        if diagonal != 0.0:
            qubo[(row, row)] = diagonal
        for column in range(row + 1, num_variables):
            coefficient = float(qubo_model.q_matrix[row, column])
            if coefficient != 0.0:
                qubo[(row, column)] = coefficient
    return qubo


def _json_safe_info(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert OpenJij metadata into JSON-friendly Python scalars."""
    normalized: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, dict):
            normalized[key] = _json_safe_info(value)
        elif isinstance(value, list):
            normalized[key] = [
                item.item() if isinstance(item, np.generic) else item for item in value
            ]
        elif isinstance(value, np.ndarray):
            normalized[key] = value.tolist()
        elif isinstance(value, np.generic):
            normalized[key] = value.item()
        else:
            normalized[key] = value
    return normalized


@dataclass(slots=True)
class OpenJijSolver(Solver):
    """Sample a QUBO model with an OpenJij annealing-based sampler."""

    sampler: str = "sa"
    num_reads: int = 64
    num_sweeps: int = 1000
    seed: int | None = None
    beta_min: float | None = None
    beta_max: float | None = None
    max_variables: int = 128
    name: str = "openjij"
    metadata: dict[str, object] = field(default_factory=dict)

    def _build_sampler(self):
        """Construct the requested OpenJij sampler."""
        try:
            import openjij as oj
        except ImportError as error:
            msg = "OpenJij is required for the OpenJij baseline solver."
            raise ImportError(msg) from error

        if self.sampler == "sa":
            return oj.SASampler()
        if self.sampler == "sqa":
            return oj.SQASampler()

        msg = f"Unsupported OpenJij sampler '{self.sampler}'."
        raise ValueError(msg)

    def solve(self, qubo_model: QUBOModel, decoder: Decoder) -> SolverResult:
        """Sample a small-to-medium QUBO with OpenJij and return the best observed bitstring."""
        if qubo_model.num_variables() > self.max_variables:
            msg = "OpenJij solving is limited to moderate benchmark instances in this project."
            raise ValueError(msg)
        if self.num_reads <= 0:
            msg = "OpenJij solving requires num_reads to be positive."
            raise ValueError(msg)
        if self.num_sweeps <= 0:
            msg = "OpenJij solving requires num_sweeps to be positive."
            raise ValueError(msg)

        started_at = perf_counter()
        sampler = self._build_sampler()
        sampler_parameters: dict[str, object] = {
            "num_reads": self.num_reads,
            "num_sweeps": self.num_sweeps,
            "seed": self.seed,
        }
        if self.beta_min is not None:
            sampler_parameters["beta_min"] = self.beta_min
        if self.beta_max is not None:
            sampler_parameters["beta_max"] = self.beta_max
        sample_set = sampler.sample_qubo(
            _qubo_to_openjij_dict(qubo_model),
            **sampler_parameters,
        )
        runtime_seconds = perf_counter() - started_at

        trace: list[SolverTraceEntry] = []
        best_bitstring: tuple[int, ...] | None = None
        best_energy = float("inf")
        sampled_records: list[dict[str, object]] = []
        for step, sample in enumerate(sample_set.record.sample):
            bitstring = tuple(int(bit) for bit in sample.tolist())
            energy = qubo_model.energy(bitstring)
            occurrences = int(sample_set.record.num_occurrences[step])
            trace.append(
                SolverTraceEntry(
                    step=step,
                    energy=energy,
                    metadata={
                        "bitstring": list(bitstring),
                        "num_occurrences": occurrences,
                    },
                )
            )
            sampled_records.append(
                {
                    "bitstring": list(bitstring),
                    "energy": energy,
                    "num_occurrences": occurrences,
                }
            )
            if energy < best_energy:
                best_energy = energy
                best_bitstring = bitstring

        if best_bitstring is None:
            msg = "OpenJij solver returned no samples."
            raise RuntimeError(msg)

        decoded_solution = decoder(best_bitstring, best_energy)
        return SolverResult(
            solver_name=self.name,
            best_bitstring=best_bitstring,
            best_energy=best_energy,
            decoded_solution=decoded_solution,
            runtime_seconds=runtime_seconds,
            trace=trace,
            metadata={
                "sampler": self.sampler,
                "num_reads": self.num_reads,
                "num_sweeps": self.num_sweeps,
                "seed": self.seed,
                "beta_min": self.beta_min,
                "beta_max": self.beta_max,
                "evaluations": len(trace),
                "sampling_success": True,
                "openjij_info": _json_safe_info(sample_set.info),
                "sampled_records": sampled_records[: min(10, len(sampled_records))],
                **self.metadata,
            },
        )
