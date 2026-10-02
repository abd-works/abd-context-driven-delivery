"""Knowledge-graph channel for the BDD model."""

from __future__ import annotations

from harness.knowledge_graph.model.knowledge_graph_node import KnowledgeGraphNode
from practices.bdd.model.nodes import Context, Description, Observation


class KnowledgeGraphDescription(Description, KnowledgeGraphNode):
    def __init__(self, source=None) -> None:
        if source is None:
            Description.__init__(self, "", 1)
        else:
            Description.__init__(self, source.name, source.sequential_order)

    def save(self) -> str:
        return ""

    def load(self, path) -> "KnowledgeGraphDescription":
        return self

    def parse(self, text: str) -> "KnowledgeGraphDescription":
        return self

    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        return (canonical or self).save()


class KnowledgeGraphContext(Context, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Context.__init__(self, source.name, source.sequential_order)


class KnowledgeGraphObservation(Observation, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Observation.__init__(self, source.name, source.sequential_order)
