"""Mixer utilities for QAOA circuits."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qiskit import QuantumCircuit


def standard_x_mixer_description() -> str:
    """Return the default mixer description used by the planned QAOA solver."""
    return "transverse_field_x_mixer"


def apply_standard_x_mixer(circuit: QuantumCircuit, beta: float) -> None:
    """Apply the standard transverse-field X mixer to all qubits."""
    for qubit in range(circuit.num_qubits):
        circuit.rx(2.0 * beta, qubit)
