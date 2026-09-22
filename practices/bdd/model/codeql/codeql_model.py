"""BDD types on the practice graph — wrap live BDD types."""

from __future__ import annotations

from practices.bdd.model.nodes import (
    Context as SourceContext,
    Description as SourceDescription,
    Observation as SourceObservation,
)

from harness.knowledge_graph.model.graph_node import Node


class Observation(SourceObservation, Node):
    practice = "bdd"
    _semantic_type_name = "Observation"


class Context(SourceContext, Node):
    practice = "bdd"
    _semantic_type_name = "Context"

    def load_observation(self, source: SourceObservation) -> Observation:
        return Observation(source.name, source.sequential_order)

    def load_context(self, source: SourceContext) -> "Context":
        return Context(source.name, source.sequential_order)


class Description(SourceDescription, Node):
    practice = "bdd"
    _semantic_type_name = "Description"

    def load_context(self, source: SourceContext) -> Context:
        return Context(source.name, source.sequential_order)
