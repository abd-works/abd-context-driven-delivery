"""Draw.io UX channel - CLI Detailed IA + Site Map against the UxMap sketch."""

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from expects import be, contain, equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from cdd_guidance.practices.ux.model.drawio import nodes as drawio_nodes
from cdd_guidance.practices.ux.model.drawio.nodes import DrawioCliFailed, DrawioCliMissing, DrawioCliTimedOut, DrawioUxMap
from harness.drawio import UnreadableDrawio
from cdd_guidance.practices.ux.model.nodes import Control, Region, Screen, StoryDemoControl, StoryStep, Transition
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import made
from harness.guidance.practice_formats import Written


class SpecFixture:
    def site_map(self) -> DrawioUxMap:
        ux_map = DrawioUxMap.create()
        ux_map.scope = "Play Core Mechanics"
        ux_map.story_references = [
            "../practices/stories/update_ability_rank_stories.js",
        ]

        sheet = Screen("Character Sheet", 0)
        sheet.apply_layout("sidebar")
        sheet.append_region(made(Region, "panel", 0, area="panel"))
        sheet.append_region(made(Region, "body", 1, area="body"))
        sheet.show_story("Update Ability Rank")
        sheet.attach_domain_term("Character")

        abilities = made(Screen, "Character Sheet - Abilities", 1, chrome_of=sheet)
        abilities.inactive_tabs = ["Identities", "Movements"]

        ux_map.append_screen(sheet)
        ux_map.append_screen(abilities)
        ux_map.transitions.append(
            made(Transition, "selects Abilities tab", 0, from_screen=sheet, to_screen=abilities, trigger="selects Abilities tab", nav_type="action")
        )
        return ux_map


    def mockup(self) -> DrawioUxMap:
        """Book Details, whose Add To Cart region holds a number and two buttons, and Checkout, whose Payment region is
        a form."""
        ux_map = DrawioUxMap.create()
        details = Screen("Book Details", 0)
        details.append_region(made(Region, "Book Summary", 0, area="body"))
        add = made(Region, "Add To Cart", 1, area="body")
        for order, (name, kind) in enumerate([("Quantity", "number"), ("Add to cart", "button"), ("Back to list", "button")]):
            add.append_control(made(Control, name, order, control_type=kind))
        details.append_region(add)
        checkout = Screen("Checkout", 1)
        payment = made(Region, "Payment", 0, area="body")
        for order, (name, kind) in enumerate([("Street", "text"), ("Country", "dropdown"), ("Save this card", "checkbox"), ("Pay", "button")]):
            payment.append_control(made(Control, name, order, control_type=kind))
        checkout.append_region(payment)
        ux_map.append_screen(details)
        ux_map.append_screen(checkout)
        ux_map.transitions.append(made(Transition, "Check out", 0, from_screen=details, to_screen=checkout, trigger="Check out", nav_type="top nav"))
        return ux_map


    def mockup_serving_stories(self) -> DrawioUxMap:
        """The mockup, whose Book Details serves a linked story, a scenario and a step, and whose Quantity and Add to
        cart controls serve a step and a scenario of their own."""
        ux_map = self.mockup()
        details = ux_map.find_screen("Book Details")
        details.show_story(_STORY_LINK)
        details.show_story("View Book & Cover")
        details.show_scenario(_SCENARIO_LINK)
        details.show_step(_STEP_LINK)
        quantity, add_to_cart, _back = details.regions[1].controls
        quantity.show_step(_STEP_LINK)
        add_to_cart.show_story(_STORY_LINK)
        add_to_cart.show_scenario(_SCENARIO_LINK)
        add_to_cart.show_scenario("Add Book To Cart › Add a second book")
        return ux_map


    def mockup_with_story_demo(self) -> DrawioUxMap:
        """Checkout, whose Payment form ends in a Story Demo control named Pay Button and labelled Pay, which runs a
        story step and serves a story."""
        ux_map = DrawioUxMap.create()
        checkout = Screen("Checkout", 0)
        payment = made(Region, "Payment", 0, area="body")
        payment.append_control(made(Control, "Card Number", 0, control_type="text", label="Card number"))
        pay = made(StoryDemoControl, "Pay Button", 1, control_type="button", label="Pay", story_steps=[StoryStep("when", "the Customer pays")])
        pay.show_story("Pay For Order")
        payment.append_control(pay)
        checkout.append_region(payment)
        ux_map.append_screen(checkout)
        return ux_map


