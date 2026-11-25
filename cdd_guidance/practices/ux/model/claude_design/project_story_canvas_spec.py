"""Mamba spec for one project's story canvas rendered in one call (ProjectStoryCanvas): the story map and the UX map
read from the project's roots, the fixtures bundle built, each story's prototype screen written and named on the UX
map, the canvas rendered into the working version with each story's and scenario's place in its scenario file, and the
walk written beside it; and a stop, with nothing rendered, when the fixtures cannot be built."""

import json
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error, be_false, be_true
from mamba import after, before, context, description, it

from cdd_guidance.practices.ux.model.claude_design.canvas_explorer import CanvasExplorer
from cdd_guidance.practices.ux.model.claude_design.project_story_canvas import (
    FixturesNotBuilt,
    ProjectStoryCanvas,
    ScreenNotOnUxMap,
)
from cdd_guidance.practices.ux.model.claude_design.story_screen import StoryScreen, WrittenMarkup

STORY_MAP = """# (E) Place Order
## (S) Customer --> [Order Plan](../story_tests/place-order/order-plan/order_plan_story.test.md#story-order-plan)
"""

SCENARIOS = """# Story: Order Plan

#### Scenario: Customer orders the Ace plan

*Given* the **Customer** has an empty cart
*When* the **Customer** orders the "Ace" plan
*Then* the order holds the "Ace" plan
"""

UX_MAP = {"name": "Shop screens", "screens": [
    {"name": "order-plan", "slug": "order-plan", "story_names": ["Order Plan"], "image": "", "prototype": "",
     "domain_terms": ["Order.plan"]}]}


def write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


class RecordedFixtures:
    """A fixtures builder that writes a bundle and keeps the stories it was asked for."""

    def __init__(self) -> None:
        self.stories = []

    def build(self, story_names, out_file):
        self.stories = list(story_names)
        Path(out_file).parent.mkdir(parents=True, exist_ok=True)
        Path(out_file).write_text("window.CanvasFixtures = {};\n", encoding="utf-8")
        return Path(out_file)


class RefusedFixtures:
    def build(self, story_names, out_file):
        raise RuntimeError("story-test.ts: no export storyBindings")


class NoMisses:
    misses = []

    def write(self, path):
        Path(path).write_text("# Walk\n", encoding="utf-8")
        return Path(path)


class QuietWalk:
    """A walk that renders nothing, so the unit tier stays out of Node; the heavy spec walks for real."""

    def __init__(self, version) -> None:
        self.version = version

    def walk(self, story_map):
        return NoMisses()


def order_screen() -> StoryScreen:
    return StoryScreen(title="Order Plan", story="Order Plan", markup=WrittenMarkup(head="", body="<main>{{ order.plan }}</main>"),
                       domain_input="order", positions={"Customer orders the Ace plan": [{"page": "plans"}, {"page": "order"}]})


def project_canvas(root: Path, fixtures) -> ProjectStoryCanvas:
    return ProjectStoryCanvas(project_root=root, ux_root=root / "ux", stories_root=root / "tests" / ".context",
                              fixtures=fixtures, walk_type=QuietWalk)


with description("a project's story canvas rendered in one call") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-story-canvas-"))
        write(self.root, "tests/.context/story-map.md", STORY_MAP)
        write(self.root, "tests/story_tests/place-order/order-plan/order_plan_story.test.md", SCENARIOS)
        write(self.root, "ux/ux.json", json.dumps(UX_MAP, indent=2))

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("when the fixtures build"):
        with before.each:
            self.fixtures = RecordedFixtures()
            self.rendered = project_canvas(self.root, self.fixtures).render({"order-plan": order_screen()})
            self.project = self.rendered.version.folder / "project"

        with it("should render into the working version of the UX root's design canvas"):
            expect(self.rendered.version.folder).to(equal(self.root / "ux" / "design-canvas" / "version-1"))
            expect((self.project / "canvas.json").is_file()).to(be_true)

        with it("should build the fixtures bundle for every story on the map"):
            expect(self.fixtures.stories).to(equal(["Order Plan"]))
            expect((self.project / "fixtures" / "canvas-fixtures.js").is_file()).to(be_true)

        with it("should write each story's prototype screen and name it on the UX map, keeping the map's other fields"):
            expect((self.project / "screens" / "order-plan.dc.html").read_text(encoding="utf-8")).to(contain("{{ order.plan }}"))
            screen = json.loads((self.root / "ux" / "ux.json").read_text(encoding="utf-8"))["screens"][0]
            expect(screen["prototype"]).to(equal("screens/order-plan.dc.html"))
            expect(screen["domain_terms"]).to(equal(["Order.plan"]))

        with it("should list the scenario in the explorer as one step group per action, playing the story's screen"):
            scenario = next(CanvasExplorer(self.project).scenarios())
            expect(scenario.screen).to(equal("order-plan"))
            expect(len(scenario.groups)).to(equal(2))

        with it("should give the explorer each story's and scenario's place in its scenario file"):
            explorer = (self.project / "screens" / "explorer.dc.html").read_text(encoding="utf-8")
            scenario_file = (self.root / "tests/story_tests/place-order/order-plan/order_plan_story.test.md").as_posix()
            expect(explorer.replace("\\\\", "/").replace("\\/", "/")).to(contain(f"{scenario_file}:1"))
            expect(explorer.replace("\\\\", "/").replace("\\/", "/")).to(contain(f"{scenario_file}:3"))

        with it("should write the walk of the screens into the version's folder"):
            expect(self.rendered.walk_file).to(equal(self.rendered.version.folder / "walk.md"))
            expect(self.rendered.walk_file.is_file()).to(be_true)

    with context("when the fixtures cannot be built"):
        with before.each:
            self.canvas = project_canvas(self.root, RefusedFixtures())

        with it("should stop with FixturesNotBuilt, saying what failed"):
            expect(lambda: self.canvas.render({"order-plan": order_screen()})).to(
                raise_error(FixturesNotBuilt, contain("story-test.ts: no export storyBindings")))

        with it("should render no canvas and write no screen"):
            try:
                self.canvas.render({"order-plan": order_screen()})
            except FixturesNotBuilt:
                pass
            project = self.root / "ux" / "design-canvas" / "version-1" / "project"
            expect((project / "canvas.json").exists()).to(be_false)
            expect((project / "screens" / "order-plan.dc.html").exists()).to(be_false)

    with context("when a screen is for a slug the UX map does not hold"):
        with it("should stop with ScreenNotOnUxMap, naming the slug"):
            expect(lambda: project_canvas(self.root, RecordedFixtures()).render({"check-out": order_screen()})).to(
                raise_error(ScreenNotOnUxMap, contain("check-out")))
