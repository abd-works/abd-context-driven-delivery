"""Two verbs for one concept: operations of different classes that name the same thing they answer with different
verbs, such as `get_order` and `fetch_order`. Nobody searching for one verb finds the operation named with the other,
so the same work gets written again under the second name."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.source_facts import CONSTRUCTOR_NAMES
from cdd_guidance.practices.clean_engineering.reading.folder_facts import record_fact
from cdd_guidance.practices.clean_engineering.reading.operation_facts import code_operations, file_qualified_name

if TYPE_CHECKING:
    from harness.graph.graph import Node, PracticeNodes

# The fact each operation of such a group keeps: the target named, the verbs used for it, and every operation of the
# group, `file: Class.operation`.
VERBS_FOR_ONE_TARGET = "verbs_for_one_target"
# The verbs that each say an operation answers something it gets from somewhere: one concept, so one word.
ANSWERING_VERBS = ("get", "fetch", "read", "load", "retrieve", "find", "lookup", "obtain", "query")
_SNAKE = re.compile(rf"^({'|'.join(ANSWERING_VERBS)})_([a-z]\w*)$")
_CAMEL = re.compile(rf"^({'|'.join(ANSWERING_VERBS)})([A-Z]\w*)$")
_WORD_START = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


class VerbsForOneTarget:
    """The public production operations whose names are an answering verb and a target, grouped by target; each
    operation of a group that uses more than one verb, across more than one class, keeps the group
    (``verbs_for_one_target``)."""

    def __init__(self, in_graph: "PracticeNodes") -> None:
        self._operations = [
            node for node in code_operations(in_graph) if not node.name.startswith("_") and node.name not in CONSTRUCTOR_NAMES
        ]

    def record(self) -> None:
        kept: dict[str, list] = {}
        for target, members in self._by_target().items():
            kept.update(self._group(target, members))
        for operation in self._operations:
            record_fact(operation, VERBS_FOR_ONE_TARGET, kept.get(operation.node_id, []))

    def _by_target(self) -> dict[str, list[tuple[str, "Node"]]]:
        """The operations named with an answering verb, by the target each names, each with its verb."""
        groups: dict[str, list[tuple[str, "Node"]]] = {}
        for operation in self._operations:
            verb, target = self._split(operation.name)
            if verb:
                groups.setdefault(target, []).append((verb, operation))
        return groups

    def _group(self, target: str, members: list[tuple[str, "Node"]]) -> dict[str, list]:
        """The fact each member keeps, when the members use more than one verb across more than one class."""
        verbs = sorted({verb for verb, _operation in members})
        owners = {(operation.source.file, str(operation.get_fact("owner") or "")) for _verb, operation in members}
        if len(verbs) < 2 or len(owners) < 2:
            return {}
        labels = sorted(file_qualified_name(operation) for _verb, operation in members)
        return {operation.node_id: [target, verbs, labels] for _verb, operation in members}

    def _split(self, name: str) -> tuple[str, str]:
        """The answering verb a name starts with and the target it names, in snake case: `getOrderLines` is `get` and
        `order_lines`; no verb for any other name."""
        snake = _SNAKE.match(name)
        if snake:
            return snake.group(1), snake.group(2)
        camel = _CAMEL.match(name)
        if camel:
            return camel.group(1), _WORD_START.sub("_", camel.group(2)).lower()
        return "", ""
