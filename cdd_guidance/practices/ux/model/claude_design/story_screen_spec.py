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
        domain_input="cart",
        positions={"Add one more line": [{"page": "plans"}, {"page": "cart", "cartOpen": True}]},
        **more,
    )


with description("a story's prototype screen") as self:
    with before.all:
        self.html = screen(WrittenMarkup(head='<link rel="stylesheet" href="../styles/app.css">', body="<main>{{ cart.plan }}</main>")).html
        self.script = re.search(r"data-dc-script[^>]*>(.*)</script>", self.html, re.S).group(1)

    with context("inside the story explorer"):
        with it("should declare story, scenario, step, stepIndex and go"):
            expect(ScreenArtboard(self.html).declared_props).to(equal({"story", "scenario", "step", "stepIndex", "go", "$preview"}))

        with it("should open on its first scenario"):
            expect(self.script).to(contain("'Add one more line'"))

    with context("loading its scenario"):
        with it("should load through the fixture bar"):
            expect(ScreenArtboard(self.html).loads_fixtures).to(equal(True))

        with it("should hand the markup the domain objects the scenario bound under its named input"):
            expect(self.script).to(contain("return { cart: (bindings && bindings.cart) || null };"))

        with it("should load the fixtures bundle after its own stylesheets"):
            expect(self.html).to(contain('<link rel="stylesheet" href="../styles/app.css">\n<script src="../fixtures/canvas-fixtures.js"></script>'))

    with context("with its markup written from scratch"):
        with it("should draw that markup inside the element that moves the explorer on a press"):
            expect(self.html).to(contain('onClickCapture="{{ advance }}">\n<main>{{ cart.plan }}</main>\n</div>'))

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
            self.ported_html = screen(PortedCanvasMarkup(component="flow", head='<script src="../flow.js"></script>', attributes={"theme": "dark"}, size="100%,844px")).html

        with it("should draw the ported component with the named input and each position setting"):
            expect(self.ported_html).to(contain('<dc-import name="flow" theme="dark" cart="{{ cart }}" cart-open="{{ position.cartOpen }}" page="{{ position.page }}" hint-size="100%,844px"></dc-import>'))

        with it("should load the ported component's scripts"):
            expect(self.ported_html).to(contain('<script src="../flow.js"></script>'))

    with context("with a named input that is not a JavaScript name"):
        with it("should refuse it"):
            expect(lambda: StoryScreen(title="x", story="x", markup=WrittenMarkup(head="", body=""), domain_input="the cart", positions={}).html).to(raise_error(ValueError))
