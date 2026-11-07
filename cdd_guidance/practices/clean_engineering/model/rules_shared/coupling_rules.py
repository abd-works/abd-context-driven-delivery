"""Coupling and encapsulation — Operation / OoadClass facts on the graph node, compared across the whole graph."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.model.base_class_model import is_interface_name
from cdd_guidance.practices.clean_engineering.model.rules_shared.class_graph import ClassGraph, names_in

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

# A copy of another class's fields: at least this many shared fields, covering most of the smaller class.
_MIN_COPIED_FIELDS = 3
_COPIED_SHARE = 0.75
_NAME_COPY = re.compile(r"^_*(?P<owner>[a-z]\w*?)(?:_name|_slug|Name|Slug)$")
_KEYED_COLLECTIONS = frozenset({"dict", "Dict", "Mapping", "MutableMapping", "Record", "Map"})
_STRING_KEYS = frozenset({"str", "string"})


class HideInnerDetails(PracticeGraphRule):
    slug = "hide-inner-details"
    node_types = ("Operation",)

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if node.get_fact("peer_private_access") or node.get_fact("private_reach"):
            return [f"Operation '{node.name}' reaches into a collaborator's private state."]
        return []


class PutLogicOnOwningResource(PracticeGraphRule):
    slug = "put-logic-on-the-owning-resource"
    node_types = ("Operation",)

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if node.get_fact("peer_private_access"):
            return [
                f"Operation '{node.name}' uses another object's internals; "
                "move the behavior onto the owning resource."
            ]
        return []


class ShapeClassesAroundResources(PracticeGraphRule):
    """A service-plus-bag pair: a stateless class whose operations take a class that holds data and does nothing."""

    slug = "shape-classes-around-resources"
    node_types = ("OoadClass",)

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        classes = context.index(ClassGraph)
        bags = {node.name for node in classes.classes if classes.fields(node) and not classes.has_behavior(node)}
        hits: list[tuple[str, str]] = []
        for service in classes.classes:
            # An interface declares what a resource does; it holds no state by design, so it is not a service.
            if classes.fields(service) or not classes.has_behavior(service) or is_interface_name(service.name):
                continue
            taken = sorted(
                {
                    name
                    for operation in classes.operations(service)
                    for _parameter, hint in operation.get_fact("parameters", []) or []
                    for name in names_in(hint) & bags
                    if name != service.name
                }
            )
            if taken:
                hits.append(
                    (
                        service.node_id,
                        f"Class '{service.name}' acts on the data bag '{taken[0]}', which holds the state but no "
                        "behavior; put the behavior on the resource that owns the data.",
                    )
                )
        return hits


class DoNotInventParallelObjectModels(PracticeGraphRule):
    """Copies of another class's data anywhere in the graph: copied fields, name copies of a reference, and dicts that
    hold one value per member, keyed by the member's name."""

    slug = "do-not-invent-parallel-object-models"
    node_types = ("OoadClass",)

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        classes = context.index(ClassGraph)
        fields = {node.node_id: classes.fields(node) for node in classes.classes}
        holders: dict[str, list["Node"]] = {}
        for node in classes.classes:
            for field in fields[node.node_id]:
                holders.setdefault(field, []).append(node)
        hits: list[tuple[str, str]] = []
        for node in classes.classes:
            hits.extend((node.node_id, message) for message in _copied_fields(node, holders, fields))
            hits.extend((node.node_id, message) for message in _copied_references(node, classes, fields[node.node_id]))
        return hits


def _copied_fields(node: "Node", holders: dict[str, list["Node"]], fields: dict[str, dict[str, str]]) -> list[str]:
    """Report the smaller class of each pair once: it is the one holding a subset of the other's fields."""
    own = set(fields[node.node_id])
    shared_counts: dict[str, int] = {}
    others: dict[str, "Node"] = {}
    for field in own:
        for other in holders.get(field, []):
            shared_counts[other.node_id] = shared_counts.get(other.node_id, 0) + 1
            others[other.node_id] = other
    for other_id in sorted(shared_counts):
        other = others[other_id]
        theirs = set(fields[other_id])
        if other is node or _related(node, other) or (len(own), node.node_id) > (len(theirs), other_id):
            continue
        shared = own & theirs
        if (other.source.file == node.source.file and own == theirs) or _copies(shared, own, theirs):
            return [
                f"Class '{node.name}' copies the fields {sorted(shared)} of '{other.name}'. "
                "Use one canonical model type."
            ]
    return []


def _related(node: "Node", other: "Node") -> bool:
    """A subclass repeats its base's fields by design."""
    return other.name in (node.get_fact("bases", []) or []) or node.name in (other.get_fact("bases", []) or [])


def _copies(shared: set[str], own: set[str], theirs: set[str]) -> bool:
    smaller = min(len(own), len(theirs))
    return len(shared) >= _MIN_COPIED_FIELDS and len(shared) >= _COPIED_SHARE * smaller


