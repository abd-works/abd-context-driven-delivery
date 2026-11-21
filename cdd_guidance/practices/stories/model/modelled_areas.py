"""ExampleObservations and ModelledAreas. The examples each Then of the Stories graph observes, and the areas of the
story map a domain model or a class model is written for, which alone are held to those edges."""

from __future__ import annotations

import re
from functools import cached_property
from typing import TYPE_CHECKING

from harness.graph.schema_conformance import EXEMPT_FACT
from harness.guidance.practice_reading import PracticeReading

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.stories.model.graph_reading import StoryTree

_STEP_TYPES = frozenset({"Step", "Given", "When", "Then"})
# A story map's epic is recorded as an Epic, or as a SubEpic under another epic.
_EPIC_TYPES = frozenset({"Epic", "SubEpic"})
# The relationships the Stories schema requires of an example that lead to a model: what an example is held to only in
# an area a model is written for.
_EXAMPLE_MODEL_RELATIONSHIPS = ["demonstrates", "retrievedUsing"]
MODEL_WRITTEN_FACT = "model_written"
"""The fact on a Then that says a model is written for its area of the story map, which the rule
then-observes-an-example reads: only there must the Then observe an Example."""


class ExampleObservations:
    """The ``observes`` edges of the Stories practice: a step observes the examples its own text and body name, and a
    Then also those the Givens of its scenario and of its story's Background name, the state whose outcome it
    observes. Each is read from the facts every step saves with the graph and from the graph's own edges, so it is
    the same whichever other practices the graph reads."""

    def __init__(self, stories: PracticeReading, tree: "StoryTree") -> None:
        self.stories = stories
        self.tree = tree
        self.graph = stories.graph

    @cached_property
    def examples(self) -> list["Node"]:
        """The examples on the Stories graph, read once."""
        return self.stories.in_graph.nodes("Example")

    def link(self) -> None:
        for step in [node for node in self.stories.in_graph.nodes() if node.type in _STEP_TYPES and node.get_fact("phase")]:
            for example in self._observed_by(step):
                self.graph.edges.relate("observes", step, example)

    def _observed_by(self, step: "Node") -> list["Node"]:
        texts = [self._step_body(step)]
        if step.get_fact("phase") == "then":
            texts.extend(self._step_body(given) for given in self._givens_of(step))
        named = [example for example in self.examples if any(re.search(rf"\b{re.escape(example.name)}\b", text) for text in texts)]
        return self._of_story_file(step, named)

    def _of_story_file(self, step: "Node", examples: list["Node"]) -> list["Node"]:
        """examples, keeping of those that share a name only the one recorded for step's own story file: each story file
        records the examples it uses, so two files that each use a LISTED hold two nodes of that name, and a step means
        its own file's. A name no example of its file has keeps every example of that name."""
        own_id = lambda example: f"stories:Example:{step.source.file}:{example.name}"  # noqa: E731
        own_names = {example.name for example in examples if example.node_id == own_id(example)}
        return [example for example in examples if example.name not in own_names or example.node_id == own_id(example)]

    def _givens_of(self, step: "Node") -> list["Node"]:
        """The Given steps of the scenario step sits in and of its story's Background, with the steps chained onto
        them."""
        scenario = self.graph.edges.direct_parent(step)
        while scenario is not None and scenario.type != "Scenario":
            scenario = self.graph.edges.direct_parent(scenario)
        if scenario is None:
            return []
        holders = [scenario, *self._backgrounds_of(scenario)]
        givens = [found for holder in holders for found in self.tree.steps(holder) if found.get_fact("phase") == "given"]
        return [*givens, *(edge.child for given in givens for edge in self.graph.edges.from_parent("ands", given))]

    def _backgrounds_of(self, scenario: "Node") -> list["Node"]:
        """The Background of the story scenario sits in; none for a story that writes none."""
        story = self.graph.edges.direct_parent(scenario)
        return [] if story is None else [edge.child for edge in self.graph.edges.from_parent("background", story)]

    def _step_body(self, step: "Node") -> str:
        """The step's own text and the body its story test gives it."""
        return f"{step.name}\n{step.get_fact('body_text') or ''}"


class ModelledAreas:
    """The areas of the story map a model is written for. An area is the stories directly under one sub-epic or
    epic, with their scenarios, steps and examples; a story the map does not hold is an area of its own. A model is
    written for an area when the graph holds an edge from a step or an example of the area to a node of the domain
    model (DDD) or the class model (Clean Engineering): a step names the class a linked domain term leads to, a step
    invokes an operation, or an example demonstrates a class. Only there must a Then observe an Example
    (then-observes-an-example) and an example show a class and what retrieves it (the Stories schema)."""

    def __init__(self, stories: PracticeReading) -> None:
        self.stories = stories
        self.graph = stories.graph

    def record(self) -> None:
        """Say on each Then whether a model is written for its area, and on each example outside a modelled area that
        it is not held to the relationships that lead to a model. A fact is written only where it says something
        new, so a graph with no model keeps its Thens as they were read."""
        for node in self.stories.in_graph.nodes():
            if node.type == "Example":
                self._record(node, EXEMPT_FACT, [] if self._is_modelled(node) else _EXAMPLE_MODEL_RELATIONSHIPS)
            elif node.type in _STEP_TYPES and node.get_fact("phase") == "then":
                self._record(node, MODEL_WRITTEN_FACT, self._is_modelled(node))

    def _record(self, node: "Node", fact: str, value: list[str] | bool) -> None:
        if value or node.has_fact(fact):
            node.set_fact(fact, value)

    def _is_modelled(self, node: "Node") -> bool:
        return self._area_of(node) in self._modelled

    @cached_property
    def _modelled(self) -> set["Node"]:
        """The areas with an edge from one of their steps or examples to a node of a model."""
        models = [reading.practice for reading in (self.stories.domain_model, self.stories.object_model) if reading is not None]
        if not models:
            return set()
        joined = [edge.parent for edge in self.stories.in_graph.edge_index.of() if edge.child.practice in models]
        return {self._area_of(node) for node in joined if node.type == "Example" or node.type in _STEP_TYPES}

    def _area_of(self, node: "Node") -> "Node":
        """The nearest sub-epic or epic above node; for a node under none, the topmost node above it, its story."""
        above = node
        while above.type not in _EPIC_TYPES:
            parent = self.graph.edges.direct_parent(above)
            if parent is None:
                return above
            above = parent
        return above
