"""kebab-case-paths — story artifact file names (graph source paths)."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_KEBAB = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.(md|ts|tsx|js|jsx)$")
_CAMEL_FILE = re.compile(r"[A-Z][a-zA-Z0-9]*(?:Story|Test|Spec)")


class KebabCasePaths(PracticeGraphRule):
    slug = "kebab-case-paths"
    node_types = ("Story", "Scenario", "Epic", "SubEpic")

    def check(self, node, context) -> list[str]:
        relative = node.source.file or ""
        if not relative or relative in {"."}:
            return []
        name = relative.rsplit("/", 1)[-1]
        if _KEBAB.match(name):
            return []
        if _CAMEL_FILE.search(name) or re.search(r"[A-Z]", name.split(".")[0]):
            return [f"Story artifact '{name}' should use kebab-case in the file name."]
        return []
