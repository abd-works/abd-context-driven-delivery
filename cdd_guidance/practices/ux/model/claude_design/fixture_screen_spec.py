"""Mamba spec for a fixture-driven screen artboard and the fixture bar it shows. Its script parsed by Node is in
fixture_screen_heavy_spec.py."""

import re

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.ux.model.claude_design.fixture_screen import (
    ENTRY_CHARACTER_MILLISECONDS,
    ENTRY_FIELDS,
    FIXTURE_TRIES,
    FIXTURE_WAIT_MILLISECONDS,
    FixtureScreen,
    ScenarioSource,
)
from cdd_guidance.practices.ux.model.claude_design.screen_artboard import ScreenArtboard


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

    with context("with its story and scenario"):
        with it("should open on its scenario"):
            expect(self.script).to(contain("'Pick the cheapest plan'"))

        with it("should offer the dev seed paste for its path"):
            expect(self.script).to(contain("pasteFor('/plans')"))

    with context("waiting for the fixtures bundle"):
        with it("should ask for it the named number of times"):
            expect(self.script).to(contain(f"tries++ >= {FIXTURE_TRIES}"))

        with it("should wait the named time between asks"):
            expect(self.script).to(contain(f"setTimeout(wait, {FIXTURE_WAIT_MILLISECONDS})"))

    with context("inside the story explorer"):
        with it("should link Edit to the screen's own artboard"):
            expect(self.html).to(contain('href="/screens/select-plan.dc.html"'))

        with it("should declare every prop the explorer hands it"):
            expect(ScreenArtboard(self.html).declared_props).to(equal({"story", "scenario", "step", "stepIndex", "stepKind", "go", "$preview"}))

        with it("should read the scenario and the step the explorer selects"):
            artboard = ScreenArtboard(self.html)
            expect((artboard.reads_prop("scenario"), artboard.reads_prop("step"))).to(equal((True, True)))

        with it("should hand the selected step to fromFixture, so a Then can show its outcome"):
            expect(self.script).to(contain("this.fromFixture(repositories, scenario, fixtures.examples, this.props.step || '', fixtures.bindings ? fixtures.bindings() : {})"))

    with context("on a step group where the Customer acts"):
        with it("should type its filled fields back in once the step group's state is drawn"):
            expect(self.script).to(contain("() => this.replayEntries()"))

        with it("should type only on a When step group"):
            expect(self.script).to(contain("if (this.props.stepKind !== 'when' || this.reducedMotion()) return;"))

        with it("should honour reduced motion, showing the values at once"):
            expect(self.script).to(contain("window.matchMedia('(prefers-reduced-motion: reduce)').matches"))

        with it("should type into text-like fields and text areas inside its own root"):
            expect((self.html.count('class="plans" data-screen-id="{{screenId}}"'), ENTRY_FIELDS in self.script)).to(equal((1, True)))

        with it("should type a character at the named pace"):
            expect(self.script).to(contain(f"replay.timer = setTimeout(next, {ENTRY_CHARACTER_MILLISECONDS});"))

        with it("should change only what a field shows, through its native value setter, without sending an input event"):
            expect((("described.set.call(field, value)" in self.script), ("dispatchEvent" in self.script))).to(equal((True, False)))
