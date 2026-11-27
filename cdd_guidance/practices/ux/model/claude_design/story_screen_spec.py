"""Mamba spec for a story's prototype screen, built on the fixture bar from one of three sources of markup: written from
scratch, taken from a page of an existing app, or ported from another Claude Design canvas. Its script run by Node is
in story_screen_heavy_spec.py."""

import re

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

from cdd_guidance.practices.ux.model.claude_design.screen_artboard import ScreenArtboard
from cdd_guidance.practices.ux.model.claude_design.story_screen import AppPageMarkup, PortedCanvasMarkup, StoryScreen, WrittenMarkup


APP_PAGE = """<!doctype html>
<html><head>
<link rel="stylesheet" href="/static/css/app.css">
<style>.plan{color:red}</style>
<script src="/static/js/app.js"></script>
</head>
<body class="app"><main class="plan">{{ cart.plan }}</main><script>boot()</script></body></html>"""


def screen(markup, **more):
    return StoryScreen(
        title="Add Line To Cart",
        story="Add Line To Cart",
        markup=markup,
        positions={"Add one more line": [{"page": "plans"}, {"page": "cart", "cartOpen": True}]},
        **more,
    )


with description("a story's prototype screen") as self:
    with before.all:
        self.html = screen(WrittenMarkup(head='<link rel="stylesheet" href="../styles/app.css">', body="<main>{{ cart.plan }}</main>")).html
        self.script = re.search(r"data-dc-script[^>]*>(.*)</script>", self.html, re.S).group(1)

    with context("inside the story explorer"):
        with it("should declare story, scenario, step, stepIndex, stepKind and go"):
            expect(ScreenArtboard(self.html).declared_props).to(equal({"story", "scenario", "step", "stepIndex", "stepKind", "go", "$preview"}))

        with it("should open on its first scenario"):
            expect(self.script).to(contain("'Add one more line'"))

    with context("loading its scenario"):
        with it("should load through the fixture bar"):
            expect(ScreenArtboard(self.html).loads_fixtures).to(equal(True))

        with it("should keep every object the scenario bound, and the repositories its Givens filled"):
            expect(self.script).to(contain("return { bound: Object.assign({}, bindings || {}), repositories: repositories || {} };"))

        with it("should hand the markup each bound object under its own name"):
            expect(self.script).to(contain("...(st.bound || {}),"))

        with it("should hand the markup every bound object at once, the repositories, and the explorer's go"):
            expect(self.script).to(contain(r"bound: st.bound || {}," + "\n" + "repositories: st.repositories || {}," + "\n" + "go: this.props.go || null,"))

        with it("should load the fixtures bundle after its own stylesheets"):
            expect(self.html).to(contain('<link rel="stylesheet" href="../styles/app.css">\n<script src="../fixtures/canvas-fixtures.js"></script>'))

    with context("with its markup written from scratch"):
        with it("should draw that markup inside the element that moves the explorer on a press"):
            expect(self.html).to(contain('onClickCapture="{{ advance }}">\n<main>{{ cart.plan }}</main>\n</div>'))

    with context("drawn at its own size"):
        with it("should draw its markup in a frame a phone wide, centred, at least a phone tall"):
            expect(self.html).to(contain('<div class="canvas-screen" style="box-sizing: border-box; width: 390px; min-height: 844px; margin: 0 auto;'))

        with it("should make the frame the canvas-screen size container, which the stylesheets' container rules ask"):
            expect(self.html).to(contain("container-type: inline-size; container-name: canvas-screen; contain: layout paint\""))

        with it("should draw a screen of another size in a frame of that size, and state that size to the canvas"):
            wide = screen(WrittenMarkup(head="", body="<main></main>"), width=768, height=1024)
            expect((wide.html.count("width: 768px; min-height: 1024px"), ScreenArtboard(wide.html).preview_size)).to(equal((1, (768, 1024))))

    with context("with its markup taken from a page of an existing app"):
        with before.all:
            self.page = AppPageMarkup(APP_PAGE, stylesheet_folder="../styles")
            self.app_html = screen(self.page).html

        with it("should link the page's stylesheets from the canvas's stylesheet folder"):
            expect(self.app_html).to(contain('<link rel="stylesheet" href="../styles/app.css">'))

        with it("should name the stylesheets the project copies into that folder"):
            expect(self.page.stylesheets).to(equal(("/static/css/app.css",)))

        with it("should keep the page's own styles"):
            expect(self.app_html).to(contain("<style>.plan{color:red}</style>"))

        with it("should draw the page's body without its scripts"):
            expect((self.app_html.count('<main class="plan">{{ cart.plan }}</main>'), "boot()" in self.app_html, "app.js" in self.app_html)).to(equal((1, False, False)))

    with context("with its markup ported from another Claude Design canvas"):
        with before.all:
            self.ported_html = screen(PortedCanvasMarkup(component="flow", head='<script src="../flow.js"></script>', attributes={"theme": "dark"}, size="100%,844px",
                                                         inputs=("cart",))).html

        with it("should draw the ported component with each bound object it takes and each position setting"):
            expect(self.ported_html).to(contain('<dc-import name="flow" theme="dark" cart="{{ cart }}" cart-open="{{ position.cartOpen }}" page="{{ position.page }}" hint-size="100%,844px"></dc-import>'))

        with it("should load the ported component's scripts"):
            expect(self.ported_html).to(contain('<script src="../flow.js"></script>'))

    with context("drawn in the canvas's theme"):
        with it("should hand the ported component the theme, over any it was given, and set it on the screen's frame"):
            themed = screen(PortedCanvasMarkup(component="flow", attributes={"theme": "light"}), theme="dark").html
            expect((themed.count(' theme="dark"'), 'theme="light"' in themed, themed.count('<div class="canvas-screen" data-theme="dark"'))).to(equal((1, False, 1)))

    with context("with a ported component that takes a bound object whose name is not a JavaScript name"):
        with it("should refuse it"):
            markup = PortedCanvasMarkup(component="flow", inputs=("the cart",))
            expect(lambda: StoryScreen(title="x", story="x", markup=markup, positions={}).html).to(raise_error(ValueError))
