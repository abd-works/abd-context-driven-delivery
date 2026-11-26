"""Mamba spec for a fixture-driven screen artboard's script, parsed as JavaScript. Heavy: runs Node."""

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.ux.model.claude_design.fixture_screen import FixtureScreen, ScenarioSource


# Runs a screen's typing replay on a stand-in page: an email, a password, and a code split over three one-character
# boxes, each field's value read and written through HTMLInputElement's own value property, on a clock that runs
# without waiting. REDRAW_AT is the write after which React draws a field again (0: never).
REPLAY = """
let now = 0; const timers = [];
globalThis.setTimeout = (callback, ms) => { timers.push({ at: now + (Number(ms) || 0), callback }); return timers.length; };
globalThis.clearTimeout = (id) => { if (timers[id - 1]) timers[id - 1].callback = null; };
globalThis.window = globalThis;
window.matchMedia = (query) => ({ matches: REDUCED && query === '(prefers-reduced-motion: reduce)' });
const writes = []; const events = [];
class HTMLInputElement {}
Object.defineProperty(HTMLInputElement.prototype, 'value', { get() { return this.held; }, set(value) { this.held = value; writes.push([this.name, value]); } });
window.HTMLInputElement = HTMLInputElement;
const field = (name, value) => Object.assign(Object.create(HTMLInputElement.prototype), { name, held: value, tagName: 'INPUT', isConnected: true, dispatchEvent: () => events.push(name) });
const fields = [field('email', 'a@b.co'), field('password', 'pw12'), field('code1', '4'), field('code2', '2'), field('code3', '7')];
let screenId = null;
globalThis.document = { querySelector: (selector) => (selector === '[data-screen-id="' + screenId + '"]' ? { querySelectorAll: () => fields } : null) };
class DCLogic { constructor() { this.props = {}; this.state = null; } setState(next, done) { this.state = Object.assign({}, this.state || {}, next); if (done) done(); } forceUpdate() {} }
const Component = new Function('DCLogic', SCRIPT + '; return Component;')(DCLogic);
const screen = new Component();
screen.props = { story: 'Create Account', scenario: 'Create an account', stepIndex: 0, stepKind: KIND };
screenId = screen.screenId();
screen.replayEntries();
while (timers.some((timer) => timer.callback)) {
  const next = timers.filter((timer) => timer.callback).sort((a, b) => a.at - b.at)[0];
  const callback = next.callback; next.callback = null; now = next.at; callback();
  if (REDRAW_AT && writes.length >= REDRAW_AT && !fields[0].redrawn) { fields[0].redrawn = true; fields[0].held = 'redrawn@b.co'; }
}
console.log(JSON.stringify({ writes, events, values: fields.map((f) => f.held), took: now }));
"""


def replay(script, kind="when", reduced=False, redraw_at=0):
    code = (REPLAY.replace("SCRIPT", repr(script)).replace("KIND", json.dumps(kind)).replace("REDUCED", json.dumps(reduced))
            .replace("REDRAW_AT", str(redraw_at)))
    node = subprocess.run([shutil.which("node") or "node", "-e", code], capture_output=True, text=True, check=True)
    return json.loads(node.stdout)


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

    with context("inside the story explorer, on a step group where the Customer acts"):
        with before.all:
            self.typed = replay(self.script)

        with it("should clear each field, then type each one back in a character at a time, one field after another"):
            email = [value for name, value in self.typed["writes"] if name == "email"]
            order = [name for name, _ in self.typed["writes"][5:]]
            expect((email, order.index("password") > order.index("email"), order[-1])).to(equal((["", "a", "a@", "a@b", "a@b.", "a@b.c", "a@b.co"], True, "code3")))

        with it("should end on exactly the values the scenario gave, a six-box code box by box among them"):
            expect(self.typed["values"]).to(equal(["a@b.co", "pw12", "4", "2", "7"]))

        with it("should send no input event, so neither React nor the domain sees the typing"):
            expect(self.typed["events"]).to(equal([]))

        with it("should type at a readable pace"):
            expect(1000 <= self.typed["took"] <= 3000).to(equal(True))

    with context("inside the story explorer, on a step group that only shows an outcome"):
        with it("should show the values at once, typing nothing"):
            shown = replay(self.script, kind="then")
            expect((shown["writes"], shown["values"])).to(equal(([], ["a@b.co", "pw12", "4", "2", "7"])))

    with context("for a reader who asks for reduced motion"):
        with it("should show the values at once, typing nothing"):
            shown = replay(self.script, reduced=True)
            expect((shown["writes"], shown["values"])).to(equal(([], ["a@b.co", "pw12", "4", "2", "7"])))

    with context("when React draws a field again while it is being typed"):
        with it("should stop and leave React's value, putting back the fields it had cleared"):
            shown = replay(self.script, redraw_at=7)
            expect(shown["values"]).to(equal(["redrawn@b.co", "pw12", "4", "2", "7"]))
