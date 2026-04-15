"""Ising model representation used by the quantum layer."""

from __future__ import annotations

from dataclasses import dataclass, field

from qubo_vqa.core.types import Metadata


@dataclass(slots=True)
class IsingModel:
    """Sparse Ising model with local fields and pairwise couplings."""

    h: dict[int, float]
    j: dict[tuple[int, int], float]
    offset: float = 0.0
    variable_names: list[str] = field(default_factory=list)
    metadata: Metadata = field(default_factory=dict)

    def num_variables(self) -> int:
        """Return the number of spin variables."""
        if self.variable_names:
            return len(self.variable_names)
        return len(self.h)

    def energy(self, spins: tuple[int, ...]) -> float:
        """Evaluate the Ising energy for a spin assignment in {-1, +1}."""
        if len(spins) != self.num_variables():
            msg = "Spin assignment length does not match the Ising dimension."
            raise ValueError(msg)
        for spin in spins:
            if spin not in {-1, 1}:
                msg = "Ising spins must be either -1 or +1."
                raise ValueError(msg)

        field_energy = sum(self.h.get(index, 0.0) * spins[index] for index in range(len(spins)))
        coupling_energy = sum(value * spins[i] * spins[j] for (i, j), value in self.j.items())
        return self.offset + field_energy + coupling_energy

    def to_pauli_terms(self) -> list[tuple[str, float]]:
        """Return a simple Pauli-Z term representation without requiring Qiskit."""
        num_variables = self.num_variables()
        terms: list[tuple[str, float]] = [("I" * num_variables, self.offset)]

        for index, value in sorted(self.h.items()):
            label = ["I"] * num_variables
            label[index] = "Z"
            terms.append(("".join(label), value))

        for (left, right), value in sorted(self.j.items()):
            label = ["I"] * num_variables
            label[left] = "Z"
            label[right] = "Z"
            terms.append(("".join(label), value))

        return terms

    def as_dict(self) -> Metadata:
        """Convert the model to a JSON-friendly dictionary."""
        return {
            "h": {str(index): value for index, value in self.h.items()},
            "j": {f"{left},{right}": value for (left, right), value in self.j.items()},
            "offset": self.offset,
            "variable_names": list(self.variable_names),
            "metadata": dict(self.metadata),
        }
