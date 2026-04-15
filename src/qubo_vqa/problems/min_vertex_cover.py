"""Minimum Vertex Cover scaffold for a later milestone."""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx

from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import DecodedSolution
from qubo_vqa.core.types import Bitstring
from qubo_vqa.problems.base import ProblemInstance


@dataclass(slots=True)
class MinimumVertexCoverInstance(ProblemInstance):
    """Starter interface for the penalty-based Minimum Vertex Cover benchmark."""

    graph: nx.Graph
    penalty_strength: float = 2.0
    name: str = "minimum_vertex_cover"

    def num_variables(self) -> int:
        """Return the number of encoded vertices."""
        return self.graph.number_of_nodes()

    def to_qubo_model(self) -> QUBOModel:
        """Encode the instance to QUBO in a later milestone."""
        msg = "Minimum Vertex Cover is planned for a later implementation pass."
        raise NotImplementedError(msg)

    def decode_bitstring(
        self,
        bitstring: Bitstring,
        energy: float | None = None,
    ) -> DecodedSolution:
        """Decode a bitstring in a later milestone."""
        msg = "Minimum Vertex Cover decoding is planned for a later implementation pass."
        raise NotImplementedError(msg)
