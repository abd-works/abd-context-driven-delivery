"""Coupling and encapsulation — the Operation and OoadClass facts the build compared across the whole graph."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding

from cdd_guidance.practices.clean_engineering.reading.folder_facts import FOLDER_TYPES
from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class HideInnerDetails(ProductionCodeRule):
    """Reports an operation that reads another object's private member, the one measure of that reach. Where the
    logic belongs instead (``put-logic-on-the-owning-resource``) is judged from the rule's prose."""

    slug = "hide-inner-details"
    node_types = ("Operation",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        if node.get_fact("peer_private_access"):
            return [Finding(node, f"Operation '{node.name}' reaches into a collaborator's private state.")]
        return []


class ShapeClassesAroundResources(PracticeGraphRule):
    """A service-plus-bag pair: a stateless class whose operations take a class that holds data and does nothing. The
    build keeps on each service the data bags it takes (``data_bags_taken``)."""

    slug = "shape-classes-around-resources"
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
    hold one value per member, keyed by the member's name. The build keeps on each class what it copies
    (``copied_fields``, ``copied_references``)."""

    slug = "do-not-invent-parallel-object-models"
    node_types = ("OoadClass",)

    def check_practice(self, context: "RuleCheckContext") -> list[Finding]:
        hits: list[Finding] = []
        for node in context.nodes("OoadClass"):
            hits.extend(Finding(node, message) for message in self._copied_fields(node))
            hits.extend(Finding(node, message) for message in self._copied_references(node))
        return hits

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
