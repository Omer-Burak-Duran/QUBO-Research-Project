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
def cycle_mvc_instance() -> MinimumVertexCoverInstance:
    """Return a small cycle Minimum Vertex Cover instance with a known optimum."""
    return MinimumVertexCoverInstance.cycle_graph(num_nodes=4, penalty_strength=2.0)


@pytest.fixture()
def sample_config_path() -> Path:
    """Return the path to the starter runnable example config."""
    return Path("configs/experiments/classical_maxcut.yaml")


@pytest.fixture()
def qaoa_config_path() -> Path:
    """Return the path to the starter QAOA example config."""
    return Path("configs/experiments/qaoa_maxcut_statevector.yaml")


@pytest.fixture()
def vqe_config_path() -> Path:
    """Return the path to the starter VQE example config."""
    return Path("configs/experiments/vqe_maxcut_statevector.yaml")


@pytest.fixture()
def qaoa_shot_based_config_path() -> Path:
    """Return the path to the shot-based QAOA example config."""
    return Path("configs/experiments/qaoa_maxcut_shot_based.yaml")


@pytest.fixture()
def vqe_shot_based_config_path() -> Path:
    """Return the path to the shot-based VQE example config."""
    return Path("configs/experiments/vqe_maxcut_shot_based.yaml")


@pytest.fixture()
def qaoa_noisy_config_path() -> Path:
    """Return the path to the noisy QAOA example config."""
    return Path("configs/experiments/qaoa_maxcut_noisy.yaml")


@pytest.fixture()
def vqe_noisy_config_path() -> Path:
    """Return the path to the noisy VQE example config."""
    return Path("configs/experiments/vqe_maxcut_noisy.yaml")


@pytest.fixture()
def backend_comparison_config_path() -> Path:
    """Return the path to the backend comparison config."""
    return Path("configs/experiments/qaoa_backend_comparison.yaml")


@pytest.fixture()
def qaoa_mvc_config_path() -> Path:
    """Return the path to the starter QAOA MVC example config."""
    return Path("configs/experiments/qaoa_min_vertex_cover_statevector.yaml")


@pytest.fixture()
def vqe_mvc_config_path() -> Path:
    """Return the path to the starter VQE MVC example config."""
    return Path("configs/experiments/vqe_min_vertex_cover_statevector.yaml")


@pytest.fixture()
def qaoa_initialization_comparison_config_path() -> Path:
    """Return the path to the QAOA initialization comparison config."""
    return Path("configs/experiments/qaoa_initialization_comparison.yaml")


@pytest.fixture()
def qaoa_landscape_analysis_config_path() -> Path:
    """Return the path to the landscape-analysis config."""
    return Path("configs/experiments/qaoa_landscape_analysis.yaml")


@pytest.fixture()
def openjij_maxcut_config_path() -> Path:
    """Return the path to the OpenJij MaxCut example config."""
    return Path("configs/experiments/openjij_maxcut.yaml")


@pytest.fixture()
def openjij_mvc_config_path() -> Path:
    """Return the path to the OpenJij MVC example config."""
    return Path("configs/experiments/openjij_min_vertex_cover.yaml")


@pytest.fixture()
def solver_comparison_config_path() -> Path:
    """Return the path to the cross-solver comparison config."""
    return Path("configs/experiments/maxcut_solver_comparison.yaml")


@pytest.fixture()
def mvc_config_path() -> Path:
    """Return the path to the starter Minimum Vertex Cover config."""
    return Path("configs/experiments/classical_min_vertex_cover.yaml")
