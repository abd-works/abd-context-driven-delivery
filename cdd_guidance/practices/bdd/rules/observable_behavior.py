"""observable-behavior — ported from cdd_guidance.practices/bdd/scanners (source slice on spec nodes)."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_EXPECT_PRIVATE = re.compile(
    r"(?:expect\s*\([^)]*\._\w+|expect\([^)]*\)\.to\([^)]*\._\w+)"
)
_DIRECT_PRIVATE = re.compile(
    r"(?:result|output|instance|obj|subject|sut|actual|entity|self\.\w+)\s*\.\s*_\w+"
)
_PRIVATE_METHOD_CALL = re.compile(
    r"(?:result|output|instance|obj|subject|sut|entity)\s*\.\s*_\w+\s*\("
)


class ObservableBehavior(PracticeGraphRule):
    slug = "observable-behavior"
    node_types = ("Spec", "Description", "Context", "Observation")

    def check(self, node, context) -> list[str]:
        span = context.span(node)
        if not span.strip():
            span = context.text(node)
        if not span.strip():
            return []
        hits: list[str] = []
        for index, line in enumerate(span.splitlines(), start=node.source.start_line or 1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "//")):
                continue
            if _EXPECT_PRIVATE.search(stripped):
                hits.append(f"Line {index}: assertion reaches a private member.")
            elif _DIRECT_PRIVATE.search(stripped):
                hits.append(f"Line {index}: probe reads private state.")
            elif _PRIVATE_METHOD_CALL.search(stripped):
                hits.append(f"Line {index}: call reaches a private method.")
        return hits[:1]
