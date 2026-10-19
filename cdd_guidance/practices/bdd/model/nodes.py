"""BDD node types — specialise the Stories StoryNode base."""

from __future__ import annotations

from typing import List

from harness.graph.bound_node import BoundChildren

from cdd_guidance.practices.clean_engineering.model.call_graph import CallGraphEntry
from cdd_guidance.practices.stories.model.story_model import StoryNode


class Description(StoryNode):
    _semantic_type_name = "Description"
    _graph_practice = "bdd"
    _belongs = {("Context", "Description"), ("Description", "Spec")}

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.contexts = BoundChildren(self, "contexts")

    def clone(self) -> "Description":
        cloned = type(self)(self.name, self.sequential_order)
        for context in self.contexts:
            cloned.contexts.append(context.clone())
        return cloned

    def load_context(self, source: "Context") -> "Context":
        return source.clone()


class Context(StoryNode):
    _semantic_type_name = "Context"
    _graph_practice = "bdd"
    _belongs = {("Observation", "Context"), ("Context", "Context"), ("Context", "Description")}

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.observations = BoundChildren(self, "observations")
        self.contexts = BoundChildren(self, "contexts")

    def clone(self) -> "Context":
        cloned = type(self)(self.name, self.sequential_order)
        for observation in self.observations:
            cloned.observations.append(observation.clone())
        for context in self.contexts:
            cloned.contexts.append(context.clone())
        return cloned

    def load_observation(self, source: "Observation") -> "Observation":
        return source.clone()

    def load_context(self, source: "Context") -> "Context":
        return source.clone()


class Observation(StoryNode):
    _semantic_type_name = "Observation"
    _graph_practice = "bdd"

    def __init__(self, name: str, sequential_order: int = 1, graph=None) -> None:
        super().__init__(name=name, sequential_order=sequential_order, graph=graph)
        self.call_graph: List[CallGraphEntry] = []
        self.surface_lines: List[str] = []

    def clone(self) -> "Observation":
        cloned = type(self)(self.name, self.sequential_order)
        cloned.call_graph = list(self.call_graph)
        cloned.surface_lines = list(self.surface_lines)
        return cloned
