"""acceptance_tests fidelity — example and fixture rules."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

def _imported_module(text: str, name: str) -> str | None:
    """The module a story file imports ``name`` from, when it imports it."""
    for match in re.finditer(r"import\s*(?:type\s*)?\{(?P<names>[^}]+)\}\s*from\s*['\"](?P<module>[^'\"]+)['\"]", text):
        names = [part.strip().split(" as ")[-1].removeprefix("type ").strip() for part in match.group("names").split(",")]
        if name in names:
            return match.group("module")
    return None


class DomainFixtureExampleFiles(PracticeGraphRule):
    slug = "domain-fixture-example-files"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        path = (node.source.file or "").lower()
        module = _imported_module(context.text(node), node.name)
        if module is not None:
            path = module.lower() + ".ts"
        name = path.rsplit("/", 1)[-1]
        if not name.endswith(".examples.ts"):
            return [f"Example file {name!r} should end with .examples.ts under an examples/ folder."]
        if "examples" not in path:
            return [f"Example file {name!r} should live under an examples/ folder."]
        return []

class ExampleRoleNames(PracticeGraphRule):
    slug = "example-role-names"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        for export in re.findall(r"export const (\w+)", text):
            lowered = export.lower()
            if any(role in lowered for role in ("entered", "stored", "expected", "seed", "fixture")):
                return []
        if "export const" in text:
            return [f"Example exports {node.name!r} without a role name (entered/stored/expected/…)."]
        return []

class OriginatingSubEpicExamples(PracticeGraphRule):
    slug = "originating-sub-epic-examples"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        path = node.source.file or ""
        if "/examples/" in path and "sub-epic" in path.lower():
            return []
        if "epic" in path.lower() and "story" not in path.lower() and "examples" in path:
            return [f"Example {path!r} sits on an epic; place fixtures on the owning story/sub-epic."]
        return []

class ExamplesExportDataNotRepository(PracticeGraphRule):
    slug = "examples-export-data-not-repository"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        relative = node.source.file or ""
        if "repository" in relative.lower() and "examples" in relative.lower():
            return [f"Example file '{relative}' looks like a repository; export data fixtures instead."]
        return []
