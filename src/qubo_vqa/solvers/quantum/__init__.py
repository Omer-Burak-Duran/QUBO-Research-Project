"""Quantum solver scaffolding."""

from qubo_vqa.solvers.quantum.qaoa import QAOASolver
from qubo_vqa.solvers.quantum.vqe import VQESolver

__all__ = ["QAOASolver", "VQESolver"]
