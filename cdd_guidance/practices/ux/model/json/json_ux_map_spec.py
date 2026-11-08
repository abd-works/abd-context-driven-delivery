"""BDD spec for JsonUxMap - the whole map round-trips through JSON."""

import json
import sys
from pathlib import Path

from expects import be, equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.json.nodes import JsonContentType, JsonNavComponent, JsonUxMap
from cdd_guidance.practices.ux.model.ux_map import ScreenNotOnMap, UxMap
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import OrderingMap, outline


with description("a UX map written as JSON"):
    with before.each:
        self.source = OrderingMap().build(UxMap.create())
        self.rendered = JsonUxMap.create().render(self.source)

    with context("that is read back"):
        with before.each:
            self.parsed = JsonUxMap.create().parse(self.rendered)

        with it("should read back the same map it wrote"):
            expect(outline(self.parsed)).to(equal(outline(self.source)))

        with it("should link each transition to the screens on the read map"):
            expect(self.parsed.transitions[0].to_screen).to(be(self.parsed.find_screen("Cart")))

        with it("should link a tab to the screen whose chrome it shares"):
            expect(self.parsed.find_screen("Cart - Saved").chrome_of).to(be(self.parsed.find_screen("Cart")))

        with it("should link each interaction to its destination screen"):
            browse = self.parsed.find_screen("Catalog").regions[0].controls[0]
            expect(browse.interactions[0].destination).to(be(self.parsed.find_screen("Cart")))

        with it("should keep every node on the read map's graph"):
            control = self.parsed.find_screen("Catalog").regions[0].controls[0]
            expect(control.interactions[0].graph).to(be(self.parsed.graph))

        with it("should read each content type and navigation component as the JSON format's own node"):
            kinds = (type(self.parsed.content_types[0]), type(self.parsed.nav_components[0]))
            expect(kinds).to(equal((JsonContentType, JsonNavComponent)))

    with context("that names a screen the map does not have"):
        with before.each:
            data = json.loads(self.rendered)
            data["transitions"][0]["to_screen"] = "Checkout"
            self.broken = json.dumps(data)

        with it("should refuse it as a screen not on the map"):
            expect(lambda: JsonUxMap.create().parse(self.broken)).to(raise_error(ScreenNotOnMap))