def _copied_references(node: "Node", classes: ClassGraph, fields: dict[str, str]) -> list[str]:
    hits: list[str] = []
    for field, hint in fields.items():
        named = _NAME_COPY.match(field)
        owner = _class_named(named.group("owner"), classes) if named else ""
        if owner and owner != node.name:
            hits.append(
                f"Class '{node.name}' holds '{field}', a name copy of a '{owner}'; hold the {owner} itself."
            )
            continue
        member = _member_keyed_by_name(field, hint, classes)
        if member and member != node.name:
            hits.append(
                f"Class '{node.name}' holds '{field}', one value per {member} keyed by its name; "
                f"ask each {member} for the value instead."
            )
    return hits


def _member_keyed_by_name(field: str, hint: str, classes: ClassGraph) -> str:
    """`fidelity_states: dict[str, str]` names a member class and keys a dict of one value each by name."""
    mentioned = names_in(hint)
    if not mentioned & _KEYED_COLLECTIONS or not mentioned & _STRING_KEYS:
        return ""
    words = _words(field)
    for length in range(len(words) - 1, 0, -1):
        member = _class_named("_".join(words[:length]), classes)
        if member and member not in mentioned:
            return member
    return ""


def _class_named(snake: str, classes: ClassGraph) -> str:
    pascal = "".join(word.capitalize() for word in _words(snake))
    return pascal if pascal in classes.by_name else ""


def _words(name: str) -> list[str]:
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name.strip("_"))
    return [word.lower() for word in spaced.split("_") if word]


class LayerSeparation(PracticeGraphRule):
    """A pass-through layer: a class, or a whole module folder, whose public operations only forward to one other."""

    slug = "layer-separation"
    node_types = ("OoadClass", "Module", "Package")

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        classes = context.index(ClassGraph)
        targets = {node.node_id: _forwarding_target(node, classes) for node in classes.classes}
        names = {node.node_id: node.name for node in context.nodes("OoadClass")}
        hits = [
            (
                node.node_id,
                f"Class '{node.name}' only forwards to '{names[targets[node.node_id]]}'; "
                "merge the layers or give it real behavior.",
            )
            for node in classes.classes
            if targets[node.node_id]
        ]
        return hits + _pass_through_folders(context, classes, targets)


def _forwarding_target(node: "Node", classes: ClassGraph) -> str:
    """The one class every public operation forwards to, or empty when the class does any work of its own."""
    operations = classes.operations(node)
    if not operations or len(classes.fields(node)) > 1:
        return ""
    candidates: set[str] | None = None
    for operation in operations:
        callee = _sole_forward(operation)
        if not callee or (len(operations) == 1 and callee != operation.name):
            return ""
        defining = classes.classes_defining(callee) - {node.node_id}
        candidates = defining if candidates is None else candidates & defining
    return sorted(candidates)[0] if candidates and len(candidates) == 1 else ""


def _sole_forward(operation: "Node") -> str:
    """The callee of an operation whose body is one statement making one call on a collaborator: a parameter
    (``cart.subtotal()``) or a field (``self._cart.subtotal()``)."""
    callees = {callee for callee in operation.get_fact("callees", []) or [] if callee}
    body = getattr(getattr(operation, "body", None), "text", "") or ""
    statements = [line for line in body.splitlines() if line.strip() and not line.strip().startswith(("#", "//"))]
    if len(callees) != 1 or len(statements) != 1:
        return ""
    callee = next(iter(callees))
    parameters = [re.escape(name) for name, _hint in operation.get_fact("parameters", []) or []]
    receivers = [r"(?:self|this)\.\w+"] + [rf"\b{name}" for name in parameters]
    forwards = re.search(rf"(?:{'|'.join(receivers)})\.{re.escape(callee)}\s*\(", statements[0])
    return callee if forwards else ""


def _folder_id(node: "Node", context: "RuleCheckContext") -> str:
    """The id of the folder the class belongs to, through its belongsTo edge."""
    return next((folder.node_id for folder in context.targets(node, "belongsTo")), "")


def _pass_through_folders(context: "RuleCheckContext", classes: ClassGraph, targets: dict[str, str]) -> list[tuple[str, str]]:
    folder_of = {node.node_id: _folder_id(node, context) for node in context.nodes("OoadClass")}
    members: dict[str, list[str]] = {}
    for node in classes.classes:
        members.setdefault(folder_of[node.node_id], []).append(node.node_id)
    hits: list[tuple[str, str]] = []
    for folder_id, class_ids in members.items():
        folder = context.node(folder_id)
        if folder is None or folder.type not in ("Module", "Package") or not all(targets[class_id] for class_id in class_ids):
            continue
        reached = {folder_of[targets[class_id]] for class_id in class_ids} - {folder_id}
        if len(reached) == 1:
            other = context.node(next(iter(reached)))
            hits.append(
                (
                    folder_id,
                    f"Module '{folder.name}' only forwards to '{other.name if other else next(iter(reached))}'; "
                    "collapse the pass-through module.",
                )
            )
    return hits
