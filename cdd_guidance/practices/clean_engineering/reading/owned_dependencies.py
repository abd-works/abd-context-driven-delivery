"""The dependencies each class reaches in a way that suggests it should own them: another class it builds on each call
from strings or dicts, or finds by name. The two objects are then not independent, and the one that builds or finds
the other is the owner to consider, holding it as a part or as a collaborator it is handed."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.reading.call_arguments import CallArguments
from cdd_guidance.practices.clean_engineering.reading.class_facts import ComparedFact
from cdd_guidance.practices.clean_engineering.reading.code_file import (
    CREATED_ON_EACH_CALL,
    LOOKED_UP_BY_NAME,
    REACHED_FACT,
    THROUGH_FACT,
)
from cdd_guidance.practices.clean_engineering.reading.folder_facts import record_fact

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.reading.production_classes import ProductionClass, ProductionClasses

# The fact each class keeps: the class it reaches, how, and the operations that reach it that way.
DEPENDENCIES_TO_OWN = "dependencies_to_own"
BUILT_ON_EACH_CALL = "built on each call"
# An argument that names or records something: a string literal, a dict written out, or keyword values unpacked. A
# formatted string (an f-string, a script's template) is a message or a label made for the call, not a reference.
_TEXT_OR_RECORD = re.compile(r"""^(?:\w+\s*=\s*)?(?:[rbuRBU]{0,2}["']|\{|\*\*|dict\()""")
# An argument named for what identifies or records something: a name, slug, key, path, or a record of data handed on.
_NAMED_TEXT = re.compile(r"(?:^|[._])(?:name|slug|key|path|record|data|row|config|payload)s?$", re.IGNORECASE)


class DependenciesToOwn(ComparedFact):
    """Each production class's dependencies on another production class that it builds on each call from strings or
    dicts, or looks up by name (``dependencies_to_own``: the class, ``built on each call`` or ``looked up by name``, and
    the operations that do it). A value, a failure, or a record with no behaviour the class makes is no dependency to
    own; neither is a class it is handed, holds, or builds once in its constructor."""

    def record(self) -> None:
        found: dict[str, list[list]] = {}
        production = {each.node_id: each for each in self._classes}
        for edge in self._classes.in_graph.edge_index.of("dependsOn"):
            owner = production.get(edge.parent.node_id)
            if owner is None or edge.child.node_id not in production or edge.child is edge.parent:
                continue
            if self._classes.is_value(edge.child.name) or not production[edge.child.node_id].has_behavior:
                continue
            found.setdefault(owner.node_id, []).extend(self._to_own(owner, edge.child, dict(edge.facts)))
        for each in self._classes:
            record_fact(each.node, DEPENDENCIES_TO_OWN, found.get(each.node_id, []))

    def _to_own(self, owner: "ProductionClass", other: "Node", facts: dict) -> list[list]:
        reached = set(facts.get(REACHED_FACT, []))
        through = list(facts.get(THROUGH_FACT, []))
        entries: list[list] = []
        if CREATED_ON_EACH_CALL in reached:
            builders = [name for name in through if self._builds_from_text(owner, name, other.name)]
            if builders:
                entries.append([other.name, BUILT_ON_EACH_CALL, builders])
        if LOOKED_UP_BY_NAME in reached:
            entries.append([other.name, LOOKED_UP_BY_NAME, through])
        return entries

    def _builds_from_text(self, owner: "ProductionClass", operation_name: str, built: str) -> bool:
        """True when the owner's operation of that name builds the class from a string or a dict: an argument written
        as one, or named for one."""
        bodies = [str(operation.get_fact("body_text") or "") for operation in self._operations_of(owner) if operation.name == operation_name]
        return any(
            _TEXT_OR_RECORD.match(argument) or _NAMED_TEXT.search(argument.split("=")[-1].strip())
            for body in bodies
            for call in CallArguments(body).of(built)
            for argument in call
        )

    def _operations_of(self, owner: "ProductionClass") -> list["Node"]:
        """Every operation the class owns, private ones among them."""
        return [edge.child for edge in owner.node.graph.edges.from_parent("owns", owner.node) if edge.child.type == "Operation"]
