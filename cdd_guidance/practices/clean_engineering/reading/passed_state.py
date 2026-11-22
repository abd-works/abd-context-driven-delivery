"""State handed down as parameters: a value an operation takes and hands on, unchanged, to the next operation and that
one to the next; and one value every operation of a class takes. Each is state an object should hold, so the
operations read it there instead of being handed it again on every call."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.source_facts import CONSTRUCTOR_NAMES
from cdd_guidance.practices.clean_engineering.reading.call_arguments import CallArguments
from cdd_guidance.practices.clean_engineering.reading.folder_facts import record_fact
from cdd_guidance.practices.clean_engineering.reading.operation_facts import code_operations, qualified_name
from cdd_guidance.practices.clean_engineering.reading.production_classes import parameters_of

if TYPE_CHECKING:
    from harness.graph.graph import Node, PracticeNodes

    from cdd_guidance.practices.clean_engineering.reading.production_classes import ProductionClasses

# The fact the operation that starts handing a value down keeps: the parameter, and each operation it passes through.
HANDS_DOWN = "hands_down"
# The fact a class keeps when every one of its operations takes one parameter: its name, and how many operations.
TAKEN_BY_EVERY_OPERATION = "taken_by_every_operation"
# The parameter a method takes for its own object, which no caller hands down.
_OWN_OBJECT = frozenset({"self", "cls"})
# A class needs at least two operations for one parameter to be taken by every one.
_FEWEST_OPERATIONS_COMPARED = 2

# One hand-on: an operation, and the parameter of it that holds the value.
_Step = tuple[str, str]


class HandedDownParameters:
    """Each production operation that takes a parameter and hands it, unchanged, as an argument to an operation it
    calls, which hands it on again; the operation that starts the chain that reaches the most other classes keeps it
    (``hands_down``: the parameter, how many times the value passes to another class, and the operations,
    `Class.operation`, in the order the value passes them). A value handed between one class's own operations stays
    with the object that holds it, so only a pass to another class counts."""

    def __init__(self, in_graph: "PracticeNodes") -> None:
        self._operations = {node.node_id: node for node in code_operations(in_graph)}
        self._parameters = {
            node_id: [parameter.name for parameter in parameters_of(node) if parameter.name not in _OWN_OBJECT]
            for node_id, node in self._operations.items()
        }
        # The longest chain of hand-ons from each step, once it is worked out.
        self._chains: dict[_Step, list[_Step]] = {}

    def record(self) -> None:
        hands = self._hands()
        received = {onward for onwards in hands.values() for onward in onwards}
        chains: dict[str, list] = {}
        for step in sorted(set(hands) - received):
            chain = self._longest(step, hands, frozenset())
            kept = chains.get(step[0], [None, 0, []])
            if (self._crossings(chain), len(chain)) > (kept[1], len(kept[2])):
                chains[step[0]] = [step[1], self._crossings(chain), [qualified_name(self._operations[node_id]) for node_id, _name in chain]]
        for node_id, operation in self._operations.items():
            record_fact(operation, HANDS_DOWN, chains.get(node_id, []))

    def _hands(self) -> dict[_Step, list[_Step]]:
        """Each step a value is handed from, with each step it is handed to."""
        hands: dict[_Step, list[_Step]] = {}
        for node_id, operation in self._operations.items():
            for step, onward in self._hand_ons(node_id, operation):
                hands.setdefault(step, []).append(onward)
        return hands

    def _hand_ons(self, node_id: str, operation: "Node") -> list[tuple[_Step, _Step]]:
        """Each of the operation's parameters it hands, as written, to an operation of the code it calls. A value handed to a
        constructor is how the object built comes to hold it, which is what the rule asks for, so it ends the chain."""
        calls = CallArguments(str(operation.get_fact("body_text") or ""))
        callees = [edge.child for edge in operation.graph.edges.from_parent("invokes", operation)]
        handed = [callee for callee in callees if callee.node_id in self._operations and callee is not operation and callee.name not in CONSTRUCTOR_NAMES]
        return [((node_id, value), onward) for callee in handed for value, onward in self._handed_to(callee, calls, self._parameters[node_id])]

    def _handed_to(self, callee: "Node", calls: CallArguments, taken: list[str]) -> list[tuple[str, _Step]]:
        """Each parameter of taken the body hands to callee, with the step of callee that receives it."""
        receiving = self._parameters[callee.node_id]
        received = [self._received(argument, place, receiving) for arguments in calls.of(callee.name) for place, argument in enumerate(arguments)]
        return [(value, (callee.node_id, receiver)) for value, receiver in received if value in taken and receiver]

    def _received(self, argument: str, place: int, receiving: list[str]) -> tuple[str, str]:
        """The value an argument hands, and the callee's parameter that takes it: by keyword, the parameter of that
        name; else the parameter in its place."""
        keyword, equals, value = argument.partition("=")
        if equals and not value.startswith("=") and keyword.strip() in receiving:
            return value.strip(), keyword.strip()
        positional = argument.strip() if not equals else ""
        return positional, receiving[place] if positional and place < len(receiving) else ""

    def _longest(self, step: _Step, hands: dict[_Step, list[_Step]], seen: frozenset[_Step]) -> list[_Step]:
        """The longest chain of hand-ons from step, never passing one operation's parameter twice. Each step's chain is
        worked out once and kept, so a repository's many calls are followed in time linear in its hand-ons."""
        if step not in self._chains:
            onward = [self._longest(next_step, hands, seen | {step}) for next_step in hands.get(step, []) if next_step not in seen | {step}]
            self._chains[step] = [step, *max(onward, key=self._crossings, default=[])]
        return self._chains[step]

    def _crossings(self, chain: list[_Step]) -> int:
        """How many times the value passes from one class's operation to another class's."""
        owners = [str(self._operations[node_id].get_fact("owner") or self._operations[node_id].source.file) for node_id, _name in chain]
        return sum(1 for before, after in zip(owners, owners[1:]) if before != after)


class ParameterEveryOperationTakes:
    """Each production class every public operation of which, constructors and properties aside, takes a parameter of
    the same name (``taken_by_every_operation``: the parameter and how many operations take it)."""

    def __init__(self, classes: "ProductionClasses") -> None:
        self._classes = classes

    def record(self) -> None:
        for each in self._classes:
            record_fact(each.node, TAKEN_BY_EVERY_OPERATION, self._taken_by_all(each.operations))

    def _taken_by_all(self, operations: list["Node"]) -> list:
        acting = [
            operation for operation in operations
            if operation.name not in CONSTRUCTOR_NAMES and not operation.name.startswith("_") and not operation.get_fact("is_property")
        ]
        if len(acting) < _FEWEST_OPERATIONS_COMPARED:
            return []
        shared = set.intersection(*({parameter.name for parameter in parameters_of(operation)} - _OWN_OBJECT for operation in acting))
        return [sorted(shared)[0], len(acting)] if shared else []
