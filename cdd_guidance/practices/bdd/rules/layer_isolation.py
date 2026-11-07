"""layer-isolation — domain specs must not patch infrastructure at import time."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class LayerIsolation(PracticeGraphRule):
    slug = "layer-isolation"
    node_types = ("Spec",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if not node.get_fact("patches_infrastructure"):
            return []
        return ["Spec patches infrastructure at import time; isolate layers through ports and adapters."]
