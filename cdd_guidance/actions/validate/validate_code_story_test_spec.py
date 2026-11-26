"""A validate that names only a story test in code, where markdown writes the same story's scenarios: the scenarios the
two merge belong to the markdown file and are written again in the story test (``Node.written_at``), so the graph rules
run on them for the story test too, in Python and TypeScript, beside one markdown file per story or a sub-epic's file."""

import re
import shutil
import tempfile
from pathlib import Path

from expects import contain, expect, equal
from mamba import after, before, description, it

from harness.graph.saved_graph import SavedGraph
from space.session.spec_support.throwaway_project import ThrowawayProject
from cdd_guidance.actions.validate.validate import Validate
from cdd_guidance.actions.validate.validate_examples import working_in
from cdd_guidance.practices.stories.model.fixtures.scenario_layouts import (
    MARKDOWN_BESIDE_PYTHON,
    MARKDOWN_BESIDE_TYPESCRIPT,
    ONE_STORY_PER_FILE_BESIDE_PYTHON,
    PYTHON_STORY_TEST,
    SUB_EPIC_FILE,
    SUB_EPIC_FILE_BESIDE_TYPESCRIPT,
    TYPESCRIPT_STORY_TEST,
)
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue

_NOTHING_READ = "No graph rule ran on"
# Pay by card in the sub-epic's markdown file with its Given written as a code identifier, which plain-english-gwt-steps reports.
_GIVEN_AS_IDENTIFIER = {**MARKDOWN_BESIDE_PYTHON, SUB_EPIC_FILE: MARKDOWN_BESIDE_PYTHON[SUB_EPIC_FILE].replace("*Given* a cart\n", "*Given* shoppingCart\n", 1)}
# The line of a report naming the graph it checked.
_GRAPH_SOURCE = re.compile(r"^- `(.+graph\.json)`$", re.MULTILINE)


class _ValidatedStoryTest:
    """A project written in one layout, and the report of a validate of the Stories scenarios that names only its story
    test in code."""

    def __init__(self, files: dict[str, str], story_test: str, rule: str = "and-chaining") -> None:
        self._project = ThrowawayProject()
        self._folder = Path(tempfile.mkdtemp(prefix="cdd-layout-"))
        for name, text in files.items():
            (self._folder / name).parent.mkdir(parents=True, exist_ok=True)
            (self._folder / name).write_text(text, encoding="utf-8")
        action = Validate(session=working_in(self._project, self._folder, self._folder))
        self.report = str(action.validate(guidance=["stories-scenarios"], paths=[story_test], graph=True, rule=rule))
        self.checked = SavedGraph.from_file(Path(_GRAPH_SOURCE.search(self.report).group(1)))

    def scenarios(self) -> list[str]:
        return sorted(node.name for node in self.checked.practices["stories"].nodes if node.type == "Scenario")

    def close(self) -> None:
        self._project.close()
        shutil.rmtree(self._folder, ignore_errors=True)


with description("a validate that names only a story test in code, beside markdown writing the same story") as self:
    with before.all:
        self.validated = {
            "Python beside a sub-epic's file": _ValidatedStoryTest(MARKDOWN_BESIDE_PYTHON, PYTHON_STORY_TEST),
            "Python beside one file per story": _ValidatedStoryTest(ONE_STORY_PER_FILE_BESIDE_PYTHON, PYTHON_STORY_TEST),
            "TypeScript beside one file per story": _ValidatedStoryTest(MARKDOWN_BESIDE_TYPESCRIPT, TYPESCRIPT_STORY_TEST),
            "TypeScript beside a sub-epic's file": _ValidatedStoryTest(SUB_EPIC_FILE_BESIDE_TYPESCRIPT, TYPESCRIPT_STORY_TEST),
        }
        self.given_as_identifier = _ValidatedStoryTest(_GIVEN_AS_IDENTIFIER, PYTHON_STORY_TEST, "plain-english-gwt-steps")

    with after.all:
        for validated in [*self.validated.values(), self.given_as_identifier]:
            validated.close()

    with it("should run the graph rules on a Python story test beside a sub-epic's markdown file"):
        expect(self.validated["Python beside a sub-epic's file"].report).not_to(contain(_NOTHING_READ))

    with it("should run the graph rules on a Python story test beside one markdown file per story"):
        expect(self.validated["Python beside one file per story"].report).not_to(contain(_NOTHING_READ))

    with it("should run the graph rules on a TypeScript story test beside one markdown file per story"):
        expect(self.validated["TypeScript beside one file per story"].report).not_to(contain(_NOTHING_READ))

    with it("should run the graph rules on a TypeScript story test beside a sub-epic's markdown file"):
        expect(self.validated["TypeScript beside a sub-epic's file"].report).not_to(contain(_NOTHING_READ))

    with it("should check every scenario the story test writes, the merged one and the one only it writes, in each layout"):
        scenarios = {layout: validated.scenarios() for layout, validated in self.validated.items()}
        expect(scenarios).to(equal({layout: ["Pay by card", "Pay with a voucher"] for layout in self.validated}))

    with it("should report a rule a merged scenario breaks in its markdown, to a validate of the story test alone"):
        expect(self.given_as_identifier.report).to(contain("**ERROR** **[graph rule]**"))
