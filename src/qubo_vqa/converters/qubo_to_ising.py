"""Conversion utilities between QUBO and Ising representations."""

from __future__ import annotations

from qubo_vqa.core.ising import IsingModel
from qubo_vqa.core.qubo import QUBOModel


def qubo_to_ising(qubo_model: QUBOModel) -> IsingModel:
    """Convert a minimization QUBO into an equivalent Ising model."""
    num_variables = qubo_model.num_variables()
    h = {index: 0.0 for index in range(num_variables)}
    j: dict[tuple[int, int], float] = {}
    offset = qubo_model.offset

    for index in range(num_variables):
        linear_coefficient = float(qubo_model.q_matrix[index, index])
        offset += linear_coefficient / 2.0
        h[index] -= linear_coefficient / 2.0

    for left in range(num_variables):
        for right in range(left + 1, num_variables):
            quadratic_coefficient = float(qubo_model.q_matrix[left, right])
            if quadratic_coefficient == 0.0:
                continue
            offset += quadratic_coefficient / 4.0
            h[left] -= quadratic_coefficient / 4.0
            h[right] -= quadratic_coefficient / 4.0
            j[(left, right)] = quadratic_coefficient / 4.0

    return IsingModel(
        h=h,
        j=j,
        offset=offset,
        variable_names=list(qubo_model.variable_names),
        metadata={"source": "qubo_to_ising", **qubo_model.metadata},
    )
