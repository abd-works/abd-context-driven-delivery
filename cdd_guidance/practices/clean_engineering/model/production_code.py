"""Which source files are test code, and the rule shape that judges only production code.

A spec or a test fixture catches every exception on purpose, raises on an empty value to prove a guard, and builds its
collaborators inline; judging it by production rules buries the real findings under hits nobody will fix.

Test code is known by its name, so a file is judged the same way whether a whole folder or only that file is read:
- a folder that holds only tests or what they use: `tests`, `test`, `__tests__`, `test-utils`, `fixtures`, `_examples`;
- a dotted part of the file name that gives the file a test role: `order.spec.ts`, `cart.test.py`, `checkout.e2e.ts`,
  `class_channel.feature.py`, a Stories story test and its shared scenarios (`board.story.shared.py`), a page driver
  (`move_ticket.page-driver.ts`), and a test's examples (`chat-bar.examples.ts`);
- the words of the name: a spec (`order_spec.py`, `watch_notice_spec.js`, pytest's `test_order.py`, Java's
  `OrderTest.java`), or what a spec uses: `story_test.py`, `rule_fixture.py`, `fixtures.py`, the named examples and
  tiers a story test replays (`session_board_examples.py`, `session_board_tiers.py`, `rule_examples.py`), and a spec's
  helpers (`spec_helpers.py`, `spec_support.py`, `testUtils.ts`).

A production module whose name ends in one of those words, such as `catalog_examples.py`, is read as test code; name it
for what it does instead, so the rules judge it.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_TEST_FOLDERS = frozenset({"tests", "test", "__tests__", "test-utils", "fixtures", "_examples"})
# The roles a dotted part of a file name gives it. The first four name a spec; the rest name what a spec uses.
_SPEC_ROLES = frozenset({"spec", "test", "e2e", "feature"})
_SUPPORT_ROLES = frozenset({"story", "page-driver", "examples"})
# The last word of a name: a spec, or what a spec uses.
_SPEC_LAST_WORDS = frozenset({"spec"})
_SUPPORT_LAST_WORDS = frozenset({"test", "fixture", "fixtures", "examples", "tiers"})
# A spec's helpers: a first word naming the tests, and a last word naming help (`spec_helpers`, `testUtils`).
_HELPED_FIRST_WORDS = frozenset({"spec", "test"})
_HELPER_LAST_WORDS = frozenset({"helper", "helpers", "support", "utils"})
# Java names its tests by a camel-case last word: `OrderTest`, `OrderTests`.
_JAVA_TEST = re.compile(r"[a-z0-9]Tests?$")
_WORD = re.compile(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])")


class TestFileName:
    """A source file's name and folders, read for the role they give it: a spec, test support, or production code."""

    def __init__(self, file: str | None) -> None:
        parts = str(file or "").replace("\\", "/").split("/")
        self.folders = parts[:-1]
        name = parts[-1]
        dotted = name.split(".")
        self.stem = dotted[0]
        # The dotted parts between the stem and the extension: `spec` in `order.spec.ts`.
        self.roles = {part.lower() for part in dotted[1:-1]}
        self.extension = dotted[-1].lower() if len(dotted) > 1 else ""
        self.words = [word.lower() for word in _WORD.findall(self.stem)]

    @property
    def is_spec(self) -> bool:
        """A spec or a test: `order.spec.ts`, `cart.test.py`, `checkout.e2e.ts`, `class_channel.feature.py`,
        `order_spec.py`, pytest's `test_order.py`, or Java's `OrderTest.java`."""
        if self.roles & _SPEC_ROLES:
            return True
        if self.words and self.words[-1] in _SPEC_LAST_WORDS:
            return True
        if self.extension == "py" and self.stem.startswith("test_"):
            return True
        return self.extension == "java" and _JAVA_TEST.search(self.stem) is not None

    @property
    def is_test_code(self) -> bool:
        """A spec, or something only specs use: a file in a test folder, or one whose name gives it a test role."""
        if self.is_spec or _TEST_FOLDERS.intersection(self.folders):
            return True
        if self.roles & _SUPPORT_ROLES:
            return True
        if not self.words:
            return False
        if self.words[0] in _HELPED_FIRST_WORDS and self.words[-1] in _HELPER_LAST_WORDS:
            return True
        return self.words[-1] in _SUPPORT_LAST_WORDS


def is_spec_file(file: str | None) -> bool:
    """True for a file named as a spec or a test."""
    return TestFileName(file).is_spec


def is_test_code(file: str | None) -> bool:
    """True for a spec, a test, or test support (see the module's description for the names that mark each)."""
    return TestFileName(file).is_test_code


class ProductionCodeRule(PracticeGraphRule):
    """A rule about production code: it passes every node read from a spec, a test, or test support. Every Clean
    Engineering rule that judges one node at a time derives from it; specs are the BDD practice's to judge. A rule that
    judges the whole practice at once reads production code only through what it reads: ``ClassGraph``, the folders'
    imports, and the operations it filters."""

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if is_test_code(node.source.file):
            return []
        return self.check_production(node, context)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        return []
