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
from cdd_guidance.practices.ux.ux import NoJavascriptPractice, Ux, UxOutsideSession, ViewNotRendered
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
        with before.each:
            self.ux = Ux(fidelity="front_end_code")

        with it("should default to typescript, a format the fidelity writes"):
            expect(self.ux.format).to(equal("typescript"))

    with context("at each of its fidelities"):
        with it("should default to a format that fidelity writes"):
            strays = [fidelity.name for fidelity in Ux().fidelities if fidelity.default_format.name not in fidelity.outputs]
            expect(strays).to(equal([]))

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


with description("a front-end view rendered to another format"):
    with before.each:
        self.ux = Ux(fidelity="front_end_code")
        self.view = "export function CheckoutView() {\n  return <main>Checkout</main>;\n}\n"

    with context("from typescript to javascript"):
        with it("should refuse it as a view, which is written and not rendered, naming the format"):
            expect(lambda: self.ux.render("javascript", self.view, source="typescript")).to(
                raise_error(ViewNotRendered, "UX front-end views are written by hand in javascript, not rendered: no render reads or writes one.")
            )

    with context("with no source format named"):
        with it("should refuse it as a view, not read it as a mockup page"):
            expect(lambda: self.ux.render("drawio", self.view)).to(raise_error(ViewNotRendered))

    with context("from a mockup page to typescript"):
        with it("should refuse it, naming typescript"):
            def render():
                self.ux.render("typescript", "<html></html>", source="html")

            expect(render).to(raise_error(ViewNotRendered))


with description("Ux ensure_javascript tool"):
    with context("with Ux working in no session"):
        with it("should refuse it as a Ux with no practices of its own"):
            expect(
                lambda: Ux().ensure_javascript("stories", "markdown", "")
            ).to(raise_error(UxOutsideSession))

    with context("with Ux working in a session"):
        with before.each:
            self.project = Path(tempfile.mkdtemp(prefix="cdd-ux-"))
            (self.project / ".git").mkdir()
            sessions = Sessions(self.project)
            self.session = sessions.opened.open(sessions.create("alpha", self.project))
            self.ux = self.session.practices["ux"].guidance

        with after.each:
            shutil.rmtree(self.project, ignore_errors=True)

        with it("should get the JavaScript from that session's own Stories practice"):
            expect(self.ux.javascript_practice("stories")).to(be(self.session.practices["stories"].guidance))

        with context("asked for a practice that writes no mockup JavaScript"):
            with it("should refuse it as a practice with no JavaScript"):
                expect(
                    lambda: self.ux.ensure_javascript("ddd", "markdown", "")
                ).to(raise_error(NoJavascriptPractice))


with description("Ux contexts instruction"):
    with context("the contexts section is expanded"):
        with before.each:
            self.ux = Ux(fidelity="ia")
            self.contexts = self.ux.scoped_markdown

        with it("should return non-empty prose"):
            expect(len(self.contexts) > 0).to(be_true)


_UX_CONTEXT = (
    "# UX context\n\n"
    "Scope: Browse Books, Fill Cart\n\n"
    "## Invariants\n- A Cart Line shows one Book and its quantity.\n\n"
    "## Notes\n- A Customer reaches the Cart from every screen through the Main Nav.\n"
)
_IA_DRAWING = (
    '<mxfile host="drawio-ux"><diagram id="site-map" name="Site Map"><mxGraphModel><root>'
    '<mxCell id="0"/><mxCell id="1" parent="0"/>'
    '<mxCell id="2" value="Book List" style="rounded=1;" vertex="1" parent="1"><mxGeometry x="40" y="40" width="200" height="48" as="geometry"/></mxCell>'
    '<mxCell id="3" value="Cart" style="rounded=1;" vertex="1" parent="1"><mxGeometry x="300" y="40" width="200" height="48" as="geometry"/></mxCell>'
    '<mxCell id="4" value="View cart" style="html=1;" edge="1" source="2" target="3" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>'
    "</root></mxGraphModel></diagram></mxfile>"
)


with description("a UX map rendered over the other file its fidelity keeps"):
    with before.each:
        self.ux = Ux(fidelity="ia")

    with context("from its drawing, which holds no scope or notes, over the UX context a person wrote"):
        with before.each:
            self.result = self.ux.render("markdown", _IA_DRAWING, source="drawio", previous=_UX_CONTEXT)

        with it("should keep the scope, the invariants, and the notes the UX context holds"):
            expect(self.result["content"]).to(equal(_UX_CONTEXT))

    with context("from its UX context, which holds no screens, over the drawing a person made"):
        with before.each:
            self.result = self.ux.render("drawio", _UX_CONTEXT, source="markdown", previous=_IA_DRAWING)

        with it("should keep the drawing with its screens and transitions"):
            expect(self.result["content"]).to(equal(_IA_DRAWING))

    with context("from a map that holds its own scope, over the UX context a person wrote"):
        with before.each:
            self.result = self.ux.render("markdown", UxJsonSample().render(), source="json", previous=_UX_CONTEXT)

        with it("should write the map's scope"):
            expect("Scope: Place New Order" in self.result["content"]).to(be_true)

        with it("should keep the invariants the map does not hold"):
            expect("- A Cart Line shows one Book and its quantity." in self.result["content"]).to(be_true)