_STORY_FILE = "story_tests/shop/fill-cart/fill_cart_story.test.md"
_STORY_LINK = f"[Add Book To Cart]({_STORY_FILE}#story-add-book-to-cart)"
_SCENARIO_LINK = f"[Add Book To Cart › Add one book]({_STORY_FILE}#scenario-add-one-book)"
_STEP_LINK = f"[Add Book To Cart › Add one book › the Customer adds 2 copies]({_STORY_FILE}#scenario-add-one-book)"


def served_by(node) -> tuple[list[str], list[str], list[str]]:
    return (node.story_keys, node.scenario_keys, node.step_keys)


def controls_of(ux_map: DrawioUxMap, screen: str, region: str) -> list[tuple[str, str]]:
    held = next(found for found in ux_map.find_screen(screen).regions if found.name == region)
    return [(control.name, control.control_type) for control in held.controls]


fixture = SpecFixture()


with description("a UX map drawn as a draw.io information architecture"):
    with before.each:
        self.source = fixture.site_map()
        self.rendered = DrawioUxMap.create().render(self.source)

    with it("should emit drawio-ux two-page mxfile"):
        expect(self.rendered.startswith("<mxfile")).to(equal(True))
        expect('name="Detailed IA"' in self.rendered).to(equal(True))
        expect('name="Site Map"' in self.rendered).to(equal(True))
        expect("host=\"drawio-ux\"" in self.rendered).to(equal(True))

    with context("that is read back"):
        with before.each:
            self.parsed = DrawioUxMap.create().parse(self.rendered)

        with it("should read back the screen names from the Site Map page"):
            names = [screen.name for screen in self.parsed.screens]
            expect(names).to(equal(["Character Sheet", "Character Sheet - Abilities"]))

        with it("should read back the region titles from Detailed IA"):
            expect([region.name for region in self.parsed.find_screen("Character Sheet").regions]).to(
                equal(["panel", "body"])
            )

        with it("should read back the transition trigger"):
            expect([transition.trigger for transition in self.parsed.transitions]).to(equal(["selects Abilities tab"]))

        with it("should link the transition to the screens on the read map"):
            expect(self.parsed.transitions[0].to_screen).to(be(self.parsed.find_screen("Character Sheet - Abilities")))

        with it("should bring its regions onto the graph that adopts the read map"):
            from harness.graph.graph import Graph

            graph = Graph()
            self.parsed.join(graph.practices.named("ux"))
            expect(self.parsed.find_screen("Character Sheet").regions[0].graph).to(be(graph))

        with it("should read back the stories the drawing shows under the screen"):
            expect(self.parsed.find_screen("Character Sheet").story_keys).to(equal(["Update Ability Rank"]))

        with it("should read back the domain terms the drawing shows under the screen"):
            expect(self.parsed.find_screen("Character Sheet").domain_terms).to(equal(["Character"]))

        with it("should read back the screen's layout"):
            expect(self.parsed.find_screen("Character Sheet").layout).to(equal("sidebar"))

        with it("should read back the area each region fills"):
            expect([region.area for region in self.parsed.find_screen("Character Sheet").regions]).to(equal(["panel", "body"]))

    with context("of a mockup whose regions hold controls, that is read back"):
        with before.each:
            self.parsed = DrawioUxMap.create().parse(DrawioUxMap.create().render(fixture.mockup()))

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
                equal([("Street", "text"), ("Country", "dropdown"), ("Save this card", "checkbox"), ("Pay", "button")])
            )

        with it("should read back a transition's kind of navigation"):
            expect(self.parsed.transitions[0].nav_type).to(equal("top nav"))

    with context("of a mockup whose screen and controls serve stories, scenarios and steps, that is read back"):
        with before.each:
            self.parsed = DrawioUxMap.create().parse(DrawioUxMap.create().render(fixture.mockup_serving_stories()))
            self.details = self.parsed.find_screen("Book Details")
            self.controls = {control.name: control for control in self.details.regions[1].controls}

        with it("should read back what the screen serves, each linked one with its target"):
            expect(served_by(self.details)).to(equal(([_STORY_LINK, "View Book & Cover"], [_SCENARIO_LINK], [_STEP_LINK])))

        with it("should read back the step a control serves"):
            expect(served_by(self.controls["Quantity"])).to(equal(([], [], [_STEP_LINK])))

        with it("should read back the story and the scenarios another control serves"):
            expect(served_by(self.controls["Add to cart"])).to(
                equal(([_STORY_LINK], [_SCENARIO_LINK, "Add Book To Cart › Add a second book"], []))
            )

        with it("should give a control that serves nothing no story, scenario or step"):
            expect(served_by(self.controls["Back to list"])).to(equal(([], [], [])))

        with it("should still read back only the regions the mockup has"):
            expect([region.name for region in self.details.regions]).to(equal(["Book Summary", "Add To Cart"]))

    with context("of a mockup whose controls are named otherwise than they are labelled, one a Story Demo control, that is read back"):
        with before.each:
            self.parsed = DrawioUxMap.create().parse(DrawioUxMap.create().render(fixture.mockup_with_story_demo()))
            self.controls = self.parsed.find_screen("Checkout").regions[0].controls

        with it("should read back each control's name"):
            expect([control.name for control in self.controls]).to(equal(["Card Number", "Pay Button"]))

        with it("should read back the label each control shows"):
            expect([control.label for control in self.controls]).to(equal(["Card number", "Pay"]))

        with it("should read back the story the Story Demo control serves"):
            expect(self.controls[1].story_keys).to(equal(["Pay For Order"]))

    with context("of a mockup, drawn again over a drawing that shows what the mockup does not"):
        with before.each:
            held = fixture.mockup_serving_stories()
            held.find_screen("Book Details").regions[0].append_control(made(Control, "Cover", 0, control_type="image"))
            held.append_screen(Screen("Wish List", 2))
            previous = DrawioUxMap.create().render(held)
            self.parsed = DrawioUxMap.create().parse(DrawioUxMap.create().render(fixture.mockup(), Written(previous)))
            self.details = self.parsed.find_screen("Book Details")

        with it("should keep the screen only the drawing showed"):
            expect([screen.name for screen in self.parsed.screens]).to(equal(["Book Details", "Checkout", "Wish List"]))

        with it("should keep the control only the drawing showed, in its region"):
            expect(controls_of(self.parsed, "Book Details", "Book Summary")).to(equal([("Cover", "image")]))

        with it("should keep what the drawing said a screen and a control serve"):
            expect((served_by(self.details), served_by(self.details.regions[1].controls[0]))).to(
                equal((([_STORY_LINK, "View Book & Cover"], [_SCENARIO_LINK], [_STEP_LINK]), ([], [], [_STEP_LINK])))
            )

    with context("that is not XML"):
        with it("should refuse it as an unreadable diagram"):
            expect(lambda: DrawioUxMap.create().parse("<mxfile><diagram>")).to(raise_error(UnreadableDrawio))

    with context("with a command line that runs past its timeout"):
        with before.each:
            self.writer = DrawioUxMap.create()
            self.writer.cli_timeout_seconds = 0.001

        with it("should stop it and say it timed out"):
            expect(lambda: self.writer.render(self.source)).to(raise_error(DrawioCliTimedOut))

    with context("with no command line vendored beside it"):
        with it("should refuse to draw, naming where the command line should be"):
            with patch.object(drawio_nodes, "_CLI", Path("missing") / "drawio_ux.mjs"):
                expect(lambda: DrawioUxMap.create().render(self.source)).to(raise_error(DrawioCliMissing, contain("drawio_ux.mjs")))

    with context("with a command line that fails"):
        with it("should refuse to draw, with what the command line said"):
            failed = subprocess.CompletedProcess([], 1, stdout="", stderr="layout broke")
            with patch.object(drawio_nodes.subprocess, "run", return_value=failed):
                expect(lambda: DrawioUxMap.create().render(self.source)).to(raise_error(DrawioCliFailed, contain("layout broke")))

    with context("that holds three screens side by side with transitions between them"):
        with before.each:
            ux_map = DrawioUxMap.create()
            screens = {}
            for order, name in enumerate(["Board", "Editor", "Explorer"]):
                screens[name] = Screen(name, order)
                screens[name].append_region(made(Region, "body", 0, area="body"))
                ux_map.append_screen(screens[name])
            for order, (source, target) in enumerate([("Board", "Explorer"), ("Explorer", "Board"), ("Editor", "Explorer")]):
                ux_map.transitions.append(made(Transition, f"go {order}", order, from_screen=screens[source], to_screen=screens[target], trigger=f"go {order}", nav_type="action"))
            page = ET.fromstring(DrawioUxMap.create().render(ux_map)).find(".//diagram[@name='Detailed IA']")
            cells = page.findall(".//mxCell")
            self.screen_top = min(
                float(cell.find("mxGeometry").get("y"))
                for cell in cells if cell.get("value") in ("Board", "Editor", "Explorer")
            )
            self.lanes = [
                [float(point.get("y")) for point in cell.findall(".//mxPoint")]
                for cell in cells if cell.get("edge") == "1"
            ]

        with it("should route every transition above the screens"):
            expect(all(points and max(points) < self.screen_top for points in self.lanes)).to(equal(True))

        with it("should give each transition a lane of its own"):
            expect(len({points[0] for points in self.lanes if points})).to(equal(len(self.lanes)))
