"""BDD spec for JsonUxMap - screen and transition round-trip."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import before, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from context_tools.ux.document.json.nodes import JsonUxMap
from context_tools.ux.ux_model.nodes import Screen, Transition
from context_tools.ux.ux_model.ux_map import UxMap


with description("JsonUxMap"):
    with before.each:
        self.source = UxMap(name="demo")
        self.source.scope = "Place New Order"
        screen = Screen("Catalog", 0, "catalog")
        screen.apply_layout("stack")
        screen.attach_domain_term("Product")
        self.source.append_screen(screen)
        self.source.append_transition(
            Transition(
                "opens cart",
                0,
                from_screen="Catalog",
                to_screen="Cart",
                trigger="opens cart",
                nav_type="action",
            )
        )
        self.rendered = JsonUxMap.render(self.source)
        self.parsed = JsonUxMap.parse(self.rendered)

    with it("should round-trip scope and screen names"):
        expect(self.parsed.scope).to(equal("Place New Order"))
        expect([s.name for s in self.parsed.screens]).to(equal(["Catalog"]))

    with it("should round-trip layout-seeded regions and domain terms"):
        screen = self.parsed.find_screen("Catalog")
        expect(screen.layout).to(equal("stack"))
        expect(screen.domain_terms).to(equal(["Product"]))
        expect([r.slot for r in screen.regions]).to(equal(["rows"]))

    with it("should round-trip transitions"):
        expect(len(self.parsed.transitions)).to(equal(1))
        expect(self.parsed.transitions[0].to_screen).to(equal("Cart"))
