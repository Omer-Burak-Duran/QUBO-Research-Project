"""Core dataclasses shared across modeling, solving, and analysis."""

from qubo_vqa.core.ising import IsingModel
from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import DecodedSolution, SolverResult, SolverTraceEntry

__all__ = ["DecodedSolution", "IsingModel", "QUBOModel", "SolverResult", "SolverTraceEntry"]
