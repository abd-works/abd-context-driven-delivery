"""BDD spec for HtmlUxMap - shell render and embedded JSON parse."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import before, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from context_tools.ux.ux_model.nodes import Control, Region, Screen
from context_tools.ux.ux_model.ux_map import UxMap
from context_tools.ux.web.html.nodes import HtmlUxMap


with description("HtmlUxMap"):
    with before.each:
        self.source = UxMap(name="demo")
        self.source.scope = "Place New Order"
        self.source.story_references = ["stories/place_order.js"]
        screen = Screen("Catalog", 0, "catalog")
        screen.apply_layout("stack")
        region = Region("body", 0, "body")
        region.append_control(Control("Browse", 0, "button", "Browse", ""))
        screen.append_region(region)
        self.source.append_screen(screen)
        self.rendered = HtmlUxMap.render(self.source)
        self.parsed = HtmlUxMap.parse(self.rendered)

    with it("should emit the mockup shell with screen markup"):
        expect("<article class=\"screen\"" in self.rendered).to(equal(True))
        expect("Catalog" in self.rendered).to(equal(True))
        expect("data-ux-story-ref" in self.rendered).to(equal(True))

    with it("should parse the embedded ux-map-json marker"):
        expect(self.parsed.scope).to(equal("Place New Order"))
        expect([s.name for s in self.parsed.screens]).to(equal(["Catalog"]))
