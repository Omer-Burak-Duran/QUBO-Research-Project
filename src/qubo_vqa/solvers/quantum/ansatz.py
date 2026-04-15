"""VQE ansatz builders for the exact-statevector milestone."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from qubo_vqa.core.ising import IsingModel

SUPPORTED_VQE_ANSATZ_FAMILIES = ("hardware_efficient", "problem_aware")


@dataclass(slots=True)
class VQEAnsatzDescription:
    """Static metadata describing one VQE ansatz family and depth."""

    family: str
    depth: int
    parameter_count: int
    metadata: dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-friendly representation."""
        return {
            "family": self.family,
            "depth": self.depth,
            "parameter_count": self.parameter_count,
            "metadata": dict(self.metadata),
        }


def _validate_depth(depth: int) -> None:
    """Ensure the requested ansatz depth is valid."""
    if depth < 1:
        msg = "VQE ansatz depth must be at least 1."
        raise ValueError(msg)


def _nonzero_field_indices(ising_model: IsingModel) -> list[int]:
    """Return field indices that meaningfully contribute to the Hamiltonian."""
    return [index for index, value in sorted(ising_model.h.items()) if value != 0.0]


def _nonzero_couplings(ising_model: IsingModel) -> list[tuple[int, int]]:
    """Return coupling pairs that meaningfully contribute to the Hamiltonian."""
    return [
        (left, right)
        for (left, right), value in sorted(ising_model.j.items())
        if value != 0.0
    ]


def describe_vqe_ansatz(
    ising_model: IsingModel,
    family: str,
    depth: int,
) -> VQEAnsatzDescription:
    """Describe the parameterization used by one supported VQE ansatz."""
    _validate_depth(depth)
    num_qubits = ising_model.num_variables()

    if family == "hardware_efficient":
        return VQEAnsatzDescription(
            family=family,
            depth=depth,
            parameter_count=2 * num_qubits * depth,
            metadata={
                "rotation_blocks": ["ry", "rz"],
                "entanglement": "ring_cx",
                "parameters_per_layer": 2 * num_qubits,
            },
        )

    if family == "problem_aware":
        field_indices = _nonzero_field_indices(ising_model)
        coupling_pairs = _nonzero_couplings(ising_model)
        parameters_per_layer = num_qubits + int(bool(field_indices)) + int(bool(coupling_pairs))
        return VQEAnsatzDescription(
            family=family,
            depth=depth,
            parameter_count=parameters_per_layer * depth,
            metadata={
                "field_terms": len(field_indices),
                "coupling_terms": len(coupling_pairs),
                "includes_field_block": bool(field_indices),
                "includes_coupling_block": bool(coupling_pairs),
                "mixer": "per_qubit_rx",
                "parameters_per_layer": parameters_per_layer,
            },
        )

    msg = f"Unsupported VQE ansatz family '{family}'."
    raise ValueError(msg)


def _validate_parameter_count(
    parameters: np.ndarray,
    description: VQEAnsatzDescription,
) -> np.ndarray:
    """Normalize and validate an ansatz parameter vector."""
    parameter_vector = np.asarray(parameters, dtype=float)
    if parameter_vector.shape != (description.parameter_count,):
        msg = (
            f"Expected {description.parameter_count} parameters for the "
            f"{description.family} ansatz, received {parameter_vector.shape}."
        )
        raise ValueError(msg)
    return parameter_vector


def _apply_ring_entanglement(circuit, num_qubits: int) -> None:
    """Apply a simple ring entanglement pattern."""
    if num_qubits < 2:
        return
    for qubit in range(num_qubits - 1):
        circuit.cx(qubit, qubit + 1)
    if num_qubits > 2:
        circuit.cx(num_qubits - 1, 0)


def _build_hardware_efficient_ansatz(
    parameter_vector: np.ndarray,
    num_qubits: int,
    depth: int,
):
    """Build a lightweight hardware-efficient ansatz."""
    try:
        from qiskit import QuantumCircuit
    except ImportError as error:
        msg = "Qiskit is required to build VQE ansatz circuits."
        raise ImportError(msg) from error

    circuit = QuantumCircuit(num_qubits)
    cursor = 0
    for _ in range(depth):
        layer_parameters = parameter_vector[cursor : cursor + (2 * num_qubits)]
        cursor += 2 * num_qubits
        ry_angles = layer_parameters[:num_qubits]
        rz_angles = layer_parameters[num_qubits:]

        for qubit, angle in enumerate(ry_angles):
            circuit.ry(float(angle), qubit)
        for qubit, angle in enumerate(rz_angles):
            circuit.rz(float(angle), qubit)

        _apply_ring_entanglement(circuit, num_qubits)

    return circuit


def _build_problem_aware_ansatz(
    parameter_vector: np.ndarray,
    ising_model: IsingModel,
    depth: int,
):
    """Build a structured ansatz that reuses the Ising Hamiltonian geometry."""
    try:
        from qiskit import QuantumCircuit
    except ImportError as error:
        msg = "Qiskit is required to build VQE ansatz circuits."
        raise ImportError(msg) from error

    num_qubits = ising_model.num_variables()
    field_indices = _nonzero_field_indices(ising_model)
    coupling_pairs = _nonzero_couplings(ising_model)
    circuit = QuantumCircuit(num_qubits)
    circuit.h(range(num_qubits))

    cursor = 0
    for _ in range(depth):
        if field_indices:
            field_scale = float(parameter_vector[cursor])
            cursor += 1
            for index in field_indices:
                circuit.rz(2.0 * field_scale * float(ising_model.h[index]), index)

        if coupling_pairs:
            coupling_scale = float(parameter_vector[cursor])
            cursor += 1
            for left, right in coupling_pairs:
                circuit.rzz(2.0 * coupling_scale * float(ising_model.j[(left, right)]), left, right)

        mixer_angles = parameter_vector[cursor : cursor + num_qubits]
        cursor += num_qubits
        for qubit, angle in enumerate(mixer_angles):
            circuit.rx(2.0 * float(angle), qubit)

    return circuit


def build_vqe_ansatz(
    ising_model: IsingModel,
    family: str,
    parameters: np.ndarray,
    depth: int,
):
    """Build one supported VQE ansatz circuit."""
    description = describe_vqe_ansatz(ising_model=ising_model, family=family, depth=depth)
    parameter_vector = _validate_parameter_count(parameters, description)

    if family == "hardware_efficient":
        return _build_hardware_efficient_ansatz(
            parameter_vector,
            ising_model.num_variables(),
            depth,
        )
    if family == "problem_aware":
        return _build_problem_aware_ansatz(parameter_vector, ising_model, depth)

    msg = f"Unsupported VQE ansatz family '{family}'."
    raise ValueError(msg)
