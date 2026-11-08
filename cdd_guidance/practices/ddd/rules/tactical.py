"""DDD tactical rules — read the facts each building block records on its graph node (a *BuildingBlock*, which works
them out from the class it is; a saved graph keeps them)."""

from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model.operation import CONSTRUCTOR_NAMES
from cdd_guidance.practices.ddd.model.stereotypes import BUILDING_BLOCK_KINDS
from harness.graph.practice_rule import PracticeGraphRule

_TECHNICAL_SUFFIXES = frozenset({"result", "response", "dto", "request"})
_AGENT_NOUNS = frozenset({"manager", "helper", "processor", "handler", "controller"})
_CAMEL = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])")


class PrivateMethodNaming(PracticeGraphRule):
    slug = "private-method-naming"
    node_types = BUILDING_BLOCK_KINDS

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
        public_ops = [name for name in node.get_fact("public_operation_names", []) if name not in CONSTRUCTOR_NAMES]
        props = len(node.get_fact("property_names", [])) or context.child_count(node, ("properties",))
        if props and not public_ops:
            return [f"{node.type} '{node.name}' has properties but no public operations."]
        return []


class EveryClassCarriesDddStereotype(PracticeGraphRule):
    slug = "every-class-carries-ddd-stereotype"
    node_types = BUILDING_BLOCK_KINDS

    def check(self, node, context) -> list[str]:
        if node.get_fact("in_screen_module", False) or node.get_fact("tactical_stereotype", True):
            return []
        return [
            f"Class '{node.name}' lacks a DDD stereotype "
            f"(<<Entity>>, <<Repository>>, or code @entity / @repository on the class)."
        ]


class DomainConceptsNotTechnicalNames(PracticeGraphRule):
    slug = "domain-concepts-not-technical-names"
    node_types = BUILDING_BLOCK_KINDS + ("Aggregate",)

    def check(self, node, context) -> list[str]:
        """A name whose last word is a technical one (a result, a response) or that names an agent noun (a manager, a
        helper) names the code, not a domain concept."""
        tokens = [token.lower() for token in _CAMEL.findall(node.name or "") if token]
        if tokens and (tokens[-1] in _TECHNICAL_SUFFIXES or any(token in _AGENT_NOUNS for token in tokens)):
            return [f"Class '{node.name}' uses a technical name instead of a domain concept."]
        return []


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
        if node.get_fact("lifecycle_operations", []):
            return []
        public = node.get_fact("public_operation_names", [])
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
        if not node.has_fact("operation_shapes") or not node.get_fact("drives_a_screen", False):
            return []
        return [
            f"'{node.name}' behaves like a UI driver (open/isShowing); put the action on the owning aggregate."
        ]
