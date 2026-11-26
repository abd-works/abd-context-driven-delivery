"""BDD spec for ClaudeDesignUxMap - a mockup written as a Claude Design canvas, one prototype page for each screen, and
read back whole."""

import json
import sys
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.claude_design.nodes import ClaudeDesignScreenMissing, ClaudeDesignUxMap, NotAClaudeDesignCanvas
from cdd_guidance.practices.ux.model.html.nodes import HtmlUxMap
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import OrderingMap, outline

_PAGES = ["screens/catalog.dc.html", "screens/cart.dc.html", "screens/cart-saved.dc.html"]


with description("a UX mockup rendered to a Claude Design canvas"):
    with before.each:
        self.source = OrderingMap().build(UxMap.create())
        self.mockup = HtmlUxMap.create().render(self.source)
        self.files = ClaudeDesignUxMap.create().render(HtmlUxMap.create().parse(self.mockup))
        self.canvas = json.loads(self.files["project/canvas.json"])

    with it("should write one prototype page for each screen, beside canvas.json"):
        expect(sorted(self.files)).to(equal(sorted(["project/canvas.json", *[f"project/{page}" for page in _PAGES]])))

    with it("should place each screen's page on a canvas page of its own, in screen order"):
        expect(self.canvas["order"]).to(equal(_PAGES))

    with it("should title each board with its screen's name"):
        expect(self.canvas["boards"]["screens/cart-saved.dc.html"]).to(equal({
            "x": 0, "y": 0, "w": 1600, "h": 1100, "page": "screen-cart-saved", "title": "Cart - Saved", "is_interactive": True,
        }))

    with it("should write a page the HTML format reads, opening on its own screen with its regions and controls"):
        page = HtmlUxMap.create().parse(self.files["project/screens/catalog.dc.html"])
        expect(outline(page)["screens"][0]).to(equal(outline(self.source)["screens"][0]))

    with it("should keep in each page the transitions the screen takes part in"):
        page = HtmlUxMap.create().parse(self.files["project/screens/cart.dc.html"])
        expect(outline(page)["transitions"]).to(equal(outline(self.source)["transitions"]))

    with context("that is read back"):
        with before.each:
            self.parsed = ClaudeDesignUxMap.create().parse(self.files)

        with it("should read back the same mockup it wrote"):
            expect(outline(self.parsed)).to(equal(outline(self.source)))

        with it("should render to the same HTML mockup it was rendered from"):
            expect(HtmlUxMap.create().render(self.parsed)).to(equal(self.mockup))

    with context("whose prototype page for a screen is missing"):
        with it("should refuse the screen by its page"):
            files = {path: text for path, text in self.files.items() if path != "project/screens/cart.dc.html"}
            expect(lambda: ClaudeDesignUxMap.create().parse(files)).to(
                raise_error(ClaudeDesignScreenMissing, contain("screens/cart.dc.html")))

    with context("read from its canvas.json alone"):
        with it("should refuse the first screen, whose page it does not hold"):
            expect(lambda: ClaudeDesignUxMap.create().parse(self.files["project/canvas.json"])).to(
                raise_error(ClaudeDesignScreenMissing, contain("screens/catalog.dc.html")))

    with context("that is not a canvas"):
        with it("should refuse JSON that places no boards"):
            expect(lambda: ClaudeDesignUxMap.create().parse("{}")).to(raise_error(NotAClaudeDesignCanvas))


with description("a UX map's prototype screens placed on the story canvas"):
    with it("should place each screen's prototype once, on its own page"):
        boards = ClaudeDesignUxMap.create().copy_of(OrderingMap().build(UxMap.create())).boards()
        expect(boards).to(equal({
            "screens/catalog.dc.html": {
                "x": 0, "y": 0, "w": 1600, "h": 1100, "page": "screen-catalog", "title": "Catalog",
                "is_interactive": True,
            },
        }))
