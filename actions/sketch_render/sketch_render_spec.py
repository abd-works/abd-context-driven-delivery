"""BDD spec for sketch_render — sketch approval triggers background render."""

import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import before, context, description, it

from actions.sketch_render.sketch_render import STAGE_DEFAULT_FORMATS, SketchRender
from harness.agent_tools.agent_tools import AgentInstructions

with description("SketchRender"):
    with context("stage default formats"):
        with it("should use drawio and markdown for discovery"):
            expect(SketchRender().stage_default_formats("discovery")).to(
                equal(STAGE_DEFAULT_FORMATS["discovery"])
            )

        with it("should use typescript and markdown for specification"):
            expect(SketchRender().stage_default_formats("specification")).to(
                equal(STAGE_DEFAULT_FORMATS["specification"])
            )

    with context("build_render_calls"):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.sketch_path = Path(self.tmp.name) / "engagement-sketch.md"
            self.sketch_path.write_text(
                "(E) Manage Customer Orders\n    (S) Customer --> Browse Catalog\n",
                encoding="utf-8",
            )
            self.action = SketchRender()
            self.action.begin(["stories"], action="sketch_render")

        with it("should emit one render.render call per chosen format"):
            payload = json.loads(
                self.action.build_render_calls(
                    ["drawio", "markdown"],
                    str(self.sketch_path),
                )
            )
            expect(len(payload)).to(equal(2))
            expect(payload[0]["tool"]).to(equal("render.render"))
            expect(payload[0]["arguments"]["format"]).to(equal("drawio"))
            expect(payload[0]["arguments"]["source"]).to(equal("sketch"))
            expect(payload[0]["arguments"]["guidance"]["fidelity"]).to(equal("story_map"))
            expect(payload[0]["arguments"]["content"]).to(contain("Manage Customer Orders"))

        with it("should skip formats the guidance does not support"):
            payload = json.loads(
                self.action.build_render_calls(
                    ["html", "markdown"],
                    str(self.sketch_path),
                )
            )
            formats = [entry["arguments"]["format"] for entry in payload]
            expect("html" in formats).to(equal(False))
            expect("markdown" in formats).to(equal(True))

        with it("should not emit markdown for ddd or ux when all practices are listed"):
            self.action.begin(["stories", "ddd", "ux"], action="sketch_render")
            payload = json.loads(
                self.action.build_render_calls(
                    ["drawio", "markdown"],
                    str(self.sketch_path),
                )
            )
            ddd_formats = [
                entry["arguments"]["format"]
                for entry in payload
                if entry["arguments"]["guidance"]["toolset"].endswith("ddd:Ddd")
            ]
            ux_formats = [
                entry["arguments"]["format"]
                for entry in payload
                if entry["arguments"]["guidance"]["toolset"].endswith("ux:Ux")
            ]
            expect("markdown" in ddd_formats).to(equal(True))
            expect("markdown" in ux_formats).to(equal(False))
            expect("drawio" in ddd_formats).to(equal(True))
            expect("drawio" in ux_formats).to(equal(True))

    with context("render_approved_sketch"):
        with it("should be a non-blocking sub_agent in the manifest"):
            entry = SketchRender.manifest.signature["render_approved_sketch"]
            expect(entry["kind"]).to(equal("sub_agent"))
            expect(entry["launch"]).to(equal("non_blocking"))

    with context("sketch_render action"):
        with before.each:
            self.body = AgentInstructions.for_callable(
                SketchRender.sketch_render,
                SketchRender(),
            )

        with it("should wire sketch review before render confirmation"):
            steps = list(self.body.tool_steps)
            review_index = steps.index("review_sketch")
            expect("build_render_calls" in steps[review_index:]).to(equal(True))
            joined = "\n".join(self.body.prompt)
            expect(joined).to(contain("AskQuestion whether to render"))
            expect(joined).to(contain("render.render"))

        with it("should instruct format confirmation with stage defaults"):
            joined = "\n".join(self.body.prompt)
            expect(joined).to(contain("drawio"))
            expect(joined).to(contain("typescript"))
            expect(joined).to(contain("review_sketch"))
