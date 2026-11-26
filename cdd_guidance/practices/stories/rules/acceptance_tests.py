"""acceptance_tests fidelity — example and fixture rules."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding
from harness.markdown.format import Format

from cdd_guidance.practices.stories.model.graph_reading import CALLS_REACH_NONE, CALLS_REACH_TEST
from cdd_guidance.practices.stories.model.realization_links import REALIZATION_REACH_FACT, REALIZATION_REACHES_NONE
from cdd_guidance.practices.stories.model.story_recording import example_source_file

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

# How each language Stories writes acceptance tests in names an examples file, lower-cased: TypeScript and JavaScript
# `account-credentials.examples.ts`, Python `account_credentials_examples.py`.
_PYTHON_EXAMPLES_ENDING = "_examples.py"
_EXAMPLES_FILE_ENDINGS = {
    "typescript": ".examples.ts",
    "javascript": ".examples.js",
    "python": _PYTHON_EXAMPLES_ENDING,
}
# The fidelity a story is read at once one of its steps has a body, which code-steps-invoke-code alone judges.
ACCEPTANCE_TESTS_FIDELITY = "acceptance_tests"


class DomainFixtureExampleFiles(PracticeGraphRule):
    """An example a story test in code uses sits in an examples file, named as its language names one. A TypeScript
    or JavaScript one sits under an examples folder of its epic. A Python one sits wherever Python can import it,
    beside the code it builds (``space/kanban/session_board_examples.py``): a story folder's name holds hyphens, which
    no Python import can name. An example read from a markdown scenarios file is a row of a table there, which no
    examples module holds, so only an example that comes from code is asked."""

    slug = "domain-fixture-example-files"
    node_types = ("Example",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        path = self._fixture_path(node).lower()
        name = path.rsplit("/", 1)[-1]
        if not Format.from_extension(PurePosixPath(name).suffix).is_code:
            return []
        if not name.endswith(tuple(_EXAMPLES_FILE_ENDINGS.values())):
            ending = self._ending_for(name)
            where = "" if ending == _PYTHON_EXAMPLES_ENDING else " under an examples/ folder"
            return [Finding(node, f"Example file {name!r} should end with {ending}{where}.")]
        if not name.endswith(_PYTHON_EXAMPLES_ENDING) and "examples" not in PurePosixPath(path).parent.parts:
            return [Finding(node, f"Example file {name!r} should live under an examples/ folder.")]
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
    requires_judge = True
    node_types = ("Example",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        exports = node.get_fact("export_names", [])
        for export in exports:
            lowered = export.lower()
            if any(role in lowered for role in ("entered", "stored", "expected", "seed", "fixture")):
                return []
        if exports:
            return [Finding(node, f"Example exports {node.name!r} without a role name (entered/stored/expected/…).")]
        return []

class ExamplesExportDataNotRepository(PracticeGraphRule):
    slug = "examples-export-data-not-repository"
    requires_judge = True
    node_types = ("Example",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        relative = node.source.file or ""
        if "repository" in relative.lower() and "examples" in relative.lower():
            return [Finding(node, f"Example file '{relative}' looks like a repository; export data fixtures instead.")]
        return []


class CodeStepsInvokeCode(PracticeGraphRule):
    """A When backed by code invokes what it tests: the code a story test's When calls, or the model operations a
    markdown When's realization names. The fidelity goes by what the story holds, never by its format: a story whose
    steps have bodies is at acceptance tests, and the read records what each step's calls reach (its calls_reach fact,
    cdd_guidance/practices/stories/model/graph_reading.py): a When that calls nothing, or only the story test's own
    helpers and seeds, fails; one whose calls name code the graph has not read is left unjudged. A story at scenarios is
    asked only of a When with a realization, once a model is read beside it (its realization_reach fact,
    cdd_guidance/practices/stories/model/realization_links.py): a realization that names no operation of the model the
    step's domain terms link to fails; a When with no realization calls nothing yet and is left out."""

    slug = "code-steps-invoke-code"
    node_types = ("When",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not node.is_read_at(ACCEPTANCE_TESTS_FIDELITY):
            return self._check_realization(node)
        reach = node.get_fact("calls_reach")
        if reach == CALLS_REACH_NONE:
            return [Finding(node, f"When {node.name!r} calls nothing: call the domain operation it tests in the step.")]
        if reach == CALLS_REACH_TEST:
            return [Finding(node, f"When {node.name!r} calls only the story test's own helpers or seeds: call the domain operation it tests in the step.")]
        return []

    def _check_realization(self, node: Node) -> list[Finding]:
        if node.get_fact(REALIZATION_REACH_FACT) != REALIZATION_REACHES_NONE:
            return []
        return [Finding(node, (
            f"When {node.name!r} has a realization that names no operation of the model its domain terms link to: link the "
            "step's domain terms to the classes the realization calls, and name in the realization an operation the model "
            "declares."
        ))]
