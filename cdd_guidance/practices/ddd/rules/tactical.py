"""DDD tactical rules — read the facts each building block recorded on its graph node."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.ddd.rules.tactical_helpers import (
    is_presentation_module_source,
    is_screen_driver_class,
    public_operation_names,
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
_CONSTRUCTORS = frozenset({"constructor", "__init__"})


class PrivateMethodNaming(PracticeGraphRule):
    slug = "private-method-naming"
    node_types = _TACTICAL_CLASS

    def check(self, node, context) -> list[str]:
        if node.name.startswith("_"):
            return [f"Domain type name {node.name!r} should not start with '_'."]
        return [
            f"Operation '{name}' on '{node.name}' reaches into another object's private API."
            for name in node.get_fact("peer_private_operations", [])
        ] + [
            f"Operation '{name}' on '{node.name}' should be private (prefix with '_')."
            for name in node.get_fact("public_derive_operations", [])
        ]


class FlaccidDataObject(PracticeGraphRule):
    slug = "flaccid-data-object-no-behavior"
    node_types = ("EntityRoot", "Entity")

    def check(self, node, context) -> list[str]:
        if node.type == "ValueObject" or not node.has_fact("operation_shapes"):
            return []
        public_ops = [name for name in public_operation_names(node) if name not in _CONSTRUCTORS]
        props = len(node.get_fact("property_names", [])) or context.child_count(node, ("properties",))
        if props and not public_ops:
            return [f"{node.type} '{node.name}' has properties but no public operations."]
        return []


class BuildingBlocksFidelityRequiresTacticalStereotype(PracticeGraphRule):
    slug = "building-blocks-fidelity-requires-tactical-stereotype"
    node_types = _TACTICAL_CLASS

    def check(self, node, context) -> list[str]:
        if is_presentation_module_source(node) or node.get_fact("tactical_stereotype", True):
            return []
        return [
            f"Class '{node.name}' lacks a tactical stereotype "
            f"(<<Entity>>, <<Repository>>, or code @entity / @repository on the class)."
        ]


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
        for name in node.get_fact("delegating_operations", []):
            return [
                f"Domain service '{node.name}' only delegates '{name}' to another type; move it onto that aggregate."
            ]
        return []


class RepositoryIsCollectionLifecycle(PracticeGraphRule):
    slug = "repository-is-collection-lifecycle"
    node_types = ("Repository",)

    def check(self, node, context) -> list[str]:
        if not node.name.endswith("Repository") or not node.has_fact("operation_shapes"):
            return []
        if repository_lifecycle_ops(node):
            return []
        public = public_operation_names(node)
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
        return [
            f"Repository '{node.name}.{name}' must take the identity already in hand."
            for name in node.get_fact("identity_free_loads", [])
        ]


class NoOrphanedObjects(PracticeGraphRule):
    slug = "no-orphaned-objects"
    node_types = ("EntityRoot", "Entity", "ValueObject")

    def check(self, node, context) -> list[str]:
        if not node.has_fact("peer_names"):
            return []
        if len(node.get_fact("peer_names")) <= 1:
            return [f"Domain type '{node.name}' has no relationship to other concepts in this module."]
        return []


class ScreenInterfaceNotADomainObject(PracticeGraphRule):
    slug = "screen-interface-not-a-domain-object"
    node_types = ("EntityRoot", "Entity", "ValueObject", "DomainService")

    def check(self, node, context) -> list[str]:
        if not is_screen_driver_class(node):
            return []
        return [
            f"'{node.name}' behaves like a UI driver (open/isShowing); put the action on the owning aggregate."
        ]
