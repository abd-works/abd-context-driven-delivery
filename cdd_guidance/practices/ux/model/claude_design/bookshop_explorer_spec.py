"""Mamba spec for the story explorer drawn from the bookshop fixture, whose scenarios are written in every code layout:
story tests in Python and TypeScript, a shared story file in each, and a screen spec. Each row the explorer lists offers
a request to open the file that writes it (``f``, ``path:line``): a scenario at the line of its own call, a story at the
line that names it, so a scenario two files write is opened in each file's own."""

import json
import tempfile
from pathlib import Path

from expects import be_above, equal, expect
from mamba import before, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices a story map is read with
from cdd_guidance.practices.ux.model.claude_design.canvas_explorer import EXPLORER_FILE, CanvasExplorer
from cdd_guidance.practices.ux.model.claude_design.project_story_canvas import NoCanvasFixtures, ProjectStoryCanvas
from cdd_guidance.practices.ux.model.claude_design.story_canvas import ClaudeDesignStoryMap, StoryCanvasSetup
from cdd_guidance.practices.ux.model.json.nodes import JsonUxMap

_PROJECT = Path(__file__).resolve().parents[3] / "stories" / "model" / "fixtures" / "bookshop"
_CONFIRM_ORDER = "story_tests/check-out/confirm-order"


def _drawn_tree() -> list:
    """The explorer's tree as the story canvas draws it from the bookshop's story map and story tests."""
    canvas = ProjectStoryCanvas(_PROJECT, _PROJECT / "ux", _PROJECT, NoCanvasFixtures([]))
    story_map = canvas.story_map()
    setup = StoryCanvasSetup(ux_map=JsonUxMap().parse({"screens": []}), sources=canvas.sources(story_map), files_root=_PROJECT)
    page = json.loads(ClaudeDesignStoryMap(setup=setup).render(story_map))[f"project/{EXPLORER_FILE}"]
    with tempfile.TemporaryDirectory() as folder:
        written = Path(folder) / EXPLORER_FILE
        written.parent.mkdir(parents=True)
        written.write_text(page, encoding="utf-8")
        return CanvasExplorer(Path(folder)).tree()


def _stories(epics: list) -> list:
    return [story for epic in epics for story in [*epic["s"], *_stories(epic["e"])]]


def _place(row: dict) -> tuple:
    """The file a row's open request names, from the project's root, and its line."""
    file, line = row["f"].rsplit(":", 1)
    return Path(file).resolve().relative_to(_PROJECT.resolve()).as_posix(), int(line)


def _line_of(file: str, line: int) -> str:
    return (_PROJECT / file).read_text(encoding="utf-8").splitlines()[line - 1]


with description("the story explorer drawn from the bookshop's story tests in code") as self:
    with before.all:
        self.stories = {story["n"]: story for story in _stories(_drawn_tree())}
        self.code_scenarios = [(scenario, _place(scenario)) for story in self.stories.values() for scenario in story["c"]
                               if not scenario["b"] and not _place(scenario)[0].endswith(".md")]

    with it("should open every scenario a story test in code writes at a line of its file"):
        expect(min(line for _scenario, (_file, line) in self.code_scenarios)).to(be_above(0))

    with it("should open every scenario a story test in code writes at the line of its own call"):
        misplaced = [(scenario["n"], file, line) for scenario, (file, line) in self.code_scenarios if scenario["n"] not in _line_of(file, line)]
        expect(misplaced).to(equal([]))

    with it("should open each of the two rows of a scenario a shared story file and its screen spec write in its own file"):
        rows = [_place(scenario)[0] for scenario in self.stories["Cancel Order"]["c"] if scenario["n"] == "Cancel a submitted order"]
        expect(sorted(rows)).to(equal([f"{_CONFIRM_ORDER}/confirm-order.story.shared.ts", f"{_CONFIRM_ORDER}/confirm-order.story.ui.spec.ts"]))

    with it("should open a story at the line of the story test that names it"):
        file, line = _place(self.stories["View Order Confirmation"])
        expect((file, "View Order Confirmation" in _line_of(file, line))).to(
            equal((f"{_CONFIRM_ORDER}/view-order-confirmation/view_order_confirmation_story.test.ts", True)))

    with it("should open a story a shared story file writes at its story call"):
        file, line = _place(self.stories["Cancel Order"])
        expect(_line_of(file, line).strip()).to(equal('story("Cancel Order", () => {'))
