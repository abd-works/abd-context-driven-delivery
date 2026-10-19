"""BDD spec for UxMap - screens, references, story name aggregation."""

import sys
from pathlib import Path

from expects import be, contain, equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph import Graph

from cdd_guidance.practices.ux.model.nodes import Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap


with description("a UxMap"):
    with context("that has screens appended"):
        with before.each:
            self.ux_map = UxMap.create(name="orders")
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
            self.ux_map = UxMap.create()
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


with description("a ux map on a graph"):
    with before.each:
        self.graph = Graph()
        self.ux_map = UxMap.create(self.graph)
        self.catalog = Screen("Catalog", 0)
        self.ux_map.append_screen(self.catalog)

    with it("should be the graph node for the screen"):
        expect(self.catalog.node).to(be(self.catalog))

    with it("should keep the screen on the map graph"):
        expect(self.catalog.graph).to(be(self.graph))

    with it("should record screens and belongsTo"):
        practice = self.graph.practice("ux")
        screens = [(edge.parent.name, edge.child.name) for edge in practice.edges.get("screens", [])]
        belongs = [(edge.parent.name, edge.child.name) for edge in practice.edges.get("belongsTo", [])]
        expect(screens).to(contain(("UxMap", "Catalog")))
        expect(belongs).to(contain(("Catalog", "UxMap")))

    with it("should open the same map from the graph"):
        restored = UxMap.create(self.graph)
        expect(restored.screens[0].name).to(equal("Catalog"))
