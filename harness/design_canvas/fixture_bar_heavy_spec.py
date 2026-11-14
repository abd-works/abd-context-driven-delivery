"""Mamba spec for a fixture-driven screen artboard's script, parsed as JavaScript. Heavy: runs Node."""

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from harness.design_canvas.fixture_bar import FixtureScreen, ScenarioSource


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
