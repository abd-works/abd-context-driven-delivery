"""Layout catalog - thin vocabulary from IA screen-templates."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import description, it

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from context_tools.ux.ux_model.layouts import known_layout_ids, layout_slots, resolve_layout
from context_tools.ux.ux_model.nodes import Screen


with description("layout catalog"):
    with it("should resolve CLI layout ids and aliases"):
        expect(resolve_layout("sidebar").slots).to(equal(("panel", "body")))
        expect(resolve_layout("list").id).to(equal("stack"))
        expect(resolve_layout("modal-dialog").id).to(equal("modal"))
        expect(layout_slots("holy-grail")).to(
            equal(["header", "nav", "body", "aside", "footer"])
        )

    with it("should list canonical ids without aliases"):
        ids = known_layout_ids()
        expect("sidebar" in ids).to(equal(True))
        expect("list" in ids).to(equal(False))

    with it("should seed Screen regions from apply_layout"):
        screen = Screen("Character Sheet", 0)
        screen.apply_layout("sidebar")
        expect(screen.layout).to(equal("sidebar"))
        expect([region.slot for region in screen.regions]).to(equal(["panel", "body"]))

    with it("should not overwrite existing regions when seeding"):
        screen = Screen("Sheet", 0)
        screen.apply_layout("sidebar")
        screen.apply_layout("split-screen")
        expect(screen.layout).to(equal("split-screen"))
        expect([region.slot for region in screen.regions]).to(equal(["panel", "body"]))
