"""Mamba spec for a story's prototype screen with its script run by Node: the position it shows for the step group on
show, an outline row taking the outline's positions, and a press moving the explorer to the next Then. Heavy: runs
Node."""

import json
import re
import shutil
import subprocess

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.ux.model.claude_design.story_screen import StoryScreen, WrittenMarkup


RUN = """
class DCLogic { constructor() { this.props = {}; this.state = null; } setState(next) { this.state = Object.assign({}, this.state || {}, next); } forceUpdate() {} }
const Component = new Function('DCLogic', SCRIPT + '; return Component;')(DCLogic);
const screen = new Component();
const moves = [];
screen.props = Object.assign({ go: (...to) => moves.push(to) }, PROPS);
screen.state = screen.fromFixture({ planRepository: { plans: 4 } }, '', {}, '', BOUND);
const vals = screen.renderVals();
vals.advance({ target: { closest: (selector) => PRESSED } });
setTimeout(() => console.log(JSON.stringify({ position: vals.position, moves, cart: vals.cart ?? null, credentials: vals.credentials ?? null,
  bound: vals.bound, repositories: vals.repositories, go: typeof vals.go })), 5);
"""


BOUND = {"cart": {"plan": "Ace"}, "credentials": {"email": "sam@example.com"}}


def run(script, props, pressed="({})", bound=None):
    code = (RUN.replace("SCRIPT", repr(script)).replace("PROPS", json.dumps(props)).replace("PRESSED", pressed)
            .replace("BOUND", json.dumps(BOUND if bound is None else bound)))
    node = subprocess.run([shutil.which("node") or "node", "-e", code], capture_output=True, text=True, check=True)
    return json.loads(node.stdout)


with description("a story's prototype screen, run") as self:
    with before.all:
        html = StoryScreen(
            title="Add Line To Cart",
            story="Add Line To Cart",
            markup=WrittenMarkup(head="", body="<main></main>"),
            positions={"Add one more line": [{"page": "plans"}, {"page": "cart"}],
                       "Add a line with ${plan}": [{"page": "plans"}, {"page": "cart", "sheet": "plan"}]},
            story_position={"page": "home"},
        ).html
        self.script = re.search(r"data-dc-script[^>]*>(.*)</script>", html, re.S).group(1)

    with context("with the objects a scenario bound"):
        with it("should hand the markup each one under its own name"):
            shown = run(self.script, {"story": "Add Line To Cart", "scenario": "Add one more line", "stepIndex": 0})
            expect((shown["cart"], shown["credentials"])).to(equal(({"plan": "Ace"}, {"email": "sam@example.com"})))

        with it("should hand the markup all of them at once, with the repositories its Givens filled and the explorer's go"):
            shown = run(self.script, {"story": "Add Line To Cart", "scenario": "Add one more line", "stepIndex": 0})
            expect((shown["bound"], shown["repositories"], shown["go"])).to(equal((BOUND, {"planRepository": {"plans": 4}}, "function")))

        with it("should hand the markup none when the scenario bound none"):
            shown = run(self.script, {"story": "Sign In", "scenario": "Sign in", "stepIndex": 0}, bound={})
            expect((shown["cart"], shown["bound"])).to(equal((None, {})))

    with context("on a scenario's step group"):
        with it("should show the position for that group's stepIndex"):
            shown = run(self.script, {"story": "Add Line To Cart", "scenario": "Add one more line", "stepIndex": 1})
            expect(shown["position"]).to(equal({"page": "cart"}))

        with it("should keep the last position past the scenario's last group"):
            shown = run(self.script, {"story": "Add Line To Cart", "scenario": "Add one more line", "stepIndex": 5})
            expect(shown["position"]).to(equal({"page": "cart"}))

    with context("on an outline's example row"):
        with it("should take the outline's positions"):
            shown = run(self.script, {"story": "Add Line To Cart", "scenario": "Add a line with ${plan}: Atlas", "stepIndex": 1})
            expect(shown["position"]).to(equal({"page": "cart", "sheet": "plan"}))

    with context("on a scenario it keeps no positions for"):
        with it("should show the story's position"):
            shown = run(self.script, {"story": "Add Line To Cart", "scenario": "Remove a line", "stepIndex": 0})
            expect(shown["position"]).to(equal({"page": "home"}))

    with context("when a button is pressed"):
        with it("should move the explorer to the next Then before the scenario's last outcome"):
            shown = run(self.script, {"story": "Add Line To Cart", "scenario": "Add one more line", "stepIndex": 0}, pressed="({})")
            expect(shown["moves"]).to(equal([["Add Line To Cart", "Add one more line", "Then"]]))

        with it("should stay at the scenario's last outcome"):
            shown = run(self.script, {"story": "Add Line To Cart", "scenario": "Add one more line", "stepIndex": 1}, pressed="({})")
            expect(shown["moves"]).to(equal([]))

    with context("when the press lands on no button or link"):
        with it("should leave the explorer where it is"):
            shown = run(self.script, {"story": "Add Line To Cart", "scenario": "Add one more line", "stepIndex": 0}, pressed="null")
            expect(shown["moves"]).to(equal([]))
