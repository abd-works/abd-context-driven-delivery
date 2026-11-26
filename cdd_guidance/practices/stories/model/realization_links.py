"""RealizationLinks. A markdown step's realization, under a Given as under a When, names the model operations the step
leads to, as a story test's step calls the code it tests: each is an edge from the step to the operation in the domain
model (DDD) or the class model (Clean Engineering) its domain terms link to."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from cdd_guidance.practices.stories.model.term_links import ModelHeadings

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.practice_reading import PracticeReading

    from cdd_guidance.practices.stories.model.story_tree import StoryTree

# A realization's call: what it is called on, written as the realization writes it (`Cart`, `checkout-flow`,
# `self.session`), then the operation's name and its opening bracket.
_REALIZED_CALL = re.compile(r"^(?P<receiver>.+?)\.(?P<operation>[A-Za-z_$][\w$]*)\s*\(")
# The name a realization gives the value a call returns, written before the call (``line = cart.addLine(plan)``).
_ASSIGNED_NAME = re.compile(r"^[A-Za-z_$][\w$]*\s*=\s*")
# The fact a step with a realization records once a model is read: whether its realization names an operation of it.
REALIZATION_REACH_FACT = "realization_reach"
REALIZATION_REACHES_MODEL = "model"
REALIZATION_REACHES_NONE = "none"


class RealizationLinks:
    """The edges from each step whose realization names calls (its ``realization_calls`` fact) to the model operations
    they name: the step ``invokes`` each, which is ``invokedBy`` the step. A call is matched only inside the model
    documents the step's own domain-term links lead to (*ModelHeadings*), never by its name across the whole model: a
    call on a class those documents hold (``Cart.addBook``) is that class's operation of that name; a call on anything
    else, an example or a field (``checkout-flow.edit_text``), is the operation of that name of the one class the step's
    links name that declares it. An operation the model no longer declares and a call two linked classes could answer
    leave the step unlinked. Each step with a realization whose links lead to a document the graph read records whether
    it reached the model (``realization_reach``), which the rule code-steps-invoke-code reads; a step whose links lead
    to no document read records nothing, as scenarios are often written before the model they will join."""

    def __init__(self, tree: StoryTree, models: list[PracticeReading]) -> None:
        self.tree = tree
        self.graph = tree.stories.graph
        stories_root = Path(tree.stories.in_graph.source_root)
        self.headings = [ModelHeadings(stories_root, model) for model in models]

    def link(self) -> None:
        for step in self.tree.every_step():
            calls = step.get_fact("realization_calls") or []
            if calls:
                self._link_step(step, calls)

    def _link_step(self, step: "Node", calls: list[str]) -> None:
        linked = LinkedModel(step, self.headings)
        if not linked.reads_a_document:
            return
        operations = linked.operations_called_by_any(calls)
        step.set_fact(REALIZATION_REACH_FACT, REALIZATION_REACHES_MODEL if operations else REALIZATION_REACHES_NONE)
        for operation in operations:
            self.graph.edges.relate("invokes", step, operation)
            self.graph.edges.relate("invokedBy", operation, step)


class LinkedModel:
    """What one step's domain-term links reach in the model: the classes they name, and the operations of every class
    in the documents they lead to."""

    def __init__(self, step: "Node", headings: list[ModelHeadings]) -> None:
        links = [(heading, link) for heading in headings for link in heading.links_of(step)]
        self._linked_classes = {node.name for heading, link in links for node in heading.nodes_at(link)}
        documents = {(heading, link.document) for heading, link in links}
        read = [node for heading, document in documents for node in heading.nodes_in(document)]
        self._operations = [node for node in read if node.type == "Operation"]
        # Every name the documents give a node, a class's among them, so a call on a class that declares no operation
        # of the name is never matched to another class's.
        self._names = {node.name for node in read}

    @property
    def reads_a_document(self) -> bool:
        """Whether the step's links lead to a document the graph read a node from."""
        return bool(self._names)

    def operations_called_by_any(self, calls: list[str]) -> list["Node"]:
        """The operations calls name, each once, in the order the calls name them."""
        found: list["Node"] = []
        for call in calls:
            found.extend(operation for operation in self._operations_called_by(call) if operation not in found)
        return found

    def _operations_called_by(self, call: str) -> list["Node"]:
        """The operations call names, after the name it gives what the call returns: of the class it is called on, when
        the linked documents hold that class, else of the one linked class that declares an operation of that name; none
        for a call that is not on an object, a constructor among them."""
        found = _REALIZED_CALL.match(_ASSIGNED_NAME.sub("", call.strip(), count=1))
        if found is None:
            return []
        receiver = found.group("receiver").rsplit(".", 1)[-1].strip()
        named = found.group("operation")
        if receiver in self._names:
            return self._declared(named, {receiver})
        declared = self._declared(named, self._linked_classes)
        return declared if len({operation.get_fact("owner") for operation in declared}) == 1 else []

    def _declared(self, name: str, owners: set[str]) -> list["Node"]:
        return [operation for operation in self._operations if operation.name == name and operation.get_fact("owner") in owners]
