"""Landscape-analysis utilities for low-dimensional variational scans."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qubo_vqa.core.ising import IsingModel
from qubo_vqa.solvers.quantum.backends import QuantumBackendConfig
from qubo_vqa.solvers.quantum.common import precompute_ising_basis_energies
from qubo_vqa.solvers.quantum.qaoa import evaluate_qaoa_parameters


@dataclass(slots=True)
class ParameterGrid:
    """One closed interval sampled at a fixed number of points."""

    minimum: float
    maximum: float
    points: int

    def values(self) -> np.ndarray:
        """Return the sampled grid values."""
        if self.points < 2:
            msg = "Parameter grids must contain at least two points."
            raise ValueError(msg)
        if self.maximum <= self.minimum:
            msg = "Parameter grid maximum must be greater than the minimum."
            raise ValueError(msg)
        return np.linspace(self.minimum, self.maximum, self.points, dtype=float)


def evaluate_qaoa_p1_landscape(
    *,
    ising_model: IsingModel,
    gamma_grid: ParameterGrid,
    beta_grid: ParameterGrid,
    backend_config: QuantumBackendConfig,
) -> list[dict[str, float | int | list[int]]]:
    """Evaluate a full QAOA p=1 parameter grid."""
    basis_energies = precompute_ising_basis_energies(ising_model)
    records: list[dict[str, float | int | list[int]]] = []

    for gamma in gamma_grid.values():
        for beta in beta_grid.values():
            evaluation = evaluate_qaoa_parameters(
                ising_model=ising_model,
                parameters=np.asarray([gamma, beta], dtype=float),
                reps=1,
                basis_energies=basis_energies,
                backend_config=backend_config,
            )
            records.append(
                {
                    "gamma": float(gamma),
                    "beta": float(beta),
                    "expectation_energy": float(evaluation.expectation_energy),
                    "dominant_probability": float(evaluation.dominant_probability),
                    "dominant_bitstring_energy": float(evaluation.dominant_bitstring_energy),
                    "dominant_bitstring": list(evaluation.dominant_bitstring),
                }
            )
    return records


def landscape_records_to_matrix(
    records: list[dict[str, float | int | list[int]]],
    *,
    row_key: str,
    column_key: str,
    value_key: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Convert flat landscape records into a dense matrix for plotting."""
    if not records:
        msg = "Landscape records must not be empty."
        raise ValueError(msg)

    row_values = np.asarray(
        sorted({float(record[row_key]) for record in records}),
        dtype=float,
    )
    column_values = np.asarray(
        sorted({float(record[column_key]) for record in records}),
        dtype=float,
    )
    matrix = np.zeros((row_values.size, column_values.size), dtype=float)
    row_lookup = {value: index for index, value in enumerate(row_values)}
    column_lookup = {value: index for index, value in enumerate(column_values)}

    for record in records:
        row_index = row_lookup[float(record[row_key])]
        column_index = column_lookup[float(record[column_key])]
        matrix[row_index, column_index] = float(record[value_key])

    return row_values, column_values, matrix


def summarize_landscape(
    records: list[dict[str, float | int | list[int]]],
) -> dict[str, float | int | list[int]]:
    """Summarize the best point in a low-dimensional landscape scan."""
    if not records:
        msg = "Landscape records must not be empty."
        raise ValueError(msg)

    best_record = min(records, key=lambda record: float(record["expectation_energy"]))
    return {
        "num_points": len(records),
        "best_gamma": float(best_record["gamma"]),
        "best_beta": float(best_record["beta"]),
        "best_expectation_energy": float(best_record["expectation_energy"]),
        "best_dominant_probability": float(best_record["dominant_probability"]),
        "best_dominant_bitstring_energy": float(best_record["dominant_bitstring_energy"]),
        "best_dominant_bitstring": list(best_record["dominant_bitstring"]),
    }
