"""Mamba spec for a fixture-driven screen artboard and the fixture bar it shows."""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

from harness.design_canvas.fixture_bar import FIXTURE_TRIES, FIXTURE_WAIT_MILLISECONDS, FixtureScreen, ScenarioSource


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

    with context("with its script read as JavaScript"):
        with it("should parse"):
            script = Path(tempfile.mkdtemp()) / "screen.js"
            script.write_text("class DCLogic {}\n" + self.script, encoding="utf-8")
            checked = subprocess.run([shutil.which("node") or "node", "--check", str(script)], capture_output=True, text=True)
            expect(checked.stderr).to(equal(""))
