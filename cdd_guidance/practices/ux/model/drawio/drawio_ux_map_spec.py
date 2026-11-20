"""Draw.io UX channel - what a drawing already written reads back as, and what a region tells the command line to
draw. No example here starts the command line: drawio_ux_map_heavy_spec.py draws through it."""

import sys
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.drawio.nodes import DrawioRegion, DrawioUxMap
from cdd_guidance.practices.ux.model.nodes import Control, Region, Screen
from cdd_guidance.practices.ux.model.ux_map import UxMap
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import made

_ROW = "fillColor=#ffffff;strokeColor=none;strokeWidth=0;"
_FRAMED = "fillColor=#ffffff;strokeColor=#000000;strokeWidth=1;"
_STRIP = "fillColor=#f0f0f0;strokeColor=#000000;strokeWidth=1;"


def cell(cell_id: str, value: str, style: str, parent: str = "1", x: int = 0, y: int = 0) -> str:
    return (
        f'<mxCell id="{cell_id}" value="{value}" style="{style}" vertex="1" parent="{parent}">'
        f'<mxGeometry x="{x}" y="{y}" width="100" height="20" as="geometry"/></mxCell>'
    )


def drawing(detailed: str, edge_style: str = "html=1;") -> str:
    """A two-page drawing of Book Details and Checkout, with detailed as the cells of the Detailed IA page."""
    return (
        '<mxfile host="drawio-ux">'
        '<diagram id="ia-diagram" name="Detailed IA"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
        f"{detailed}</root></mxGraphModel></diagram>"
        '<diagram id="site-map" name="Site Map"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
        f'{cell("5001", "Book Details", "rounded=1;")}{cell("5002", "Checkout", "rounded=1;", x=300)}'
        f'<mxCell id="5003" value="Check out" style="{edge_style}" edge="1" source="5001" target="5002" parent="1">'
        '<mxGeometry relative="1" as="geometry"/></mxCell>'
        "</root></mxGraphModel></diagram></mxfile>"
    )


# The Detailed IA page as the command line draws Book Details: a list region whose row is drawn twice, its action
# strip, and the callout under the screen's box; then Checkout with a form.
_DRAWN = drawing(
    cell("2", "Book Details", "strokeWidth=2;uxLayout=split-screen;", x=50, y=200)
    + cell("3", "Checkout", "strokeWidth=2;", x=890, y=200)
    + cell("4", "Book Summary", _FRAMED + "fontStyle=2;uxArea=panel;", parent="2")
    + cell("5", "&lt;b&gt;Add To Cart&lt;/b&gt;", _FRAMED + "uxArea=body;", parent="2")
    + cell("6", "Add to cart · Back to list", _STRIP + "uxControls=button,button;", parent="2")
    + cell("7", "Quantity", _ROW + "uxControls=number;", parent="2")
    + cell("8", "Quantity", _ROW + "uxControls=number;", parent="2")
    + cell("9", "&lt;b&gt;Stories:&lt;/b&gt; Add Book To Cart · View Book&lt;br&gt;&lt;b&gt;Domain terms:&lt;/b&gt; Book · Cart Line",
           "text;html=1;strokeColor=none;fillColor=none;", x=50, y=420)
    + cell("10", "&lt;b&gt;Payment&lt;/b&gt;", _FRAMED, parent="3")
    + cell("11", "Street", _ROW + "uxControls=text;", parent="3")
    + cell("12", "Country", _ROW + "uxControls=dropdown;", parent="3")
    + cell("13", "[Pay]", _ROW + "uxControls=button;", parent="3")
    + cell("14", "&lt;b&gt;Stories:&lt;/b&gt; Pay For Order", "text;html=1;strokeColor=none;fillColor=none;", x=890, y=420),
    edge_style="html=1;uxNav=top nav;",
)

# The same screen as a drawing made before the command line kept control types, or drawn by hand.
_DRAWN_WITHOUT_TYPES = drawing(
    cell("2", "Book Details", "strokeWidth=2;", x=50, y=200)
    + cell("5", "&lt;b&gt;Add To Cart&lt;/b&gt;", _FRAMED, parent="2")
    + cell("6", "Add to cart · Back to list", _STRIP, parent="2")
    + cell("7", "Quantity", _ROW, parent="2"),
    edge_style="html=1;dashed=1;",
)


