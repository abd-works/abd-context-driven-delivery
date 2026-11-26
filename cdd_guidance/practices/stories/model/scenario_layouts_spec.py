"""The same two stories written in every layout a project keeps its scenarios in: one markdown file per story, one
markdown file per sub-epic holding several stories, the story map alone, code alone in Python or TypeScript, and
markdown beside a story test in Python or TypeScript. Each layout gives the graph the same stories, scenarios and steps.
Where markdown and code both write a story, they merge: the markdown gives each scenario and its steps, the code gives
their bodies, and a scenario only the code writes is added; no scenario of the markdown is lost to the code."""

import tempfile
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import after, before, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices a graph holds
from harness.graph.graph import Graph
from harness.graph.saved_graph import SavedGraph

from cdd_guidance.practices.stories.model.fixtures.scenario_layouts import (
    CANCEL_FILE,
    MAP,
    MAP_LISTING_SCENARIOS,
    MARKDOWN_BESIDE_PYTHON,
    MARKDOWN_BESIDE_PYTHON_IN_OTHER_WORDS,
    MARKDOWN_BESIDE_TYPESCRIPT,
    ONE_STORY_PER_FILE,
    ONLY_IN_CODE,
    PAY_FILE,
    PYTHON_ONLY,
    STORIES,
    SUB_EPIC_FILE,
    SUB_EPIC_FILE_HOLDING_BOTH,
    TYPESCRIPT_ONLY,
)
from cdd_guidance.practices.ux.model.claude_design.project_story_canvas import NoCanvasFixtures, ProjectStoryCanvas

class _Layout:
    """One project written in a layout, read into a graph as a session's graph reads it."""

    def __init__(self, files: dict[str, str]) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.root = Path(self._folder.name)
        (self.root / ".git").mkdir()
        for name, text in files.items():
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_text(text, encoding="utf-8")
        self.graph = Graph()
        self.graph.load_working_copy(str(self.root), {"stories": "."}, force=True)

    def scenarios(self) -> list[tuple]:
        """Each story's scenarios, in the order the map gives them, each with its steps' names."""
        held = []
        for story in self._stories.nodes("Story"):
            for scenario in self._children("scenarios", story):
                held.append((story.name, scenario.name, [step.name for step in self._steps(scenario)]))
        return held

    def scenario_names(self) -> list[tuple]:
        return [(story, scenario) for story, scenario, _steps in self.scenarios()]

    def file_of(self, scenario_name: str) -> str:
        return next(node.source.file for node in self._stories.nodes("Scenario") if node.name == scenario_name)

    def step_has_a_body(self, step_name: str) -> bool:
        return any(bool(node.get_fact("body_text")) for node in self._stories.nodes() if node.name == step_name)

    def checked(self, file: str) -> list[str]:
        """The scenarios a validate of file is given: the nodes a refresh of the session's graph reads from it."""
        checked = self.root / "checked.json"
        self.graph.reads.refreshed([file], checked)
        return [node.name for node in SavedGraph.from_file(checked).practices["stories"].nodes if node.type == "Scenario"]

    def drawn(self) -> list[tuple]:
        """Each story's scenarios as the story explorer draws them, each with its steps' text."""
        story_map = ProjectStoryCanvas(self.root, self.root / "ux", self.root, NoCanvasFixtures([])).story_map()
        return [
            (story.name, scenario.name, [f"{step.keyword.lower()} {step.text}" for step in scenario.steps])
            for story in story_map.descendants.stories()
            for scenario in story.scenarios
        ]

    def close(self) -> None:
        self._folder.cleanup()

    @property
    def _stories(self):
        return self.graph.practices.named("stories").reading.in_graph

    def _children(self, edge: str, parent) -> list:
        return [found.child for found in self.graph.edges.from_parent(edge, parent)]

    def _steps(self, parent) -> list:
        steps = []
        for step in self._children("steps", parent):
            steps += [step, *self._steps_chained(step)]
        return steps

    def _steps_chained(self, step) -> list:
        chained = []
        for continued in self._children("ands", step):
            chained += [continued, *self._steps_chained(continued)]
        return chained


