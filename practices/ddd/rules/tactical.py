"""DDD rules from practices/ddd/scanners (main history) — graph building-block nodes."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class PrivateMethodNaming(PracticeGraphRule):
    slug = "private-method-naming"
    node_types = ("EntityRoot", "Entity", "ValueObject", "DomainService", "Repository")

    def check(self, node, context) -> list[str]:
        if node.name.startswith("_"):
            return [f"Domain type name {node.name!r} should not start with '_'."]
        return []


class FlaccidDataObject(PracticeGraphRule):
    """Entity/value types should expose operations on the graph, not only properties."""

    slug = "flaccid-data-object-no-behavior"
    node_types = ("EntityRoot", "Entity", "ValueObject")

    def check(self, node, context) -> list[str]:
        props = context.child_count(node, ("properties",))
        ops = sum(
            1
            for edge in node.practice.edges.get("owns", [])
            if edge.parent is node and edge.child.type == "Operation"
        )
        if props and ops == 0:
            return [f"{node.type} '{node.name}' has properties but no operations."]
        return []
