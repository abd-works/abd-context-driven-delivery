"""DDD tactical rules — building blocks in code (ported from historical scanners)."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

from practices.ddd.rules.tactical_helpers import (
    has_tactical_stereotype,
    is_screen_driver_class,
    other_classes_reference,
    repository_lifecycle_ops,
    technical_name_violation,
)

_TACTICAL_CLASS = (
    "EntityRoot",
    "Entity",
    "ValueObject",
    "Repository",
    "DomainService",
    "Factory",
    "Specification",
)


class PrivateMethodNaming(PracticeGraphRule):
    slug = "private-method-naming"
    node_types = _TACTICAL_CLASS

    def check(self, node, context) -> list[str]:
        if node.name.startswith("_"):
            return [f"Domain type name {node.name!r} should not start with '_'."]
        oclass = context.ce_class(node)
        if oclass is None:
            return []
        messages: list[str] = []
        for op in oclass.operations:
            if op.peer_private_access:
                messages.append(
                    f"Operation '{op.name}' on '{node.name}' reaches into another object's private API."
                )
            if op.name and re.match(r"^derive\w*", op.name) and not op.name.startswith("_"):
                messages.append(
                    f"Operation '{op.name}' on '{node.name}' should be private (prefix with '_')."
                )
        return messages


class FlaccidDataObject(PracticeGraphRule):
    slug = "flaccid-data-object-no-behavior"
    node_types = ("EntityRoot", "Entity", "ValueObject")

    def check(self, node, context) -> list[str]:
        oclass = context.ce_class(node)
        if oclass is not None:
            public_ops = [
                op
                for op in oclass.operations
                if op.name and not str(op.name).startswith("_") and op.name not in {"constructor", "__init__"}
            ]
            props = len(getattr(oclass, "properties", []) or [])
            if props == 0:
                props = context.child_count(node, ("properties",))
            if props and not public_ops:
                return [f"{node.type} '{node.name}' has properties but no public operations."]
            return []
        props = context.child_count(node, ("properties",))
        ops = sum(
            1
            for edge in node.practice.edges.get("owns", [])
            if edge.parent is node and edge.child.type == "Operation"
        )
        if props and ops == 0:
            return [f"{node.type} '{node.name}' has properties but no operations."]
        return []


class BuildingBlocksFidelityRequiresTacticalStereotype(PracticeGraphRule):
    slug = "building-blocks-fidelity-requires-tactical-stereotype"
    node_types = _TACTICAL_CLASS

    def check(self, node, context) -> list[str]:
        if has_tactical_stereotype(context, node):
            return []
        return [f"Class '{node.name}' lacks a tactical stereotype (<<Entity>>, <<Value Object>>, …)."]


class DomainConceptsNotTechnicalNames(PracticeGraphRule):
    slug = "domain-concepts-not-technical-names"
    node_types = _TACTICAL_CLASS + ("Aggregate",)

    def check(self, node, context) -> list[str]:
        message = technical_name_violation(node.name)
        return [message] if message else []


class ServiceIsHomeless(PracticeGraphRule):
    slug = "service-is-homeless"
    node_types = ("DomainService",)

    def check(self, node, context) -> list[str]:
        if not node.name.endswith("Service"):
            return []
        oclass = context.ce_class(node)
        if oclass is None or not oclass.operations:
            return []
        from practices.clean_engineering.model.rules_shared.span_helpers import method_body

        text = context.text(node)
        for op in oclass.operations:
            if not op.name or op.name.startswith("_"):
                continue
            body = method_body(text, op.name)
            if re.search(r"return\s+\w+\.\w+\s*\(", body):
                return [
                    f"Domain service '{node.name}' only delegates '{op.name}' to another type; move it onto that aggregate."
                ]
        return []


class RepositoryIsCollectionLifecycle(PracticeGraphRule):
    slug = "repository-is-collection-lifecycle"
    node_types = ("Repository",)

    def check(self, node, context) -> list[str]:
        if not node.name.endswith("Repository"):
            return []
        lifecycle = repository_lifecycle_ops(context, node)
        if lifecycle:
            return []
        oclass = context.ce_class(node)
        if oclass is None:
            return []
        public = [op.name for op in oclass.operations if op.name and not op.name.startswith("_")]
        if not public:
            return [f"Repository '{node.name}' exposes no collection lifecycle operations (add, find, remove, …)."]
        if len(public) == 1 and public[0].lower() in {"persist", "save", "store"}:
            return [
                f"Repository '{node.name}' only '{public[0]}'; model find/add/remove for the aggregate collection."
            ]
        return []


class LoadWithIdentityInHand(PracticeGraphRule):
    slug = "load-with-identity-in-hand"
    node_types = ("Repository",)

    def check(self, node, context) -> list[str]:
        oclass = context.ce_class(node)
        if oclass is None:
            return []
        messages: list[str] = []
        for op in oclass.operations:
            if op.name.lower() not in {"load", "get", "find", "fetch"}:
                continue
            if not op.parameters:
                messages.append(
                    f"Repository '{node.name}.{op.name}' must take the identity already in hand."
                )
        return messages


class NoOrphanedObjects(PracticeGraphRule):
    slug = "no-orphaned-objects"
    node_types = ("EntityRoot", "Entity", "ValueObject")

    def check(self, node, context) -> list[str]:
        names = class_names_in_file(context, node)
        if len(names) <= 1:
            return [f"Domain type '{node.name}' has no relationship to other concepts in this module."]
        if other_classes_reference(context, node, node.name):
            return []
        for edge_kind in ("associates", "composition", "aggregation", "belongsTo", "accesses"):
            if context.child_count(node, (edge_kind,)):
                return []
        return [f"Domain type '{node.name}' is orphaned — relate it to an aggregate or peer concept."]


class ScreenInterfaceNotADomainObject(PracticeGraphRule):
    slug = "screen-interface-not-a-domain-object"
    node_types = ("EntityRoot", "Entity", "ValueObject", "DomainService")

    def check(self, node, context) -> list[str]:
        if not is_screen_driver_class(context, node):
            return []
        return [
            f"'{node.name}' behaves like a UI driver (open/isShowing); put the action on the owning aggregate."
        ]


def class_names_in_file(context, node) -> set[str]:
    model = context.clean_engineering_model(node)
    if model is None:
        return set()
    return {cls.name for module in model.modules for cls in module.classes}