with description("two stories written in every layout a project keeps its scenarios in") as self:
    with before.all:
        self.layouts = {
            "one story per file": _Layout(ONE_STORY_PER_FILE),
            "a sub-epic file": _Layout(SUB_EPIC_FILE_HOLDING_BOTH),
            "the story map alone": _Layout({MAP: MAP_LISTING_SCENARIOS}),
            "Python alone": _Layout(PYTHON_ONLY),
            "TypeScript alone": _Layout(TYPESCRIPT_ONLY),
            "markdown beside Python": _Layout(MARKDOWN_BESIDE_PYTHON),
            "markdown beside TypeScript": _Layout(MARKDOWN_BESIDE_TYPESCRIPT),
            "markdown beside Python in other words": _Layout(MARKDOWN_BESIDE_PYTHON_IN_OTHER_WORDS),
        }

    with after.all:
        for layout in self.layouts.values():
            layout.close()

    with it("should read each story, scenario and step from one markdown file per story"):
        expect(self.layouts["one story per file"].scenarios()).to(equal(STORIES))

    with it("should read each story, scenario and step from a sub-epic's markdown file holding both stories"):
        expect(self.layouts["a sub-epic file"].scenarios()).to(equal(STORIES))

    with it("should read each story and the scenarios the story map lists under it, from the story map alone"):
        expect(self.layouts["the story map alone"].scenario_names()).to(equal([(story, scenario) for story, scenario, _steps in STORIES]))

    with it("should read each story, scenario and step from story tests in Python alone"):
        expect(self.layouts["Python alone"].scenarios()).to(equal(STORIES))

    with it("should read each story, scenario and step from story tests in TypeScript alone"):
        expect(self.layouts["TypeScript alone"].scenarios()).to(equal(STORIES))

    with it("should keep every scenario and step of markdown beside Python, and add the scenario only Python writes"):
        expect(self.layouts["markdown beside Python"].scenarios()).to(equal([STORIES[0], ONLY_IN_CODE, STORIES[1]]))

    with it("should keep every scenario and step of markdown beside TypeScript, and add the scenario only TypeScript writes"):
        expect(self.layouts["markdown beside TypeScript"].scenarios()).to(equal([STORIES[0], ONLY_IN_CODE, STORIES[1]]))

    with it("should place a scenario both write in the sub-epic's markdown file"):
        expect(self.layouts["markdown beside Python"].file_of("Pay by card")).to(equal(SUB_EPIC_FILE))

    with it("should place a scenario both write in the story's own markdown file"):
        expect(self.layouts["markdown beside TypeScript"].file_of("Pay by card")).to(equal(PAY_FILE))

    with it("should give a markdown step the body Python gives the same step"):
        expect(self.layouts["markdown beside Python"].step_has_a_body("when the Shopper pays by card")).to(be_true)

    with it("should give a markdown step the body TypeScript gives the same step"):
        expect(self.layouts["markdown beside TypeScript"].step_has_a_body("when the Shopper pays by card")).to(be_true)

    with it("should give a markdown step the body of the code step of its kind at its place, when code words it otherwise and chains one line more"):
        expect(self.layouts["markdown beside Python in other words"].step_has_a_body("given a cart")).to(be_true)

    with it("should give a validate of the sub-epic's markdown file every scenario it writes, beside Python"):
        expect(self.layouts["markdown beside Python"].checked(SUB_EPIC_FILE)).to(contain("Pay by card", "Cancel an open order"))

    with it("should give a validate of a story's own markdown file its scenario, beside TypeScript"):
        expect(self.layouts["markdown beside TypeScript"].checked(PAY_FILE)).to(equal(["Pay by card"]))

    with it("should draw in the story explorer the stories, scenarios and steps the graph reads, in every layout that writes steps"):
        drawn = {name: layout.drawn() for name, layout in self.layouts.items() if name != "the story map alone"}
        read = {name: layout.scenarios() for name, layout in self.layouts.items() if name != "the story map alone"}
        expect(drawn).to(equal(read))
