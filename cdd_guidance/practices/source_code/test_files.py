"""Which source files are test code.

A spec or a test fixture catches every exception on purpose, raises on an empty value to prove a guard, and builds its
collaborators inline; judging it by production rules buries the real findings under hits nobody will fix.

Test code is known by its name, so a file is judged the same way whether a whole folder or only that file is read:
- a folder that holds only tests or what they use: `tests`, `test`, `__tests__`, `test-utils`, `fixtures`, `_examples`,
  the story tests and the code they share (`story_tests`), and a spec's support (`spec_support`);
- a dotted part of the file name that gives the file a test role: `order.spec.ts`, `cart.test.py`, `checkout.e2e.ts`,
  `class_channel.feature.py`, a Stories story test and its shared scenarios (`board.story.shared.py`), a page driver
  (`move_ticket.page-driver.ts`), and a test's examples (`chat-bar.examples.ts`);
- the words of the name: a spec (`order_spec.py`, `watch_notice_spec.js`, pytest's `tests/test_order.py`), or what a spec
  uses: `story_test.py`, `rule_fixture.py`, `fixtures.py`, the named examples and tiers a story test replays (`session_board_examples.py`, `session_board_tiers.py`, `rule_examples.py`), the test doubles a spec stands in with (`mcp_daemon_doubles.py`), and a spec's
  helpers (`spec_helpers.py`, `spec_support.py`, `testUtils.ts`).

A production module whose name ends in one of those words, such as `catalog_examples.py`, is read as test code; name it
for what it does instead, so the rules judge it.
"""

from __future__ import annotations

import re
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

from harness.installation.context_config import ContextConfig

# A test function pytest collects, at the top of a file or in a test class.
_TEST_FUNCTION = re.compile(r"^\s*(?:async\s+)?def test_\w*\(", re.MULTILINE)
# The section of a project's ``.context/config.json`` that names files as test code beside those their names mark.
TEST_CODE_SECTION = "test_code"
_TEST_FOLDERS = frozenset({"tests", "test", "__tests__", "test-utils", "fixtures", "_examples", "story_tests", "spec_support"})
# The roles a dotted part of a file name gives it. The first four name a spec; the rest name what a spec uses.
_SPEC_ROLES = frozenset({"spec", "test", "e2e", "feature"})
_SUPPORT_ROLES = frozenset({"story", "page-driver", "examples"})
# The last word of a name: a spec, or what a spec uses.
_SPEC_LAST_WORDS = frozenset({"spec"})
_SUPPORT_LAST_WORDS = frozenset({"test", "fixture", "fixtures", "examples", "tiers", "double", "doubles"})
# A spec's helpers: a first word naming the tests, and a last word naming help (`spec_helpers`, `testUtils`).
_HELPED_FIRST_WORDS = frozenset({"spec", "test"})
_HELPER_LAST_WORDS = frozenset({"helper", "helpers", "support", "utils"})
# Folders of examples a reader studies, such as the catalog's, which no production code runs.
_EXAMPLE_FOLDERS = frozenset({"examples"})
# The first word of a test double's name: `mock_repo.py`, `fake_clock.py`.
_DOUBLE_FIRST_WORDS = frozenset({"mock", "fake"})
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
        `order_spec.py`, or pytest's `tests/test_order.py`. By its name alone, a `test_` prefix names a test only in a
        folder of tests; elsewhere the file's content decides (``ProjectTestCode``), since pytest collects `test_*.py`
        wherever it is, and a production module may start with the word, such as a test runner's own `test_runs.py`."""
        if self.roles & _SPEC_ROLES:
            return True
        if self.words and self.words[-1] in _SPEC_LAST_WORDS:
            return True
        return self.extension == "py" and self.stem.startswith("test_") and bool(_TEST_FOLDERS.intersection(self.folders))

    @property
    def may_be_a_test_by_content(self) -> bool:
        """A Python file named `test_*.py` outside a folder of tests: a test when it declares a test function."""
        return self.extension == "py" and self.stem.startswith("test_") and not _TEST_FOLDERS.intersection(self.folders)

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


    @property
    def is_example(self) -> bool:
        """Code kept to show or stand in, not to run: a file in an examples folder (`catalog/examples/ddd/tactics.ts`),
        or a test double (`mock_repo.py`). Production rules still judge it; it is no part of a module's seam."""
        return bool(_EXAMPLE_FOLDERS.intersection(self.folders)) or bool(self.words and self.words[0] in _DOUBLE_FIRST_WORDS)


