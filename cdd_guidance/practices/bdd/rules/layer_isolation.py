"""layer-isolation — domain specs must not patch infrastructure at import time."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_PATCH_IMPORT = re.compile(r"^\s*@patch\s*\(", re.MULTILINE)
_UNittest_MOCK = re.compile(r"from unittest\.mock import patch")


class LayerIsolation(PracticeGraphRule):
    slug = "layer-isolation"
    node_types = ("Spec",)

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        if not text.strip():
            return []
        if _PATCH_IMPORT.search(text) or _UNittest_MOCK.search(text):
            return [
                "Spec patches infrastructure at import time; isolate layers through ports and adapters."
            ]
        return []
