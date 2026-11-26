"""Heavy mamba spec: a small LERN project's story canvas rendered in one call, for real. The LERN pattern bundles the
project's shared story with esbuild through its story runtime, the story's prototype screen is written beside the
explorer, the canvas is rendered into the working version, and the walk renders the screen in Node at each step group."""

import json
import os
import shutil
import tempfile
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.patterns.lern_domain_driven.lern_domain_driven import LernDomainDriven
from cdd_guidance.patterns.lern_domain_driven.practices.stories.model.claude_design.story_runtime import StoryRuntimeContract
from cdd_guidance.practices.ux.model.claude_design.canvas_explorer import CanvasExplorer
from cdd_guidance.practices.ux.model.claude_design.project_story_canvas import ProjectStoryCanvas
from cdd_guidance.practices.ux.model.claude_design.story_screen import StoryScreen, WrittenMarkup
from cdd_guidance.practices.ux.model.claude_design.borrowed_node_modules import node_modules_with_esbuild

_REPO = Path(__file__).resolve().parents[5]
# An esbuild the repository already installs for one of its apps; the throwaway project borrows its node_modules.
_NODE_MODULES = node_modules_with_esbuild(_REPO)

STORY_MAP = """# (E) Place Order
## (S) Customer --> [Order Plan](../story_tests/place-order/order-plan/order_plan_story.test.md#story-order-plan)
"""

SCENARIOS = """# Story: Order Plan

#### Scenario: Customer orders the Ace plan

*Given* the "Ace" plan is in the catalog
*When* the **Customer** orders the "Ace" plan
*Then* the order holds the "Ace" plan
"""

REPOSITORIES = """
const plans: Array<{ name: string }> = [];
export const planRepository = {
  save(plan: { name: string }) { plans.push(plan); },
  all() { return [...plans]; },
  _reset() { plans.length = 0; },
};
export function domainRepositories() { return { planRepository }; }
"""

SHARED_STORY = """
import { ctx, scenario, shareStory, setStoryBinding } from '../../../test-utils/story-test/story-test';

shareStory('Order Plan', () => {
  scenario('Customer orders the Ace plan', ({ given, when, then }) => {
    given('the "Ace" plan is in the catalog', () => { (ctx.planRepository as any).save({ name: 'Ace' }); });
    when('the Customer orders the "Ace" plan', () => { setStoryBinding('order', { plan: 'Ace' }); });
    then('the order holds the "Ace" plan', () => {});
  });
});
"""

UX_MAP = {"name": "Shop screens", "screens": [
    {"name": "order-plan", "slug": "order-plan", "story_names": ["Order Plan"], "image": "", "prototype": ""}]}


def link_folder(link: Path, target: Path) -> None:
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


def write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


with description("a LERN project's story canvas rendered in one call, for real") as self:
    with before.all:
        self.folder = tempfile.mkdtemp(prefix="cdd-story-canvas-")
        root = Path(self.folder)
        link_folder(root / "node_modules", _NODE_MODULES)
        write(root, "tsconfig.json", json.dumps({"compilerOptions": {"target": "es2020", "module": "esnext"}}))
        write(root, "test-utils/story-test/story-test.ts", StoryRuntimeContract.template().read_text(encoding="utf-8"))
        write(root, "test-utils/story-test/repositories.ts", REPOSITORIES)
        write(root, "tests/story_tests/place-order/order-plan.story.shared.ts", SHARED_STORY)
        write(root, "tests/.context/story-map.md", STORY_MAP)
        write(root, "tests/story_tests/place-order/order-plan/order_plan_story.test.md", SCENARIOS)
        write(root, "ux/ux.json", json.dumps(UX_MAP, indent=2))
        screen = StoryScreen(title="Order Plan", story="Order Plan",
                             markup=WrittenMarkup(head="", body="<main><p>Plan {{ order.plan }}</p></main>"), positions={"Customer orders the Ace plan": [{"page": "plans"}, {"page": "order"}]})
        canvas = ProjectStoryCanvas(project_root=root, ux_root=root / "ux", stories_root=root / "tests" / ".context",
                                    fixtures=LernDomainDriven().canvas_fixtures(root))
        self.rendered = canvas.render({"order-plan": screen})
        self.project = self.rendered.version.folder / "project"

    with after.all:
        # Remove the link first, so the cleanup never reaches into the repository's own node_modules.
        link = Path(self.folder) / "node_modules"
        if os.name == "nt":
            os.rmdir(link)
        else:
            os.unlink(link)
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("a story map with one story, one scenario and one screen"):
        with it("should bundle the project's shared story into the version's fixtures"):
            bundle = (self.project / "fixtures" / "canvas-fixtures.js").read_text(encoding="utf-8")
            expect(bundle).to(contain("Customer orders the Ace plan"))

        with it("should list the scenario in the explorer as two step groups playing the story's screen"):
            scenario = next(CanvasExplorer(self.project).scenarios())
            expect((scenario.screen, len(scenario.groups))).to(equal(("order-plan", 2)))

        with it("should load the fixtures bundle in the explorer"):
            explorer = (self.project / "screens" / "explorer.dc.html").read_text(encoding="utf-8")
            expect(explorer).to(contain("../fixtures/canvas-fixtures.js"))

        with it("should walk the screen at the scenario's step groups and write the walk beside the version"):
            expect(self.rendered.walk_file.is_file()).to(be_true)
            expect(self.rendered.walk_file.read_text(encoding="utf-8")).to(contain("Customer orders the Ace plan"))
            expect(list(self.rendered.walk.misses)).to(equal([]))
