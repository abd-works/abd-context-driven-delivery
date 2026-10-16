"""acceptance_tests fidelity — example and fixture rules."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

def _in_examples_folder(path: str) -> bool:
    """An example file lives in an examples folder. A story file that uses it does not."""
    return "examples" in path.replace("\\", "/").lower().split("/")


def _story_file(name: str) -> bool:
    """A story file uses the example. The word shared in *.story.shared.* does not make it a fixture file."""
    return ".story." in name or name.endswith(".story.ts") or "_story." in name or name.endswith("_story.ts")


class DomainFixtureExampleFiles(PracticeGraphRule):
    slug = "domain-fixture-example-files"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        path = (node.source.file or "").replace("\\", "/").lower()
        if not _in_examples_folder(path):
            return []
        name = path.rsplit("/", 1)[-1]
        if _story_file(name) or not name.endswith(".examples.ts"):
            return [f"Example file {name!r} should end with .examples.ts under an examples/ folder."]
        return []

class ExampleRoleNames(PracticeGraphRule):
    slug = "example-role-names"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        if not _in_examples_folder(node.source.file or ""):
            return []
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
        relative = (node.source.file or "").replace("\\", "/")
        if not _in_examples_folder(relative):
            return []
        if "repository" in relative.lower():
            return [f"Example file '{relative}' looks like a repository; export data fixtures instead."]
        return []
