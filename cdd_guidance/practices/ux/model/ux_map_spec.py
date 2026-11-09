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
    return [(edge.parent.name, edge.child.name) for edge in graph.practice("ux").reading.in_graph.edges(kind)]


with description("a UxMap"):
    with context("that has screens appended"):
        with before.each:
            self.ux_map = UxMap.create(name="orders")
            self.ux_map.append_screen(Screen("Catalog", 0))
            self.ux_map.append_screen(Screen("Cart", 1))

        with it("should find a screen by name"):
            expect(self.ux_map.find_screen("Cart").name).to(equal("Cart"))

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
        screens = [(edge.parent.name, edge.child.name) for edge in practice.reading.in_graph.edges("screens")]
        belongs = [(edge.parent.name, edge.child.name) for edge in practice.reading.in_graph.edges("belongsTo")]
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


with description("a UxMap copied into a format"):
    with before.each:
        from cdd_guidance.practices.ux.model.drawio.nodes import DrawioRegion, DrawioScreen, DrawioUxMap
        from cdd_guidance.practices.ux.model.ux_map_spec_fixture import OrderingMap, outline

        self.graph = Graph()
        self.source = OrderingMap().build(UxMap.create(self.graph))
        self.copy = DrawioUxMap.create().copy_of(self.source)
        self.outline = outline
        self.screen_type = DrawioScreen
        self.region_type = DrawioRegion

    with it("should hold the same screens, regions, controls, links, and context"):
        expect(self.outline(self.copy)).to(equal(self.outline(self.source)))

    with it("should make its screens of the format's screen type"):
        expect(all(isinstance(screen, self.screen_type) for screen in self.copy.screens)).to(equal(True))

    with it("should make its regions of the format's region type"):
        regions = [region for screen in self.copy.screens for region in screen.regions]
        expect(all(isinstance(region, self.region_type) for region in regions)).to(equal(True))

    with it("should be detached, as a render writes it, with no graph made for it"):
        expect(self.copy.practice).to(equal(None))

    with it("should leave the source's graph holding the source's map alone"):
        expect(len(self.graph.practice("ux").reading.in_graph.nodes("UxMap"))).to(equal(1))

    with it("should keep the stories each screen shows by key"):
        expect([screen.story_keys for screen in self.copy.screens]).to(equal([screen.story_keys for screen in self.source.screens]))
