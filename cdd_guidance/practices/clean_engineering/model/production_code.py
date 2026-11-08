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

_TEST_FOLDERS = frozenset({"tests", "test", "__tests__", "test-utils", "fixtures", "_examples"})
# A spec: `*_spec.py` or pytest's `test_*.py`, a script's `*.spec.ts`, `*.test.ts` or end-to-end `*.e2e.ts`, a Java `*Test.java`.
_SPEC_FILE = re.compile(r"(\.(spec|test|e2e)\.[jt]sx?$)|(_spec\.py$)|(^test_.*\.py$)|(Tests?\.java$)")
# Test support that holds no spec: a fixtures module, and the page driver an end-to-end spec drives its pages through.
_TEST_SUPPORT_FILE = re.compile(r"((^|_)fixtures?\.py$)|(\.page-driver\.[jt]sx?$)")


def is_spec_file(file: str | None) -> bool:
    """True for a file named as a spec or a test, whatever folder holds it: the files a spec's describe tree is read from."""
    return _SPEC_FILE.search(str(file or "").replace("\\", "/").rsplit("/", 1)[-1]) is not None


def is_test_code(file: str | None) -> bool:
    """True for a spec, a test, or test support: a spec file, a file in a tests, test-utils or fixtures folder, a
    fixtures module, or an end-to-end spec's page driver."""
    parts = str(file or "").replace("\\", "/").split("/")
    return bool(_TEST_FOLDERS.intersection(parts[:-1])) or is_spec_file(parts[-1]) or _TEST_SUPPORT_FILE.search(parts[-1]) is not None


class ProductionCodeRule(PracticeGraphRule):
    """A rule about production code: it passes every node read from a spec, a test, or test support."""

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if is_test_code(node.source.file):
            return []
        return self.check_production(node, context)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        return []
