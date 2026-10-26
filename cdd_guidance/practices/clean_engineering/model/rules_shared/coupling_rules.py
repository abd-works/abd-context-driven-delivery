"""Coupling and encapsulation — Operation / OoadClass facts on the graph node."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class HideInnerDetails(PracticeGraphRule):
    slug = "hide-inner-details"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if node.get_fact("peer_private_access") or node.get_fact("private_reach"):
            return [f"Operation '{node.name}' reaches into a collaborator's private state."]
        return []


class PutLogicOnOwningResource(PracticeGraphRule):
    slug = "put-logic-on-the-owning-resource"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if node.get_fact("peer_private_access"):
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
        if not node.has_fact("property_names"):
            return []
        if node.name in self._FRAMEWORK_NAMES:
            return [f"Class '{node.name}' mirrors framework model types; use domain names."]
        passive = len(node.get_fact("property_names")) <= 4 and not node.get_fact("operation_shapes")
        if node.name.endswith("Data") and passive:
            return [f"Class '{node.name}' is a passive data bag; shape behavior around a resource."]
        return []


class DoNotInventParallelObjectModels(PracticeGraphRule):
    slug = "do-not-invent-parallel-object-models"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        signature = node.get_fact("property_names", [])
        if not signature:
            return []
        for other in context.practice.nodes.get("OoadClass", []):
            if other.node_id == node.node_id or (other.source.file or "") != (node.source.file or ""):
                continue
            if other.get_fact("property_names") == signature:
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
        shapes = node.get_fact("operation_shapes", [])
        if len(shapes) != 1 or len(shapes[0]["callees"]) != 1:
            return []
        return [
            f"Class '{node.name}' only delegates to '{shapes[0]['callees'][0]}'; "
            "merge layers or add real behavior."
        ]
