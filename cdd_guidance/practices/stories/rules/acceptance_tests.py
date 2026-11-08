"""acceptance_tests fidelity — example and fixture rules."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.markdown.format import Format

from cdd_guidance.practices.stories.model.story_recording import example_source_file

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

# How each language Stories writes acceptance tests in names an examples file, lower-cased: TypeScript and JavaScript
# `account-credentials.examples.ts`, Python `account_credentials_examples.py`, Java `AccountCredentialsExamples.java`.
_EXAMPLES_FILE_ENDINGS = {
    "typescript": ".examples.ts",
    "javascript": ".examples.js",
    "python": "_examples.py",
    "java": "examples.java",
}


class DomainFixtureExampleFiles(PracticeGraphRule):
    slug = "domain-fixture-example-files"
    node_types = ("Example",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        path = self._fixture_path(node).lower()
        name = path.rsplit("/", 1)[-1]
        if not name.endswith(tuple(_EXAMPLES_FILE_ENDINGS.values())):
            return [f"Example file {name!r} should end with {self._ending_for(name)} under an examples/ folder."]
        if "examples" not in PurePosixPath(path).parent.parts:
            return [f"Example file {name!r} should live under an examples/ folder."]
        return []

    def _fixture_path(self, node: Node) -> str:
        """The file the example comes from: the module the story test imports it from, in the story test's language,
        else the story test itself."""
        return example_source_file(node.source.file or "", node.get_fact("imported_modules") or {}, node.name)

    def _ending_for(self, name: str) -> str:
        """The examples-file ending of the file's own language; every ending when the file is in none of them."""
        ending = _EXAMPLES_FILE_ENDINGS.get(Format.from_extension(PurePosixPath(name).suffix).name)
        return ending or " or ".join(_EXAMPLES_FILE_ENDINGS.values())

class ExampleRoleNames(PracticeGraphRule):
    slug = "example-role-names"
    node_types = ("Example",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        exports = node.get_fact("export_names", [])
        for export in exports:
            lowered = export.lower()
            if any(role in lowered for role in ("entered", "stored", "expected", "seed", "fixture")):
                return []
        if exports:
            return [f"Example exports {node.name!r} without a role name (entered/stored/expected/…)."]
        return []

class ExamplesExportDataNotRepository(PracticeGraphRule):
    slug = "examples-export-data-not-repository"
    node_types = ("Example",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        relative = node.source.file or ""
        if "repository" in relative.lower() and "examples" in relative.lower():
            return [f"Example file '{relative}' looks like a repository; export data fixtures instead."]
        return []
