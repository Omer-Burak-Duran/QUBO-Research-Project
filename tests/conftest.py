"""Shared pytest fixtures for the repository."""

from __future__ import annotations

from pathlib import Path

import pytest

from qubo_vqa.problems.maxcut import MaxCutInstance
from qubo_vqa.problems.min_vertex_cover import MinimumVertexCoverInstance


@pytest.fixture()
def cycle_maxcut_instance() -> MaxCutInstance:
    """Return a small MaxCut instance with a known optimum."""
    return MaxCutInstance.cycle_graph(num_nodes=4, weight=1.0)


@pytest.fixture()
def path_mvc_instance() -> MinimumVertexCoverInstance:
    """Return a small Minimum Vertex Cover instance with a known optimum."""
    return MinimumVertexCoverInstance.path_graph(num_nodes=4, penalty_strength=2.0)


@pytest.fixture()
def sample_config_path() -> Path:
    """Return the path to the starter runnable example config."""
    return Path("configs/experiments/classical_maxcut.yaml")


@pytest.fixture()
def qaoa_config_path() -> Path:
    """Return the path to the starter QAOA example config."""
    return Path("configs/experiments/qaoa_maxcut_statevector.yaml")


@pytest.fixture()
def qaoa_initialization_comparison_config_path() -> Path:
    """Return the path to the QAOA initialization comparison config."""
    return Path("configs/experiments/qaoa_initialization_comparison.yaml")


@pytest.fixture()
def mvc_config_path() -> Path:
    """Return the path to the starter Minimum Vertex Cover config."""
    return Path("configs/experiments/classical_min_vertex_cover.yaml")
