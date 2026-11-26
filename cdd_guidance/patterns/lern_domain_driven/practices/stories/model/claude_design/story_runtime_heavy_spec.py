"""Heavy mamba spec: the story runtime the LERN pattern ships, bundled for real with esbuild into canvas fixtures and
run in Node, replays a scenario's Givens and its first action and hands a screen what the steps bound."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from mamba import description, context, it, before, after
from expects import equal, expect

from cdd_guidance.patterns.lern_domain_driven.practices.stories.model.claude_design.fixtures import LernCanvasFixtures
from cdd_guidance.patterns.lern_domain_driven.practices.stories.model.claude_design.story_runtime import StoryRuntimeContract

_REPO = Path(__file__).resolve().parents[7]
# An esbuild the repository already installs for one of its apps; the throwaway workspace borrows its node_modules.
_NODE_MODULES = next(path for path in (_REPO / "harness" / "graph" / "app" / "node_modules",
                                       _REPO / "cdd_guidance" / "practices" / "stories" / "app" / "node_modules")
                     if (path / "esbuild").is_dir())

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
import { ctx, scenario, shareStory } from '../../test-utils/story-test/story-test';

shareStory('Place Order', () => {
  scenario('Customer places an order', ({ given, when, then }) => {
    given('the Ace plan is in the catalog', () => { (ctx.planRepository as any).save({ name: 'Ace' }); });
    when('the customer orders the Ace plan', () => { ctx.order = { plan: 'Ace' }; });
    then('the order holds the Ace plan', () => {});
  });
  scenario('Customer registers credentials', ({ when, then }) => {
    when('the customer registers valid credentials', () => { ctx.registered = ctx.credentials; },
      () => ({ credentials: { email: 'sam@example.com' } }));
    then('the credentials are registered', () => {});
  });
});
"""

RUN_BUNDLE = """
const fs = require('fs');
const vm = require('vm');
const sandbox = { console };
vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), sandbox);
const fixtures = sandbox.CanvasFixtures;
(async () => {
  const story = 'Place Order';
  const scenario = 'Customer places an order';
  const before = (await fixtures.load(story, scenario, 0)).planRepository.all();
  const beforeOrder = fixtures.bindings().order ?? null;
  const after = (await fixtures.load(story, scenario, 1)).planRepository.all();
  const afterOrder = fixtures.bindings().order;
  await fixtures.load(story, 'Customer registers credentials', 0);
  const entered = { credentials: fixtures.bindings().credentials ?? null, registered: fixtures.bindings().registered ?? null };
  await fixtures.load(story, 'Customer registers credentials', 1);
  const applied = fixtures.bindings().registered ?? null;
  console.log(JSON.stringify({ scenarios: fixtures.scenarios(story), actions: fixtures.actions(story, scenario),
    before, beforeOrder, after, afterOrder, entered, applied }));
})();
"""


def link_folder(link: Path, target: Path) -> None:
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)


def write(root: Path, path: str, text: str) -> None:
    (root / path).parent.mkdir(parents=True, exist_ok=True)
    (root / path).write_text(text, encoding="utf-8")


with description("the LERN story runtime bundled into canvas fixtures") as self:
    with before.all:
        self.folder = tempfile.mkdtemp()
        root = Path(self.folder)
        link_folder(root / "node_modules", _NODE_MODULES)
        write(root, "tsconfig.json", json.dumps({"compilerOptions": {"target": "es2020", "module": "esnext"}}))
        write(root, "test-utils/story-test/story-test.ts", StoryRuntimeContract.template().read_text(encoding="utf-8"))
        write(root, "test-utils/story-test/repositories.ts", REPOSITORIES)
        write(root, "tests/order/order.story.shared.ts", SHARED_STORY)
        bundle = LernCanvasFixtures(root).build(["Place Order"], root / "out" / "canvas-fixtures.js")
        run = subprocess.run(["node", "-e", RUN_BUNDLE, str(bundle)], capture_output=True, text=True, check=True)
        self.result = json.loads(run.stdout.strip().splitlines()[-1])

    with after.all:
        # Remove the link first, so the cleanup never reaches into the repository's own node_modules.
        link = Path(self.folder) / "node_modules"
        if os.name == "nt":
            os.rmdir(link)
        else:
            os.unlink(link)
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("a scenario with one Given and one When"):
        with it("lists the scenario and its one action"):
            expect(self.result["scenarios"]).to(equal(["Customer places an order", "Customer registers credentials"]))
            expect(self.result["actions"]).to(equal(1))

        with it("replays the Givens alone before the action"):
            expect(self.result["before"]).to(equal([{"name": "Ace"}]))
            expect(self.result["beforeOrder"]).to(equal(None))

        with it("replays the action on fresh repositories and hands the screen what it bound"):
            expect(self.result["after"]).to(equal([{"name": "Ace"}]))
            expect(self.result["afterOrder"]).to(equal({"plan": "Ace"}))

    with context("a When that names what the Customer enters"):
        with it("binds what it enters before the When runs, so the When's screen shows it"):
            expect(self.result["entered"]).to(equal({"credentials": {"email": "sam@example.com"}, "registered": None}))

        with it("binds it again when the When runs, so its action applies it"):
            expect(self.result["applied"]).to(equal({"email": "sam@example.com"}))
