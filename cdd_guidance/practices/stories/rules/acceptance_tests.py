"""acceptance_tests fidelity — example and fixture rules."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.markdown.format import Format

from cdd_guidance.practices.stories.model.graph_reading import CALLS_REACH_NONE, CALLS_REACH_TEST
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
    """An example a story test in code uses sits in an examples file, named as its language names one, under an
    examples folder. An example read from a markdown scenarios file is a row of a table there, which no examples
    module holds, so only an example that comes from code is asked."""

    slug = "domain-fixture-example-files"
    node_types = ("Example",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        path = self._fixture_path(node).lower()
        name = path.rsplit("/", 1)[-1]
        if not Format.from_extension(PurePosixPath(name).suffix).is_code:
            return []
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


class CodeStepsInvokeCode(PracticeGraphRule):
    """A When read from a story test in code invokes code it tests. A When in markdown names no code until a realization
    links it, so only a step backed by code is asked. The read records what the step's calls reach (its calls_reach
    fact, cdd_guidance/practices/stories/model/graph_reading.py): a When that calls nothing, or only the story test's
    own helpers and seeds, fails; one whose calls name code the graph has not read is left unjudged."""

    slug = "code-steps-invoke-code"
    node_types = ("When",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if not Format.from_extension(PurePosixPath(node.source.file or "").suffix).is_code:
            return []
        reach = node.get_fact("calls_reach")
        if reach == CALLS_REACH_NONE:
            return [f"When {node.name!r} calls nothing: call the domain operation it tests in the step."]
        if reach == CALLS_REACH_TEST:
            return [f"When {node.name!r} calls only the story test's own helpers or seeds: call the domain operation it tests in the step."]
        return []
