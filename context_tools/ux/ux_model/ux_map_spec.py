"""BDD spec for UxMap - screens, references, story name aggregation."""

import sys
from pathlib import Path

from expects import equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from context_tools.ux.ux_model.nodes import Screen
from context_tools.ux.ux_model.ux_map import UxMap


with description("a UxMap"):
    with context("that has screens appended"):
        with before.each:
            self.ux_map = UxMap(name="orders")
            self.ux_map.append_screen(Screen("Catalog", 0))
            self.ux_map.append_screen(Screen("Cart", 1))

        with it("should find a screen by name"):
            expect(self.ux_map.find_screen("Cart").name).to(equal("Cart"))

        with it("should remove a screen by name"):
            removed = self.ux_map.remove_screen("Catalog")
            expect(removed.name).to(equal("Catalog"))
            expect(len(self.ux_map.screens)).to(equal(1))

        with it("should raise KeyError when the screen is missing"):
            expect(lambda: self.ux_map.find_screen("Missing")).to(
                raise_error(KeyError)
            )

    with context("that holds story references and screen story names"):
        with before.each:
            self.ux_map = UxMap()
            self.ux_map.story_references = ["stories/place_order.js"]
            sheet = Screen("Catalog", 0)
            sheet.attach_story_name("Browse Product Catalog")
            self.ux_map.append_screen(sheet)

        with it("should expose story_references as a list"):
            expect(self.ux_map.story_references.as_list()).to(
                equal(["stories/place_order.js"])
            )

        with it("should aggregate all story names from screens"):
            expect(self.ux_map.all_story_names()).to(
                equal(["Browse Product Catalog"])
            )
