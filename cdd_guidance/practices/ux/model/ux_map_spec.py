"""BDD spec for UxMap - screens, references, story name aggregation."""

import sys
from pathlib import Path

from expects import be, contain, equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph import Graph

from cdd_guidance.practices.ux.model.nodes import Control, Interaction, Region, Screen, Transition
from cdd_guidance.practices.ux.model.ux_map import ScreenNotOnMap, UxMap


def edge_pairs(graph, kind):
    return [(edge.parent.name, edge.child.name) for edge in graph.edges_of(graph.practice("ux"), kind)]


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

        with it("should say the screen is not on the map when it is missing"):
            expect(lambda: self.ux_map.find_screen("Missing")).to(raise_error(ScreenNotOnMap))

    with context("that holds story references and screen story names"):
        with before.each:
            self.ux_map = UxMap.create()
            self.ux_map.story_references = ["stories/place_order.js"]
            sheet = Screen("Catalog", 0)
            sheet.show_story("Browse Product Catalog")
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
        screens = [(edge.parent.name, edge.child.name) for edge in practice.graph.edges_of(practice, "screens")]
        belongs = [(edge.parent.name, edge.child.name) for edge in practice.graph.edges_of(practice, "belongsTo")]
        expect(screens).to(contain(("UxMap", "Catalog")))
        expect(belongs).to(contain(("Catalog", "UxMap")))

    with context("with a screen that holds regions, controls, and interactions"):
        with before.each:
            self.list_region = Region("product list", 0, "body")
            self.browse = Control("Browse", 0, "button")
            self.open_cart = Interaction("open cart", 0, "click")
            self.browse.append_interaction(self.open_cart)
            self.list_region.append_control(self.browse)
            self.catalog.append_region(self.list_region)

        with it("should keep the region on the map graph"):
            expect(self.list_region.graph).to(be(self.graph))

        with it("should keep the control on the map graph"):
            expect(self.browse.graph).to(be(self.graph))

        with it("should keep the interaction on the map graph"):
            expect(self.open_cart.graph).to(be(self.graph))

        with it("should record regions, controls, and interactions"):
            expect(edge_pairs(self.graph, "regions") + edge_pairs(self.graph, "controls")
                   + edge_pairs(self.graph, "interactions")).to(equal([
                ("Catalog", "product list"), ("product list", "Browse"), ("Browse", "open cart"),
            ]))

        with it("should record that each belongs to its owner"):
            expect(edge_pairs(self.graph, "belongsTo")).to(contain(
                ("product list", "Catalog"), ("Browse", "product list"), ("open cart", "Browse"),
            ))

    with context("with a transition between two screens"):
        with before.each:
            self.cart = Screen("Cart", 1)
            self.ux_map.append_screen(self.cart)
            self.opens_cart = Transition("opens cart", 0, self.catalog, self.cart)
            self.ux_map.transitions.append(self.opens_cart)

        with it("should keep the transition on the map graph"):
            expect(self.opens_cart.graph).to(be(self.graph))

        with it("should record the transition on the map"):
            expect(edge_pairs(self.graph, "transitions")).to(equal([("UxMap", "opens cart")]))

        with it("should keep its link when a screen is renamed"):
            self.cart.name = "Basket"
            expect(self.opens_cart.to_screen.name).to(equal("Basket"))
