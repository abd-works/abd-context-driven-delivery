"""BDD spec for Ux generator - fidelity defaults, transform, ensure_javascript."""

import sys
from pathlib import Path

from expects import be_true, equal, expect, raise_error
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import context_tools  # noqa: F401
from context_tools.ux.document.json.nodes import JsonUxMap
from context_tools.ux.ux import Ux
from context_tools.ux.ux_model.nodes import Screen
from context_tools.ux.ux_model.ux_map import UxMap


def _sample_json() -> str:
    ux_map = UxMap(name="demo")
    ux_map.scope = "Place New Order"
    screen = Screen("Catalog", 0)
    screen.apply_layout("stack")
    ux_map.append_screen(screen)
    return JsonUxMap.render(ux_map)


with description("Ux fidelity and format defaults"):
    with context("Ux constructed with fidelity ia"):
        with before.each:
            self.ux = Ux(fidelity="ia")

        with it("should default format to drawio"):
            expect(self.ux.format).to(equal("drawio"))

        with it("should retain fidelity ia"):
            expect(self.ux.fidelity).to(equal("ia"))

    with context("Ux constructed with fidelity mockup"):
        with before.each:
            self.ux = Ux(fidelity="mockup")

        with it("should default format to html"):
            expect(self.ux.format).to(equal("html"))

        with it("should retain fidelity mockup"):
            expect(self.ux.fidelity).to(equal("mockup"))

    with context("Ux constructed with fidelity front_end_code"):
        with it("should default format to html"):
            expect(Ux(fidelity="front_end_code").format).to(equal("html"))

    with context("Ux constructed with an unsupported fidelity"):
        with it("should raise ValueError"):
            expect(lambda: Ux(fidelity="nope")).to(raise_error(ValueError))

    with context("Ux constructed with an unsupported format"):
        with it("should raise ValueError"):
            expect(lambda: Ux(fidelity="ia", format="yaml")).to(raise_error(ValueError))


with description("Ux transform tool"):
    with context("transform from json to markdown"):
        with before.each:
            self.ux = Ux(fidelity="ia")
            self.result = self.ux.transform(
                source_format="json",
                target_format="markdown",
                content=_sample_json(),
            )

        with it("should return a dict"):
            expect(isinstance(self.result, dict)).to(be_true)

        with it("should set format to markdown"):
            expect(self.result["format"]).to(equal("markdown"))

        with it("should render markdown content that names the scope"):
            expect("Place New Order" in self.result["content"]).to(be_true)

    with context("transform with an unsupported source format"):
        with it("should raise ValueError"):
            expect(
                lambda: Ux().transform("yaml", "json", "{}")
            ).to(raise_error(ValueError))


with description("Ux ensure_javascript tool"):
    with context("an unsupported generator name"):
        with it("should raise ValueError"):
            expect(
                lambda: Ux().ensure_javascript("unknown", "markdown", "")
            ).to(raise_error(ValueError))


with description("Ux contexts instruction"):
    with context("the contexts slot is expanded"):
        with before.each:
            self.ux = Ux(fidelity="ia")
            self.contexts = self.ux.contexts().expand()

        with it("should return non-empty prose"):
            expect(len(self.contexts) > 0).to(be_true)
