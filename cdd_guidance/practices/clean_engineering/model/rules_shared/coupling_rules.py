"""Coupling and encapsulation — Operation / OoadClass model fields."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.model.rules_shared.span_helpers import control_flow_depth


class HideInnerDetails(PracticeGraphRule):
    slug = "hide-inner-details"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        operation = _parsed_op(context, node)
        if operation is not None and operation.peer_private_access:
            return [f"Operation '{node.name}' reaches into a collaborator's private state."]
        span = context.span(node)
        if re.search(r"(?<![\w.])\w+\._\w+", span):
            return [f"Operation '{node.name}' reaches into a collaborator's private state."]
        return []


class PutLogicOnOwningResource(PracticeGraphRule):
    slug = "put-logic-on-the-owning-resource"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        operation = _parsed_op(context, node)
        if operation is not None and operation.peer_private_access:
            return [
                f"Operation '{node.name}' uses another object's internals; "
                "move the behavior onto the owning resource."
            ]
        return []


class ShapeClassesAroundResources(PracticeGraphRule):
    slug = "shape-classes-around-resources"
    node_types = ("OoadClass",)

    _FRAMEWORK_NAMES = frozenset(
        {"Module", "GraphCleanEngineeringModel", "CleanEngineeringModel", "Operation", "OoadClass"}
    )

    def check(self, node, context) -> list[str]:
        oclass = context.ce_class(node)
        if oclass is None:
            return []
        if node.name in self._FRAMEWORK_NAMES:
            return [f"Class '{node.name}' mirrors framework model types; use domain names."]
        if node.name.endswith("Data") and len(oclass.properties) <= 4 and not oclass.operations:
            return [f"Class '{node.name}' is a passive data bag; shape behavior around a resource."]
        return []


class DoNotInventParallelObjectModels(PracticeGraphRule):
    slug = "do-not-invent-parallel-object-models"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        oclass = context.ce_class(node)
        if oclass is None:
            return []
        relative = node.source.file or ""
        siblings = [
            other
            for other in context.practice.nodes.get("OoadClass", [])
            if (other.source.file or "") == relative and other.node_id != node.node_id
        ]
        if not siblings:
            return []
        sig = _property_signature(oclass)
        if len(sig) < 1:
            return []
        for other in siblings:
            other_class = context.ce_class(other)
            if other_class is None:
                continue
            if _property_signature(other_class) == sig and len(sig) >= 1:
                return [
                    f"Class '{node.name}' duplicates the same property shape as '{other.name}'. "
                    "Use one canonical model type."
                ]
        return []


class LayerSeparation(PracticeGraphRule):
    slug = "layer-separation"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        if "Facade" not in node.name:
            return []
        oclass = context.ce_class(node)
        if oclass is None or len(oclass.operations) != 1:
            return []
        op = oclass.operations[0]
        if len(op.callees) == 1:
            return [
                f"Class '{node.name}' only delegates to '{op.callees[0]}'; "
                "merge layers or add real behavior."
            ]
        return []


def _property_signature(oclass) -> tuple[str, ...]:
    names = tuple(sorted(p.name for p in oclass.properties))
    return names


def _parsed_op(context, node):
    matched = context.ce_operation(node)
    return matched[1] if matched else None