def controls_of(ux_map: DrawioUxMap, screen: str, region: str) -> list[tuple[str, str]]:
    held = next(found for found in ux_map.find_screen(screen).regions if found.name == region)
    return [(control.name, control.control_type) for control in held.controls]


with description("a UX map drawn as a draw.io information architecture"):
    with context("that is read back"):
        with before.each:
            self.parsed = DrawioUxMap.create().parse(_DRAWN)
            self.details = self.parsed.find_screen("Book Details")

        with it("should read back the stories the drawing shows under the screen"):
            expect(self.details.story_keys).to(equal(["Add Book To Cart", "View Book"]))

        with it("should read back the domain terms the drawing shows under the screen"):
            expect(self.details.domain_terms).to(equal(["Book", "Cart Line"]))

        with it("should give each screen the stories under its own box"):
            expect(self.parsed.find_screen("Checkout").story_keys).to(equal(["Pay For Order"]))

        with it("should read back the screen's layout"):
            expect(self.details.layout).to(equal("split-screen"))

        with it("should read back the area each region fills"):
            expect([region.area for region in self.details.regions]).to(equal(["panel", "body"]))

        with it("should read back a transition's kind of navigation"):
            expect(self.parsed.transitions[0].nav_type).to(equal("top nav"))

    with context("of a mockup whose regions hold controls, that is read back"):
        with before.each:
            self.parsed = DrawioUxMap.create().parse(_DRAWN)

        with it("should read back only the regions the mockup has"):
            expect([region.name for region in self.parsed.find_screen("Book Details").regions]).to(
                equal(["Book Summary", "Add To Cart"])
            )

        with it("should read back a region's controls with their types, its buttons last"):
            expect(controls_of(self.parsed, "Book Details", "Add To Cart")).to(
                equal([("Quantity", "number"), ("Add to cart", "button"), ("Back to list", "button")])
            )

        with it("should read back a form's fields and its button"):
            expect(controls_of(self.parsed, "Checkout", "Payment")).to(
                equal([("Street", "text"), ("Country", "dropdown"), ("Pay", "button")])
            )

    with context("drawn without the types of its controls, that is read back"):
        with before.each:
            self.parsed = DrawioUxMap.create().parse(_DRAWN_WITHOUT_TYPES)

        with it("should read an action strip's labels as buttons and a row's label as a control of no known type"):
            expect(controls_of(self.parsed, "Book Details", "Add To Cart")).to(
                equal([("Quantity", ""), ("Add to cart", "button"), ("Back to list", "button")])
            )

        with it("should read a dashed transition as a tab"):
            expect(self.parsed.transitions[0].nav_type).to(equal("tab"))


with description("a region of a UX map drawn as draw.io"):
    with context("that holds a number and two buttons"):
        with before.each:
            def map_holding(region):
                ux_map = UxMap.create()
                screen = Screen("Book Details", 0)
                screen.append_region(region)
                ux_map.append_screen(screen)
                return ux_map

            self.map_holding = map_holding
            region = made(Region, "Add To Cart", 0, area="body")
            for order, (name, kind) in enumerate([("Quantity", "number"), ("Add to cart", "button"), ("Back to list", "button")]):
                region.append_control(made(Control, name, order, control_type=kind))
            self.record = DrawioUxMap.create().copy_of(self.map_holding(region)).screens[0].regions[0].cli_record()

        with it("should be drawn as a list that shows every control, each with its type"):
            expect((self.record["type"], self.record["fields"], self.record["fieldKinds"], self.record["actions"])).to(
                equal(("list", ["Quantity"], ["number"], ["Add to cart", "Back to list"]))
            )

    with context("that holds no control"):
        with it("should be drawn as chrome in its area"):
            record = made(DrawioRegion, "Main Nav", 0, area="header").cli_record()
            expect((record["type"], record["uxArea"])).to(equal(("chrome", "header")))