class ProjectTestCode:
    """The test code of one project: every file its name marks as test code, and every file the project's
    ``.context/config.json`` names as test code under ``test_code`` (``files``: patterns from the project's root, such as
    ``checks/template_*.py``), for spec support a project keeps under a name that does not say so. Naming it in the
    config keeps the production rules off it, and keeps its calls from counting as a use of the code it calls."""

    def __init__(self, root: Path, patterns: list[str]) -> None:
        self._root = Path(root)
        self._patterns = list(patterns)
        self._declares_tests: dict[str, bool] = {}

    @property
    def root(self) -> Path:
        return self._root

    @classmethod
    def from_project(cls, root: Path | str) -> ProjectTestCode:
        """The test code of the project at root, with the files its config names; none named when it names none."""
        section = ContextConfig(root).load().get(TEST_CODE_SECTION) or {}
        return cls(Path(root), list(section.get("files") or []))

    def is_spec(self, file: str | Path | None) -> bool:
        """A spec or a test: one its name marks as a spec (``TestFileName.is_spec``), or a `test_*.py` file that
        declares a test function."""
        path = self._relative(file)
        return TestFileName(path).is_spec or self._holds_tests(path)

    def is_test_code(self, file: str | Path | None) -> bool:
        """A spec, a test, or test support: by its name, by the config, or by the test functions it declares."""
        path = self._relative(file)
        return TestFileName(path).is_test_code or self._names(path) or self._holds_tests(path)

    def is_example_code(self, file: str | Path | None) -> bool:
        """Test code, or example code or a test double, which production rules judge but no seam holds."""
        return self.is_test_code(file) or TestFileName(self._relative(file)).is_example

    def _relative(self, file: str | Path | None) -> str:
        """The file named from the project's root, with forward slashes; a path outside the root as it is given."""
        path = Path(str(file or ""))
        if path.is_absolute():
            try:
                path = path.resolve().relative_to(self._root.resolve())
            except ValueError:
                pass
        return path.as_posix() if str(file or "") else ""

    def _holds_tests(self, path: str) -> bool:
        """Whether a file named `test_*.py` outside a folder of tests declares a test function, as pytest collects it.
        A class whose name starts with Test is not enough: a production class may be named so (`TestRunRecord`)."""
        if not TestFileName(path).may_be_a_test_by_content:
            return False
        if path not in self._declares_tests:
            source = self._root / path
            text = source.read_text(encoding="utf-8", errors="replace") if source.is_file() else ""
            self._declares_tests[path] = bool(_TEST_FUNCTION.search(text))
        return self._declares_tests[path]

    def _names(self, path: str) -> bool:
        return any(fnmatch(path, pattern) for pattern in self._patterns)


class HoldsProjectTestCode:
    """A practice's part in the knowledge graph that tells test code from production code the one way the project
    does (*ProjectTestCode*), read once from the folder its graph reads."""

    graph: Any
    _test_code: ProjectTestCode | None = None

    @property
    def test_code(self) -> ProjectTestCode:
        """The project's test code, read again only when the graph comes to read another folder, or a first one. A
        graph that read no folder belongs to no project: its test code is what names say, with no config read."""
        folder = getattr(self.graph, "folder", None)
        root = Path(folder or ".")
        if self._test_code is None or self._test_code.root != root:
            self._test_code = ProjectTestCode.from_project(root) if folder else ProjectTestCode(root, [])
        return self._test_code
