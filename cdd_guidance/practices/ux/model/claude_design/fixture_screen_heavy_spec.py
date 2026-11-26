"""Mamba spec for a fixture-driven screen artboard's script, parsed as JavaScript. Heavy: runs Node."""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.ux.model.claude_design.fixture_screen import FixtureScreen, ScenarioSource


with description("a fixture-driven screen") as self:
    with before.all:
        self.html = FixtureScreen(
            title="Select plan",
            head="",
            root_class="plans",
            body="<main></main>",
            source=ScenarioSource("Select Plan", "Pick the cheapest plan", "/plans"),
            own_methods="fromFixture(repositories) { return {}; }\n",
            vals="plan: st.plan",
            artboard="/screens/select-plan.dc.html",
        ).html
        self.script = re.search(r"data-dc-script[^>]*>(.*)</script>", self.html, re.S).group(1)

    with context("with its script read as JavaScript"):
        with it("should parse"):
            script = Path(tempfile.mkdtemp()) / "screen.js"
            script.write_text("class DCLogic {}\n" + self.script, encoding="utf-8")
            checked = subprocess.run([shutil.which("node") or "node", "--check", str(script)], capture_output=True, text=True)
            expect(checked.stderr).to(equal(""))

    with context("inside the story explorer, on a step group past the scenario's first action"):
        with it("should load the fixture through that action and hand the screen what the scenario bound"):
            run = """
const loaded = [];
globalThis.CanvasFixtures = {
  actions: () => 2,
  load: (story, scenario, actions) => { loaded.push([story, scenario, actions]); return Promise.resolve({}); },
  bindings: () => ({ cart: 'the cart after one action' }),
  examples: {}, scenarios: () => [], pasteFor: () => null,
};
class DCLogic { constructor() { this.props = {}; this.state = null; } setState(next) { this.state = Object.assign({}, this.state || {}, next); } forceUpdate() {} }
const Component = new Function('DCLogic', SCRIPT + '; return Component;')(DCLogic);
const screen = new Component();
screen.fromFixture = (repositories, scenario, examples, step, bindings) => ({ plan: bindings.cart });
screen.props = { story: 'Add Line To Cart', scenario: 'Add one more line', step: 'Then the cart holds Atlas and Ace', stepIndex: 1 };
screen.loadFromFixture();
setTimeout(() => console.log(JSON.stringify({ loaded, plan: screen.state.plan })), 10);
"""
            node = subprocess.run([shutil.which("node") or "node", "-e", run.replace("SCRIPT", repr(self.script))], capture_output=True, text=True, check=True)
            expect(node.stdout.strip()).to(equal('{"loaded":[["Add Line To Cart","Add one more line",1]],"plan":"the cart after one action"}'))
