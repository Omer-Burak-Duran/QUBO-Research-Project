"""Exact-statevector VQE implementation for the next quantum milestone."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter

import numpy as np
from scipy.optimize import minimize

from qubo_vqa.converters import qubo_to_ising
from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import SolverResult, SolverTraceEntry
from qubo_vqa.solvers.base import Decoder, Solver
from qubo_vqa.solvers.quantum.ansatz import build_vqe_ansatz, describe_vqe_ansatz
from qubo_vqa.solvers.quantum.backends import QuantumBackendConfig
from qubo_vqa.solvers.quantum.common import (
    VariationalEvaluation,
    evaluate_statevector_circuit,
    precompute_ising_basis_energies,
    top_basis_probabilities,
)


@dataclass(slots=True)
class VQEOptimizerConfig:
    """Optimization settings for the VQE outer loop."""

    method: str = "COBYLA"
    maxiter: int = 80
    tol: float | None = 1e-3
    options: dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation."""
        return {
            "method": self.method,
            "maxiter": self.maxiter,
            "tol": self.tol,
            "options": dict(self.options),
        }


@dataclass(slots=True)
class VQEInitializationConfig:
    """Configuration for deterministic VQE parameter initialization."""

    strategy: str = "small_random"
    seed: int | None = 0
    scale: float = 0.2

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation."""
        return {
            "strategy": self.strategy,
            "seed": self.seed,
            "scale": self.scale,
        }


def initialize_vqe_parameters(
    parameter_count: int,
    config: VQEInitializationConfig,
) -> np.ndarray:
    """Create the initial VQE parameter vector."""
    if config.strategy == "zeros":
        return np.zeros(parameter_count, dtype=float)

    rng = np.random.default_rng(config.seed)
    if config.strategy == "small_random":
        return rng.uniform(-config.scale, config.scale, size=parameter_count).astype(float)
    if config.strategy == "uniform":
        return rng.uniform(-np.pi, np.pi, size=parameter_count).astype(float)

    msg = f"Unsupported VQE initialization strategy '{config.strategy}'."
    raise ValueError(msg)


def evaluate_vqe_parameters(
    *,
    ising_model,
    parameters: np.ndarray,
    ansatz_name: str,
    ansatz_depth: int,
    basis_energies: np.ndarray,
    backend_config: QuantumBackendConfig,
) -> VariationalEvaluation:
    """Evaluate one VQE parameter vector exactly in the computational basis."""
    circuit = build_vqe_ansatz(
        ising_model=ising_model,
        family=ansatz_name,
        parameters=parameters,
        depth=ansatz_depth,
    )
    return evaluate_statevector_circuit(
        circuit=circuit,
        parameters=parameters,
        basis_energies=basis_energies,
        backend_config=backend_config,
    )


@dataclass(slots=True)
class VQESolver(Solver):
    """Exact-statevector VQE solver for small Ising/QUBO benchmark problems."""

    ansatz_name: str = "hardware_efficient"
    ansatz_depth: int = 1
    backend_config: QuantumBackendConfig = field(default_factory=QuantumBackendConfig)
    optimizer_config: VQEOptimizerConfig = field(default_factory=VQEOptimizerConfig)
    initialization_config: VQEInitializationConfig = field(default_factory=VQEInitializationConfig)
    max_variables: int = 12
    name: str = "vqe"
    metadata: dict[str, object] = field(default_factory=dict)

    def solve(self, qubo_model: QUBOModel, decoder: Decoder) -> SolverResult:
        """Optimize a VQE ansatz against the QUBO-derived Ising Hamiltonian."""
        if qubo_model.num_variables() > self.max_variables:
            msg = "Exact-statevector VQE is limited to small benchmark instances."
            raise ValueError(msg)

        ising_model = qubo_to_ising(qubo_model)
        ansatz_description = describe_vqe_ansatz(
            ising_model=ising_model,
            family=self.ansatz_name,
            depth=self.ansatz_depth,
        )
        basis_energies = precompute_ising_basis_energies(ising_model)
        initial_parameters = initialize_vqe_parameters(
            parameter_count=ansatz_description.parameter_count,
            config=self.initialization_config,
        )
        trace: list[SolverTraceEntry] = []
        best_evaluation: VariationalEvaluation | None = None

        started_at = perf_counter()

        def objective(parameters: np.ndarray) -> float:
            nonlocal best_evaluation
            evaluation = evaluate_vqe_parameters(
                ising_model=ising_model,
                parameters=parameters,
                ansatz_name=self.ansatz_name,
                ansatz_depth=self.ansatz_depth,
                basis_energies=basis_energies,
                backend_config=self.backend_config,
            )
            trace.append(
                SolverTraceEntry(
                    step=len(trace),
                    energy=evaluation.expectation_energy,
                    metadata={
                        "parameters": evaluation.parameters.tolist(),
                        "dominant_bitstring": list(evaluation.dominant_bitstring),
                        "dominant_probability": evaluation.dominant_probability,
                        "dominant_bitstring_energy": evaluation.dominant_bitstring_energy,
                    },
                )
            )
            if (
                best_evaluation is None
                or evaluation.expectation_energy < best_evaluation.expectation_energy
            ):
                best_evaluation = evaluation
            return evaluation.expectation_energy

        scipy_options = {"maxiter": self.optimizer_config.maxiter, **self.optimizer_config.options}
        optimization_result = minimize(
            objective,
            x0=initial_parameters,
            method=self.optimizer_config.method,
            tol=self.optimizer_config.tol,
            options=scipy_options,
        )

        final_evaluation = evaluate_vqe_parameters(
            ising_model=ising_model,
            parameters=np.asarray(optimization_result.x, dtype=float),
            ansatz_name=self.ansatz_name,
            ansatz_depth=self.ansatz_depth,
            basis_energies=basis_energies,
            backend_config=self.backend_config,
        )
        if (
            best_evaluation is None
            or final_evaluation.expectation_energy < best_evaluation.expectation_energy
        ):
            best_evaluation = final_evaluation

        runtime_seconds = perf_counter() - started_at
        best_bitstring = best_evaluation.dominant_bitstring
        best_bitstring_energy = qubo_model.energy(best_bitstring)
        decoded_solution = decoder(best_bitstring, best_bitstring_energy)

        return SolverResult(
            solver_name=self.name,
            best_bitstring=best_bitstring,
            best_energy=best_bitstring_energy,
            decoded_solution=decoded_solution,
            runtime_seconds=runtime_seconds,
            trace=trace,
            metadata={
                "backend": {"mode": self.backend_config.mode, "shots": self.backend_config.shots},
                "optimizer": self.optimizer_config.as_dict(),
                "initialization": self.initialization_config.as_dict(),
                "ansatz": ansatz_description.as_dict(),
                "initial_parameters": initial_parameters.tolist(),
                "final_parameters": np.asarray(optimization_result.x, dtype=float).tolist(),
                "best_expectation_energy": best_evaluation.expectation_energy,
                "final_expectation_energy": final_evaluation.expectation_energy,
                "best_dominant_probability": best_evaluation.dominant_probability,
                "top_basis_probabilities": top_basis_probabilities(
                    best_evaluation.probabilities,
                    basis_energies=basis_energies,
                ),
                "optimization_success": bool(optimization_result.success),
                "optimization_message": str(optimization_result.message),
                "evaluations": len(trace),
                "ising_model": ising_model.as_dict(),
                **self.metadata,
            },
        )
