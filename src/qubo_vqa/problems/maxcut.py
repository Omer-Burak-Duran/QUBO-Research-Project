"""MaxCut benchmark problem and QUBO encoder."""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import numpy as np

from qubo_vqa.core.qubo import QUBOModel
from qubo_vqa.core.result import DecodedSolution
from qubo_vqa.core.types import Bitstring
from qubo_vqa.problems.base import ProblemInstance


@dataclass(slots=True)
class MaxCutInstance(ProblemInstance):
    """Concrete MaxCut instance backed by a NetworkX graph."""

    graph: nx.Graph
    name: str = "maxcut"

    @classmethod
    def cycle_graph(cls, num_nodes: int, weight: float = 1.0) -> MaxCutInstance:
        """Create a simple weighted cycle graph for small examples and tests."""
        graph = nx.cycle_graph(num_nodes)
        nx.set_edge_attributes(graph, weight, "weight")
        return cls(graph=graph)

    @classmethod
    def erdos_renyi(
        cls,
        num_nodes: int,
        edge_probability: float,
        seed: int,
        weighted: bool = False,
    ) -> MaxCutInstance:
        """Create a random graph with optional integer edge weights."""
        graph = nx.erdos_renyi_graph(num_nodes, edge_probability, seed=seed)
        for left, right in graph.edges():
            graph[left][right]["weight"] = float((left + right) % 5 + 1) if weighted else 1.0
        return cls(graph=graph)

    def num_variables(self) -> int:
        """Return the number of graph vertices."""
        return self.graph.number_of_nodes()

    def to_qubo_model(self) -> QUBOModel:
        """Encode MaxCut as a minimization QUBO by negating the cut objective."""
        q_matrix = np.zeros((self.num_variables(), self.num_variables()), dtype=float)

        for left, right, data in self.graph.edges(data=True):
            weight = float(data.get("weight", 1.0))
            q_matrix[left, left] -= weight
            q_matrix[right, right] -= weight
            row, column = sorted((left, right))
            q_matrix[row, column] += 2.0 * weight

        return QUBOModel(
            q_matrix=q_matrix,
            offset=0.0,
            sense="min",
            variable_names=[f"node_{node}" for node in self.graph.nodes()],
            metadata={"problem": self.name, "num_edges": self.graph.number_of_edges()},
        )

    def cut_value(self, bitstring: Bitstring) -> float:
        """Compute the cut weight of a bitstring-defined partition."""
        return float(
            sum(
                data.get("weight", 1.0) * int(bitstring[left] != bitstring[right])
                for left, right, data in self.graph.edges(data=True)
            )
        )

    def decode_bitstring(
        self,
        bitstring: Bitstring,
        energy: float | None = None,
    ) -> DecodedSolution:
        """Decode a bitstring into a partition and associated objective metrics."""
        qubo_energy = self.to_qubo_model().energy(bitstring) if energy is None else energy
        left_partition = [node for node, value in enumerate(bitstring) if value == 0]
        right_partition = [node for node, value in enumerate(bitstring) if value == 1]
        cut_value = self.cut_value(bitstring)

        return DecodedSolution(
            bitstring=bitstring,
            is_feasible=True,
            objective_value=cut_value,
            penalty=0.0,
            total_energy=qubo_energy,
            interpretation={
                "left_partition": left_partition,
                "right_partition": right_partition,
            },
        )
