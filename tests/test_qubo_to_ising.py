"""Tests for QUBO to Ising conversion."""

from __future__ import annotations

import itertools

from qubo_vqa.converters import qubo_to_ising


def test_qubo_to_ising_preserves_energy_ranking(cycle_maxcut_instance) -> None:
    """Converted Ising energies should match QUBO energies under bit-to-spin mapping."""
    qubo_model = cycle_maxcut_instance.to_qubo_model()
    ising_model = qubo_to_ising(qubo_model)

    qubo_energies: list[float] = []
    ising_energies: list[float] = []

    for bitstring in itertools.product((0, 1), repeat=qubo_model.num_variables()):
        spins = tuple(1 - 2 * bit for bit in bitstring)
        qubo_energies.append(qubo_model.energy(bitstring))
        ising_energies.append(ising_model.energy(spins))

    assert qubo_energies == ising_energies
