"""Tests for core QUBO behavior."""

from __future__ import annotations

import numpy as np

from qubo_vqa.core.qubo import QUBOModel


def test_qubo_energy_matches_manual_evaluation() -> None:
    """The QUBO model should evaluate linear and pairwise terms correctly."""
    model = QUBOModel(
        q_matrix=np.array(
            [
                [1.0, -2.0],
                [0.0, 3.0],
            ]
        ),
        offset=0.5,
    )

    assert model.energy((0, 0)) == 0.5
    assert model.energy((1, 0)) == 1.5
    assert model.energy((0, 1)) == 3.5
    assert model.energy((1, 1)) == 2.5
