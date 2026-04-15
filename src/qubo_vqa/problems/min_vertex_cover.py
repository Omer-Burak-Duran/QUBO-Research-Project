"""Minimum Vertex Cover benchmark problem and QUBO encoder."""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import numpy as np

from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import DecodedSolution
from qubo_vqa.core.types import Bitstring
from qubo_vqa.problems.base import ProblemInstance


@dataclass(slots=True)
class MinimumVertexCoverInstance(ProblemInstance):
    """Penalty-based Minimum Vertex Cover benchmark instance."""

    graph: nx.Graph
    penalty_strength: float = 2.0
    name: str = "minimum_vertex_cover"

    @classmethod
    def path_graph(
        cls,
        num_nodes: int,
        penalty_strength: float = 2.0,
    ) -> MinimumVertexCoverInstance:
        """Create a path-graph benchmark instance."""
        return cls(
            graph=nx.path_graph(num_nodes),
            penalty_strength=penalty_strength,
        )

    @classmethod
    def cycle_graph(
        cls,
        num_nodes: int,
        penalty_strength: float = 2.0,
    ) -> MinimumVertexCoverInstance:
        """Create a cycle-graph benchmark instance."""
        return cls(
            graph=nx.cycle_graph(num_nodes),
            penalty_strength=penalty_strength,
        )

    @classmethod
    def erdos_renyi(
        cls,
        num_nodes: int,
        edge_probability: float,
        seed: int,
        penalty_strength: float = 2.0,
    ) -> MinimumVertexCoverInstance:
        """Create a random graph benchmark instance."""
        return cls(
            graph=nx.erdos_renyi_graph(num_nodes, edge_probability, seed=seed),
            penalty_strength=penalty_strength,
        )

    def num_variables(self) -> int:
        """Return the number of encoded vertices."""
        return self.graph.number_of_nodes()

    def to_qubo_model(self) -> QUBOModel:
        """Encode Minimum Vertex Cover with one penalty term per uncovered edge."""
        q_matrix = np.zeros((self.num_variables(), self.num_variables()), dtype=float)

        for node in self.graph.nodes():
            q_matrix[node, node] += 1.0

        offset = 0.0
        for left, right in self.graph.edges():
            offset += self.penalty_strength
            q_matrix[left, left] -= self.penalty_strength
            q_matrix[right, right] -= self.penalty_strength
            row, column = sorted((left, right))
            q_matrix[row, column] += self.penalty_strength

        return QUBOModel(
            q_matrix=q_matrix,
            offset=offset,
            sense="min",
            variable_names=[f"node_{node}" for node in self.graph.nodes()],
            metadata={
                "problem": self.name,
                "num_edges": self.graph.number_of_edges(),
                "penalty_strength": self.penalty_strength,
            },
        )

    def selected_vertices(self, bitstring: Bitstring) -> list[int]:
        """Return the selected vertices for a candidate cover bitstring."""
        return [node for node, value in enumerate(bitstring) if value == 1]

    def uncovered_edges(self, bitstring: Bitstring) -> list[tuple[int, int]]:
        """Return edges left uncovered by the candidate bitstring."""
        return [
            (left, right)
            for left, right in self.graph.edges()
            if bitstring[left] == 0 and bitstring[right] == 0
        ]

    def decode_bitstring(
        self,
        bitstring: Bitstring,
        energy: float | None = None,
    ) -> DecodedSolution:
        """Decode a bitstring into a vertex set with feasibility diagnostics."""
        qubo_energy = self.to_qubo_model().energy(bitstring) if energy is None else energy
        selected_vertices = self.selected_vertices(bitstring)
        uncovered_edges = self.uncovered_edges(bitstring)
        penalty = float(self.penalty_strength * len(uncovered_edges))

        return DecodedSolution(
            bitstring=bitstring,
            is_feasible=not uncovered_edges,
            objective_value=float(len(selected_vertices)),
            penalty=penalty,
            total_energy=qubo_energy,
            interpretation={
                "selected_vertices": selected_vertices,
                "uncovered_edges": [list(edge) for edge in uncovered_edges],
                "cover_size": len(selected_vertices),
                "uncovered_edge_count": len(uncovered_edges),
            },
        )
