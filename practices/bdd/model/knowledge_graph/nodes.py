"""Knowledge-graph channel for the BDD model."""

from __future__ import annotations

import json
from pathlib import Path

from harness.knowledge_graph.model.knowledge_graph_node import KnowledgeGraphNode
from practices.bdd.model.nodes import Context, Description, Observation


class KnowledgeGraphDescription(Description, KnowledgeGraphNode):
    def __init__(self, source=None) -> None:
        if source is None:
            Description.__init__(self, "", 1)
            return
        Description.__init__(self, source.name, source.sequential_order)
        for context in getattr(source, "contexts", []):
            self.contexts.append(KnowledgeGraphContext(context))

    def save(self) -> str:
        return json.dumps(
            {
                "name": self.name,
                "contexts": [_context_record(item) for item in self.contexts],
            },
            indent=2,
        )

    def load(self, path) -> "KnowledgeGraphDescription":
        target = Path(path)
        if target.is_dir():
            target = target / "description.kg"
        if not target.is_file():
            return self
        return self.parse(target.read_text(encoding="utf-8"))

    def parse(self, text: str) -> "KnowledgeGraphDescription":
        data = json.loads(text) if text.strip() else {"name": "", "contexts": []}
        loaded = type(self)()
        loaded.name = data.get("name", "")
        for record in data.get("contexts", []):
            loaded.contexts.append(_context_from(record))
        return loaded

    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        return (canonical or self).save()


class KnowledgeGraphContext(Context, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Context.__init__(self, source.name, source.sequential_order)
        for observation in getattr(source, "observations", []):
            self.observations.append(KnowledgeGraphObservation(observation))
        for context in getattr(source, "contexts", []):
            self.contexts.append(KnowledgeGraphContext(context))


class KnowledgeGraphObservation(Observation, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Observation.__init__(self, source.name, source.sequential_order)


def _context_record(context) -> dict:
    return {
        "name": context.name,
        "observations": [item.name for item in context.observations],
        "contexts": [_context_record(item) for item in context.contexts],
    }


def _context_from(record: dict) -> KnowledgeGraphContext:
    context = KnowledgeGraphContext(Context(record.get("name", ""), 1))
    context.observations = [
        KnowledgeGraphObservation(Observation(name, index))
        for index, name in enumerate(record.get("observations", []), 1)
    ]
    context.contexts = [_context_from(item) for item in record.get("contexts", [])]
    return context
