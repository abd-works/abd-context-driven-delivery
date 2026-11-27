"""ExampleObservations and ModelledAreas. The examples each Then of the Stories graph observes, and the areas of the
story map a domain model or a class model is written for, which alone are held to those edges."""

from __future__ import annotations

import re
from functools import cached_property
from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from harness.graph.schema_conformance import EXEMPT_FACT
from harness.markdown.format import Format

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.stories.model.story_tree import StoryTree

# The relationships the Stories schema requires of an example that lead to a model: what an example is held to only in
# an area a model is written for.
_EXAMPLE_MODEL_RELATIONSHIPS = ["demonstrates", "retrievedUsing"]
MODEL_WRITTEN_FACT = "model_written"
"""The fact on a Then that says a model is written for its area of the story map, which the rule
then-observes-an-example reads: only there must the Then observe an Example."""


# Where a name written in code breaks into words: at an underscore, and before a capital that follows a small letter.
_WORD_BREAK = re.compile(r"_+|(?<=[a-z0-9])(?=[A-Z])")


def _is_markdown(file: str | None) -> bool:
    return Format.from_extension(PurePosixPath(file or "").suffix).name == "markdown"


class ExampleObservations:
    """The ``observes`` edges of the Stories practice: a step observes the examples its own text and body name, and a
    Then also those the Givens of its scenario and of its story's Background name, the state whose outcome it
    observes. An example is named by its name as written, and, by an example of the step's own story file, in the
    plain words a step is written in (``paid order`` for ``paid_order`` or ``paidOrder``), so a story test whose
    steps hold no code yet observes the same examples as one that calls them. Each is read from the facts every step
    saves with the graph and from the graph's own edges, so it is the same whichever other practices the graph reads."""

    def __init__(self, tree: StoryTree) -> None:
        self.tree = tree
        self.graph = tree.stories.graph

    @cached_property
    def examples(self) -> list["Node"]:
        """The examples on the Stories graph, read once."""
        return self.tree.examples()

    def link(self) -> None:
        for step in [step for step in self.tree.every_step() if self.tree.step_phase(step)]:
            for example in self._observed_by(step):
                self.graph.edges.relate("observes", step, example)

    def _observed_by(self, step: "Node") -> list["Node"]:
        texts = [self.tree.step_body(step)]
        if self.tree.step_phase(step) == "then":
            texts.extend(self.tree.step_body(given) for given in self._givens_of(step))
        named = [example for example in self.examples if any(self._names(text, example, step) for text in texts)]
        return self._of_story_file(step, named)

    def _names(self, text: str, example: "Node", step: "Node") -> bool:
        """Whether text names example: by its name as written, or, for an example of step's own story file, by its
        name in plain words, in any case. An example read from a markdown scenarios file is a line of that file's
        examples table, so only the steps of that file name it: another story's step that holds the same words, such
        as a book's title, means the book, not that story's example."""
        if example.source.file != step.source.file and _is_markdown(example.source.file):
            return False
        if re.search(rf"\b{re.escape(example.name)}\b", text):
            return True
        if example.source.file != step.source.file:
            return False
        words = _WORD_BREAK.sub(" ", example.name)
        return words != example.name and re.search(rf"\b{re.escape(words)}\b", text, re.IGNORECASE) is not None

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
        scenario = self.tree.scenario_of(step)
        if scenario is None:
            return []
        holders = [*self.tree.steps(scenario), *self.tree.background_steps(self.tree.story_of(scenario))]
        givens = [found for found in holders if self.tree.step_phase(found) == "given"]
        return [*givens, *(edge.child for given in givens for edge in self.graph.edges.from_parent("ands", given))]


class ModelledAreas:
    """The areas of the story map a model is written for. An area is the stories directly under one sub-epic or
    epic, with their scenarios, steps and examples; a story the map does not hold is an area of its own. A model is
    written for an area when the graph holds an edge from a step or an example of the area to a node of the domain
    model (DDD) or the class model (Clean Engineering): a step names the class a linked domain term leads to, a step
    invokes an operation, or an example demonstrates a class. Only there must a Then observe an Example
    (then-observes-an-example) and an example show a class and what retrieves it (the Stories schema)."""

    def __init__(self, tree: StoryTree) -> None:
        self.tree = tree
        self.stories = tree.stories
        self.graph = tree.stories.graph

    def record(self) -> None:
        """Say on each Then whether a model is written for its area, and on each example outside a modelled area that
        it is not held to the relationships that lead to a model. A fact is written only where it says something
        new, so a graph with no model keeps its Thens as they were read; a node a refresh kept, whose area is no longer
        what it was, lets go of the fact it held, as a node read anew holds none."""
        for node in self.stories.in_graph.nodes():
            if node.type == "Example":
                self._record(node, EXEMPT_FACT, [] if self._is_modelled(node) else _EXAMPLE_MODEL_RELATIONSHIPS)
            elif self.tree.is_step(node) and self.tree.step_phase(node) == "then":
                self._record(node, MODEL_WRITTEN_FACT, self._is_modelled(node))

    def _record(self, node: "Node", fact: str, held: list[str] | bool) -> None:
        if held:
            node.set_fact(fact, held)
        else:
            node.forget_fact(fact)

    def _is_modelled(self, node: "Node") -> bool:
        return self.tree.area_of(node) in self._modelled

    @cached_property
    def _modelled(self) -> set["Node"]:
        """The areas with an edge from one of their steps or examples to a node of a model."""
        models = [reading.practice for reading in (self.stories.domain_model, self.stories.object_model) if reading is not None]
        if not models:
            return set()
        joined = [edge.parent for edge in self.stories.in_graph.edge_index.of() if edge.child.practice in models]
        return {self.tree.area_of(node) for node in joined if node.type == "Example" or self.tree.is_step(node)}
