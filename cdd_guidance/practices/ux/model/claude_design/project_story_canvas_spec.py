"""Mamba spec for one project's story canvas rendered in one call (ProjectStoryCanvas): the story map and the UX map
read from the project's roots, the fixtures bundle built, each story's prototype screen written and named on the UX
map, the canvas rendered into the working version with each story's and scenario's place in its scenario file, and the
walk written beside it; and a stop, with nothing rendered, when the fixtures cannot be built."""

import io
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
from cdd_guidance.practices.ux.model.claude_design.screen_files import ScreenFiles
from cdd_guidance.practices.ux.model.claude_design.story_screen import PortedCanvasMarkup, StoryScreen, WrittenMarkup

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
    differences = []

    def write(self, path):
        Path(path).write_text("# Walk\n", encoding="utf-8")
        return Path(path)


class QuietWalk:
    """A walk that renders nothing, so the unit tier stays out of Node; the heavy spec walks for real."""

    def __init__(self, version) -> None:
        self.version = version

    def walk(self, story_map, beside=None):
        return NoMisses()


def order_screen() -> StoryScreen:
    return StoryScreen(title="Order Plan", story="Order Plan", markup=WrittenMarkup(head="", body="<main>{{ order.plan }}</main>"),
                       positions={"Customer orders the Ace plan": [{"page": "plans"}, {"page": "order"}]})


class MinusSignMissed:
    misses = ["Then the cart reads \u2212$5.00"]
    differences = []

    def write(self, path):
        Path(path).write_text("# Walk\n", encoding="utf-8")
        return Path(path)


class MinusSignWalk(QuietWalk):
    def walk(self, story_map, beside=None):
        return MinusSignMissed()


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

        with it("should draw every screen in the canvas's one theme, named once"):
            canvas = ProjectStoryCanvas(project_root=self.root, ux_root=self.root / "ux", stories_root=self.root / "tests" / ".context",
                                        fixtures=RecordedFixtures(), walk_type=QuietWalk, theme="dark")
            project = canvas.render({"order-plan": order_screen()}).version.folder / "project"
            expect((project / "screens" / "order-plan.dc.html").read_text(encoding="utf-8")).to(contain('<div class="canvas-screen" data-theme="dark"'))

        with it("should hand the walk the prototype a production view stands beside, by the screen's slug"):
            handed = {}

            class BesideWalk(QuietWalk):
                def walk(self, story_map, beside=None):
                    handed.update(beside or {})
                    return NoMisses()

            prototype = StoryScreen(title="Order Plan", story="Order Plan", markup=WrittenMarkup(head="", body="<main>prototype</main>"), positions={})
            production = StoryScreen(title="Order Plan", story="Order Plan", markup=WrittenMarkup(head="", body="<main>production</main>"), positions={},
                                     beside=prototype)
            ProjectStoryCanvas(project_root=self.root, ux_root=self.root / "ux", stories_root=self.root / "tests" / ".context",
                               fixtures=RecordedFixtures(), walk_type=BesideWalk).render({"order-plan": production})
            expect((list(handed), "<main>prototype</main>" in handed["order-plan"])).to(equal((["order-plan"], True)))

        with it("should say to publish it titled exactly as the canvas and its version are named, ux-mockup.version-1"):
            expect(self.rendered.summary()).to(contain("titled exactly 'ux-mockup.version-1'"))

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

    with context("when a screen is ported from another canvas that names the files it needs"):
        with before.each:
            write(self.root, "ux/prototype/Main.dc.html", '<head><script src="./vendor/react.js"></script>\n<script src="domain.js"></script></head>')
            write(self.root, "ux/prototype/domain.js", "window.Domain = {};")
            files = ScreenFiles(component=self.root / "ux/prototype/Main.dc.html", needs={"domain.js": self.root / "ux/prototype/domain.js"},
                                dropped=(r"vendor/",))
            ported = StoryScreen(title="Order Plan", story="Order Plan", markup=PortedCanvasMarkup("flow", files=files),
                                 positions={"Customer orders the Ace plan": [{"page": "plans"}]})
            self.rendered = project_canvas(self.root, RecordedFixtures()).render({"order-plan": ported})
            self.project = self.rendered.version.folder / "project"

        with it("should copy the component beside the screens, linking the copies of what it loads"):
            component = (self.project / "screens" / "flow.dc.html").read_text(encoding="utf-8")
            expect(component).to(equal('<head><script src="../domain.js"></script></head>'))

        with it("should copy the files it loads into the version"):
            expect((self.project / "domain.js").is_file()).to(be_true)

    with context("when the canvas covers one scope"):
        with it("should say to publish it titled with the scope's name in front, ordering-ux-mockup.version-1"):
            canvas = ProjectStoryCanvas(project_root=self.root, ux_root=self.root / "ux", stories_root=self.root / "tests" / ".context",
                                        fixtures=RecordedFixtures(), scope="ordering", walk_type=QuietWalk)
            expect(canvas.render({"order-plan": order_screen()}).summary()).to(contain("titled exactly 'ordering-ux-mockup.version-1'"))

    with context("when the walk names a value a Windows console cannot print"):
        with before.each:
            canvas = ProjectStoryCanvas(project_root=self.root, ux_root=self.root / "ux", stories_root=self.root / "tests" / ".context",
                                        fixtures=RecordedFixtures(), walk_type=MinusSignWalk)
            self.rendered = canvas.render({"order-plan": order_screen()})
            self.bytes = io.BytesIO()
            self.console = io.TextIOWrapper(self.bytes, encoding="cp1252")

        with it("should print the summary to that console, writing the value as an escape"):
            self.rendered.print_summary(self.console)
            self.console.flush()
            expect(self.bytes.getvalue()).to(contain(b"Then the cart reads \\u2212$5.00"))

        with it("should keep the value as it is in the summary's text"):
            expect(self.rendered.summary()).to(contain("\u2212$5.00"))

    with context("when the project keeps one canvas and it is already published"):
        with before.each:
            write(self.root, "ux/design-canvas/versions.json", json.dumps({"keep_one": True, "version-1": "https://claude.ai/artifact/one"}))
            (self.root / "ux" / "design-canvas" / "version-1" / "project").mkdir(parents=True)
            self.rendered = project_canvas(self.root, RecordedFixtures()).render({"order-plan": order_screen()})

        with it("should render into the published version"):
            expect(self.rendered.version.folder).to(equal(self.root / "ux" / "design-canvas" / "version-1"))

        with it("should say to publish it again at the link it already has"):
            expect(self.rendered.summary()).to(contain("https://claude.ai/artifact/one"))

        with it("should say to read the live canvas.json for people's edits first"):
            expect(self.rendered.summary()).to(contain("first read that canvas's live canvas.json for edits people made there"))

        with context("rendered again after that publish, with one screen changed"):
            with before.each:
                self.rendered.version.publish_at("https://claude.ai/artifact/one", NoMisses())
                changed = StoryScreen(title="Order Plan", story="Order Plan", markup=WrittenMarkup(head="", body="<main>{{ order.total }}</main>"),
                                      positions={"Customer orders the Ace plan": [{"page": "plans"}, {"page": "order"}]})
                self.again = project_canvas(self.root, RecordedFixtures()).render({"order-plan": changed})

            with it("should name exactly the files that differ from the publish, to publish those"):
                expect(self.again.changed).to(equal(["screens/order-plan.dc.html"]))
                expect(self.again.summary()).to(contain("Publish the 1 file(s) that changed since the last publish"))
                expect(self.again.summary()).to(contain("  - project/screens/order-plan.dc.html"))

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
