"""Which source files are production code, and the rule shape that judges only production code.

A spec or a test fixture catches every exception on purpose, raises on an empty value to prove a guard, and builds its
collaborators inline; judging it by production rules buries the real findings under hits nobody will fix.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_TEST_FOLDERS = frozenset({"tests", "test", "__tests__", "fixtures", "_examples"})
_TEST_FILE = re.compile(r"(\.(spec|test)\.[jt]sx?$)|(_spec\.py$)|(^test_.*\.py$)|((^|_)fixtures?\.py$)")


def is_test_code(file: str | None) -> bool:
    """True for a spec, a test, or test support: a file in a tests or fixtures folder, a `*_spec.py`, `test_*.py`,
    `*.spec.ts` or `*.test.ts`, or a fixtures module."""
    parts = str(file or "").replace("\\", "/").split("/")
    return bool(_TEST_FOLDERS.intersection(parts[:-1])) or _TEST_FILE.search(parts[-1]) is not None


class ProductionCodeRule(PracticeGraphRule):
    """A rule about production code: it passes every node read from a spec, a test, or test support."""

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if is_test_code(node.source.file):
            return []
        return self.check_production(node, context)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        return []
