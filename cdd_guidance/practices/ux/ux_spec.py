"""BDD spec for Ux generator - fidelity defaults, transform, ensure_javascript."""

import shutil
import sys
import tempfile
from pathlib import Path

from expects import be, be_true, equal, expect, raise_error
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cdd_guidance.practices  # noqa: F401
from cdd_guidance.practices.ux.model.json.nodes import JsonUxMap
from cdd_guidance.practices.ux.ux import NoJavascriptPractice, Ux
from cdd_guidance.practices.ux.model.nodes import Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap
from space.session.sessions import Sessions


class UxJsonSample:
    def render(self) -> str:
        ux_map = UxMap.create(name="demo")
        ux_map.scope = "Place New Order"
        screen = Screen("Catalog", 0)
        screen.apply_layout("stack")
        ux_map.append_screen(screen)
        return JsonUxMap.create().render(ux_map)


with description("Ux fidelity and format defaults"):
    with context("Ux constructed with fidelity ia"):
        with before.each:
            self.ux = Ux(fidelity="ia")

        with it("should default format to drawio"):
            expect(self.ux.format).to(equal("drawio"))

        with it("should retain fidelity ia"):
            expect(self.ux.fidelities.current.name).to(equal("ia"))

    with context("Ux constructed with fidelity mockup"):
        with before.each:
            self.ux = Ux(fidelity="mockup")

        with it("should default format to html"):
            expect(self.ux.format).to(equal("html"))

        with it("should retain fidelity mockup"):
            expect(self.ux.fidelities.current.name).to(equal("mockup"))

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
            self.result = self.ux.render(
                format="markdown",
                content=UxJsonSample().render(),
                source="json",
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
                lambda: Ux().render("json", "{}", source="yaml")
            ).to(raise_error(ValueError))


with description("Ux ensure_javascript tool"):
    with context("a practice that writes no mockup JavaScript"):
        with it("should refuse it as a practice with no JavaScript"):
            expect(
                lambda: Ux().ensure_javascript("ddd", "markdown", "")
            ).to(raise_error(NoJavascriptPractice))

    with context("with Ux working in a session"):
        with before.each:
            self.project = Path(tempfile.mkdtemp(prefix="cdd-ux-"))
            (self.project / ".git").mkdir()
            sessions = Sessions(self.project)
            self.session = sessions.open(sessions.create("alpha", self.project))
            self.ux = self.session.practices["ux"].guideline

        with after.each:
            shutil.rmtree(self.project, ignore_errors=True)

        with it("should get the JavaScript from that session's own Stories practice"):
            expect(self.ux.javascript_practice("stories")).to(be(self.session.practices["stories"].guideline))


with description("Ux contexts instruction"):
    with context("the contexts section is expanded"):
        with before.each:
            self.ux = Ux(fidelity="ia")
            self.contexts = self.ux.scoped_markdown()

        with it("should return non-empty prose"):
            expect(len(self.contexts) > 0).to(be_true)
