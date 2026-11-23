"""Coupling and encapsulation — the Operation and OoadClass facts the build compared across the whole graph."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import SCOPE_ALL, PracticeGraphRule
from harness.graph.violation import Finding

from cdd_guidance.practices.clean_engineering.reading.folder_facts import FOLDER_TYPES, own_fact
from cdd_guidance.practices.clean_engineering.reading.second_registries import SECOND_REGISTRIES
import cdd_guidance.practices.clean_engineering.rules.rule_numbers as rule_numbers
from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class HideInnerDetails(ProductionCodeRule):
    """Reports an operation that reads another object's private member, the one measure of that reach. Where the
    logic belongs instead (``put-logic-on-the-owning-resource``) is judged from the rule's prose."""

    slug = "hide-inner-details"
    # Requires a judge: whether a caller reads how a class stores its data is read from what the member is for; the check matches the access.
    requires_judge = True
    node_types = ("Operation",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        if node.get_fact("peer_private_access"):
            return [Finding(node, f"Operation '{node.name}' reaches into a collaborator's private state.")]
        return []


class ShapeClassesAroundResources(PracticeGraphRule):
    """A service-plus-bag pair: a stateless class whose operations take a class that holds data and does nothing. The
    build keeps on each service the data bags it takes (``data_bags_taken``)."""

    slug = "shape-classes-around-resources"
    # Requires a judge: whether a class is a doer acting on a data bag is read from what the two classes mean; the check matches their shapes.
    requires_judge = True
    node_types = ("OoadClass",)

    def check_practice(self, context: "RuleCheckContext") -> list[Finding]:
        return [
            Finding(
                service,
                f"Class '{service.name}' acts on the data bag '{taken[0]}', which holds the state but no "
                "behavior; put the behavior on the resource that owns the data.",
            )
            for service in context.nodes("OoadClass")
            for taken in [service.get_fact("data_bags_taken") or []]
            if taken
        ]


class DoNotInventParallelObjectModels(PracticeGraphRule):
    """Copies of another class's data anywhere in the graph: copied fields, name copies of a reference, and dicts that
    hold one value per member, keyed by the member's name; and second registries, a collection in one file naming the
    classes a collection in another already names. The build keeps on each class what it copies (``copied_fields``,
    ``copied_references``), and on each folder the collections of its files another file's collection repeats
    (``second_registries``). A copy looks fine in the file that holds it, so the rule runs over the whole code."""

    slug = "do-not-invent-parallel-object-models"
    # Requires a judge: whether a class is a second model of a concept is read from what both classes mean; the check matches their fields.
    requires_judge = True
    node_types = ("OoadClass", *FOLDER_TYPES)
    scope = SCOPE_ALL

    def check_practice(self, context: "RuleCheckContext") -> list[Finding]:
        hits: list[Finding] = []
        for node in context.nodes("OoadClass"):
            hits.extend(Finding(node, message) for message in self._copied_fields(node))
            hits.extend(Finding(node, message) for message in self._copied_references(node))
        for kind in FOLDER_TYPES:
            for folder in context.nodes(kind):
                hits.extend(Finding(folder, message) for message in self._second_registries(folder))
        return hits

    def _second_registries(self, folder: "Node") -> list[str]:
        return [
            f"'{file}' {name} and '{other_file}' {other_name} hold the same classes: {', '.join(shared)}. "
            "Read whether one is a second registry; if it is, read the classes from the other."
            for file, name, count, other_file, other_name, other_count, shared in own_fact(folder, SECOND_REGISTRIES) or []
            if len(shared) >= rule_numbers.FEWEST_CLASSES_REGISTERED_TWICE
            and len(shared) >= rule_numbers.LEAST_SHARE_REGISTERED_TWICE * min(count, other_count)
        ]

    def _copied_fields(self, node: "Node") -> list[str]:
        copied = node.get_fact("copied_fields") or []
        if not copied:
            return []
        other, shared = copied
        return [f"Class '{node.name}' copies the fields {shared} of '{other}'. Use one canonical model type."]

    def _copied_references(self, node: "Node") -> list[str]:
        return [
            f"Class '{node.name}' holds '{field}', a name copy of a '{copied}'; hold the {copied} itself."
            if kind == "name"
            else f"Class '{node.name}' holds '{field}', one value per {copied} keyed by its name; "
            f"ask each {copied} for the value instead."
            for field, kind, copied in node.get_fact("copied_references") or []
        ]


class LayerSeparation(PracticeGraphRule):
    """A pass-through layer: a class, or a whole module folder, whose public operations only forward to one other. The
    build keeps the class or folder each forwards to (``forwards_to``, ``forwards_to_module``)."""

    slug = "layer-separation"
    # Requires a judge: whether a module only passes calls through is read from what it adds; the check compares signatures.
    requires_judge = True
    node_types = ("OoadClass", "Module", "Package")

    def check_practice(self, context: "RuleCheckContext") -> list[Finding]:
        classes = [
            Finding(node, f"Class '{node.name}' only forwards to '{target}'; merge the layers or give it real behavior.")
            for node in context.nodes("OoadClass")
            for target in [node.get_fact("forwards_to") or ""]
            if target
        ]
        folders = [
            Finding(folder, f"Module '{folder.name}' only forwards to '{other}'; collapse the pass-through module.")
            for kind in FOLDER_TYPES
            for folder in context.nodes(kind)
            for other in [folder.get_fact("forwards_to_module") or ""]
            if other
        ]
        return classes + folders
