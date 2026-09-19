"""kebab-case-paths — epic/sub-epic folders and story file stems use kebab-case."""

from __future__ import annotations

import re
from pathlib import PurePosixPath

from story_workspace_base import StoryWorkspaceScanner

RULE = "kebab-case-paths"

_KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_PY_EPIC_HELPER = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*_helper\.py$")
_STORY_TEST_FILE = re.compile(r"^[a-z][a-z0-9_]*_story\.test\.[a-z0-9]+$")

# Infrastructure beside the GWT tree — not subject to story slug naming.
_SKIP_FILES = frozenset(
    {
        "conftest.py",
        "story_runner.py",
        "story_types.py",
        "story_test.py",
        "story-test.ts",
        "story-test.js",
        "givens.py",
        "__init__.py",
        "story-context.md",
    }
)


def _is_kebab(token: str) -> bool:
    return bool(token and _KEBAB.fullmatch(token))


class KebabCasePathsScanner(StoryWorkspaceScanner):
    RULE = RULE

    def scan_workspace(self, workspace):
        for suite in workspace.test_suites:
            if not suite.source or not suite.source.file:
                continue
            rel = suite.source.file.replace("\\", "/")
            yield from self._check_rel_path(rel, self.loc(suite, rel))

    def _check_rel_path(self, rel: str, location: str):
        path = PurePosixPath(rel)
        if path.name in _SKIP_FILES:
            return

        for part in path.parts[:-1]:
            if not _is_kebab(part):
                yield self.violation(
                    f"Folder {part!r} in {rel!r} must be kebab-case (lowercase, hyphens only)",
                    location=location,
                    severity="error",
                )

        name = path.name
        if _PY_EPIC_HELPER.fullmatch(name):
            if len(path.parts) != 2:
                yield self.violation(
                    f"Python epic helper {name!r} must sit at {{epic}}/{name} only",
                    location=location,
                    severity="error",
                )
            return

        if _STORY_TEST_FILE.fullmatch(name):
            return

        stem = path.stem
        if "_" in stem and stem.endswith("_stories"):
            yield self.violation(
                f"Legacy snake_case story file {name!r} — use {{story_snake}}_story.test.{path.suffix.lstrip('.')}",
                location=location,
                severity="warning",
            )
            return

        if not _is_kebab(stem.replace(".", "-")):
            yield self.violation(
                f"Path segment {name!r} in {rel!r} must be kebab-case",
                location=location,
                severity="error",
            )
