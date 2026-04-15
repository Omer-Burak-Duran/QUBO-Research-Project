"""Exact-statevector QAOA implementation for small benchmark problems."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter

import numpy as np
from scipy.optimize import minimize

from qubo_vqa.converters import qubo_to_ising
from qubo_vqa.core.ising import IsingModel
from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import SolverResult, SolverTraceEntry
from qubo_vqa.solvers.base import Decoder, Solver
from qubo_vqa.solvers.quantum.backends import QuantumBackendConfig, build_backend
from qubo_vqa.solvers.quantum.initialization import (
    QAOAInitializationConfig,
    initialize_qaoa_parameters,
)
from qubo_vqa.solvers.quantum.mixers import apply_standard_x_mixer


@dataclass(slots=True)
class QAOAOptimizerConfig:
    """Optimization settings for the QAOA outer loop."""

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
class QAOAEvaluation:
    """One evaluated parameter setting and its exact basis distribution."""

    parameters: np.ndarray
    expectation_energy: float
    dominant_bitstring: tuple[int, ...]
    dominant_probability: float
    dominant_bitstring_energy: float
    probabilities: np.ndarray


def index_to_bitstring(index: int, num_variables: int) -> tuple[int, ...]:
    """Convert a basis-state index to a bitstring ordered by qubit index."""
    return tuple((index >> qubit) & 1 for qubit in range(num_variables))


def bitstring_to_spins(bitstring: tuple[int, ...]) -> tuple[int, ...]:
    """Map a binary bitstring to Ising spins with 0 -> +1 and 1 -> -1."""
    return tuple(1 - 2 * bit for bit in bitstring)


def split_qaoa_parameters(parameters: np.ndarray, reps: int) -> tuple[np.ndarray, np.ndarray]:
    """Split a flat parameter vector into gamma and beta blocks."""
    parameter_vector = np.asarray(parameters, dtype=float)
    if parameter_vector.shape != (2 * reps,):
        msg = "QAOA parameters must have shape (2 * reps,)."
        raise ValueError(msg)
    return parameter_vector[:reps], parameter_vector[reps:]


def precompute_ising_basis_energies(ising_model: IsingModel) -> np.ndarray:
    """Precompute the Ising energy of every computational basis state."""
    num_variables = ising_model.num_variables()
    return np.asarray(
        [
            ising_model.energy(bitstring_to_spins(index_to_bitstring(index, num_variables)))
            for index in range(2**num_variables)
        ],
        dtype=float,
    )


def build_qaoa_circuit(ising_model: IsingModel, parameters: np.ndarray, reps: int):
    """Construct the standard QAOA circuit for a diagonal Ising Hamiltonian."""
    try:
        from qiskit import QuantumCircuit
    except ImportError as error:
        msg = "Qiskit is required to build QAOA circuits."
        raise ImportError(msg) from error

    gammas, betas = split_qaoa_parameters(parameters, reps)
    circuit = QuantumCircuit(ising_model.num_variables())
    circuit.h(range(ising_model.num_variables()))

    for layer in range(reps):
        gamma = float(gammas[layer])
        beta = float(betas[layer])

        for index, value in sorted(ising_model.h.items()):
            if value != 0.0:
                circuit.rz(2.0 * gamma * value, index)

        for (left, right), value in sorted(ising_model.j.items()):
            if value != 0.0:
                circuit.rzz(2.0 * gamma * value, left, right)

        apply_standard_x_mixer(circuit, beta)

    return circuit


def top_basis_probabilities(
    probabilities: np.ndarray,
    basis_energies: np.ndarray,
    limit: int = 5,
) -> list[dict[str, object]]:
    """Summarize the most probable basis states for logging."""
    num_variables = int(np.log2(len(probabilities)))
    ranked_indices = np.argsort(probabilities)[::-1][:limit]
    return [
        {
            "bitstring": list(index_to_bitstring(int(index), num_variables)),
            "probability": float(probabilities[index]),
            "energy": float(basis_energies[index]),
        }
        for index in ranked_indices
    ]


def evaluate_qaoa_parameters(
    ising_model: IsingModel,
    parameters: np.ndarray,
    reps: int,
    basis_energies: np.ndarray,
    backend_config: QuantumBackendConfig,
) -> QAOAEvaluation:
    """Evaluate one QAOA parameter vector exactly in the computational basis."""
    backend = build_backend(backend_config)
    circuit = build_qaoa_circuit(ising_model, parameters, reps)
    probabilities = backend.bitstring_probabilities(circuit)
    expectation_energy = float(np.dot(probabilities, basis_energies))
    dominant_index = int(np.argmax(probabilities))
    dominant_bitstring = index_to_bitstring(dominant_index, ising_model.num_variables())

    return QAOAEvaluation(
        parameters=np.asarray(parameters, dtype=float),
        expectation_energy=expectation_energy,
        dominant_bitstring=dominant_bitstring,
        dominant_probability=float(probabilities[dominant_index]),
        dominant_bitstring_energy=float(basis_energies[dominant_index]),
        probabilities=probabilities,
    )


@dataclass(slots=True)
class QAOASolver(Solver):
    """Exact-statevector QAOA solver for small Ising/QUBO problems."""

    reps: int = 1
    backend_config: QuantumBackendConfig = field(default_factory=QuantumBackendConfig)
    optimizer_config: QAOAOptimizerConfig = field(default_factory=QAOAOptimizerConfig)
    initialization_config: QAOAInitializationConfig = field(
        default_factory=QAOAInitializationConfig
    )
    previous_parameters: np.ndarray | None = None
    max_variables: int = 12
    name: str = "qaoa"
    metadata: dict[str, object] = field(default_factory=dict)

    def solve(self, qubo_model: QUBOModel, decoder: Decoder) -> SolverResult:
        """Optimize a standard QAOA ansatz against the QUBO-derived Ising Hamiltonian."""
        if qubo_model.num_variables() > self.max_variables:
            msg = "Exact-statevector QAOA is limited to small benchmark instances."
            raise ValueError(msg)

        ising_model = qubo_to_ising(qubo_model)
        basis_energies = precompute_ising_basis_energies(ising_model)
        initial_parameters = initialize_qaoa_parameters(
            reps=self.reps,
            config=self.initialization_config,
            previous_parameters=self.previous_parameters,
        )
        trace: list[SolverTraceEntry] = []
        best_evaluation: QAOAEvaluation | None = None

        started_at = perf_counter()

        def objective(parameters: np.ndarray) -> float:
            nonlocal best_evaluation
            evaluation = evaluate_qaoa_parameters(
                ising_model=ising_model,
                parameters=parameters,
                reps=self.reps,
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

        final_evaluation = evaluate_qaoa_parameters(
            ising_model=ising_model,
            parameters=np.asarray(optimization_result.x, dtype=float),
            reps=self.reps,
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
                "reps": self.reps,
                "initial_parameters": initial_parameters.tolist(),
                "final_parameters": np.asarray(optimization_result.x, dtype=float).tolist(),
                "previous_parameters": (
                    np.asarray(self.previous_parameters, dtype=float).tolist()
                    if self.previous_parameters is not None
                    else None
                ),
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
