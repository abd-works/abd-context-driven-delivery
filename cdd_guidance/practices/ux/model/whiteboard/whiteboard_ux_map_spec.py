"""Claude Whiteboard UX channel - a mockup drawn as a board shows each screen and each control with the stories,
scenarios and steps it serves, and a board read back keeps them."""

import sys
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[5]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.whiteboard.whiteboard import Box, UnreadableBoard, Whiteboard  # noqa: E402

from cdd_guidance.practices.ux.model.nodes import Control, Region, Screen, Transition  # noqa: E402
from cdd_guidance.practices.ux.model.ux_map import UxMap  # noqa: E402
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import made  # noqa: E402
from cdd_guidance.practices.ux.model.whiteboard.nodes import WhiteboardUxMap  # noqa: E402
from harness.guidance.practice_formats import Written

_STORY_FILE = "story_tests/shop/fill-cart/fill_cart_story.test.md"
_STORY_LINK = f"[Add Book To Cart]({_STORY_FILE}#story-add-book-to-cart)"
_SCENARIO_LINK = f"[Add Book To Cart › Add one book]({_STORY_FILE}#scenario-add-one-book)"
_STEP_LINK = f"[Add Book To Cart › Add one book › the Customer adds 2 copies]({_STORY_FILE}#scenario-add-one-book)"


def mockup() -> UxMap:
    """Book Details, which serves a linked story, a named story, a scenario and a step, and whose Add To Cart region
    holds Quantity, which serves a step, Add to cart, which serves a story and two scenarios, and Back to list, which
    serves nothing; and Checkout, reached by the top nav Check out."""
    ux_map = UxMap.create("Bookshop")
    details = made(Screen, "Book Details", 0, layout="split-screen")
    details.show_story(_STORY_LINK)
    details.show_story("View Book")
    details.show_scenario(_SCENARIO_LINK)
    details.show_step(_STEP_LINK)
    details.attach_domain_term("Book")
    details.attach_domain_term("Cart Line")
    details.append_region(made(Region, "Book Summary", 0, area="panel"))
    add = made(Region, "Add To Cart", 1, area="body")
    quantity = made(Control, "Quantity", 0, control_type="number")
    quantity.show_step(_STEP_LINK)
    add_to_cart = made(Control, "Add to cart", 1, control_type="button")
    add_to_cart.show_story(_STORY_LINK)
    add_to_cart.show_scenario(_SCENARIO_LINK)
    add_to_cart.show_scenario("Add Book To Cart › Add a second book")
    for control in (quantity, add_to_cart, made(Control, "Back to list", 2, control_type="button")):
        add.append_control(control)
    details.append_region(add)
    checkout = Screen("Checkout", 1)
    checkout.append_region(made(Region, "Payment", 0, area="body"))
    ux_map.append_screen(details)
    ux_map.append_screen(checkout)
    ux_map.transitions.append(made(Transition, "Check out", 0, from_screen=details, to_screen=checkout, trigger="Check out", nav_type="top nav"))
    ux_map.transitions.append(made(Transition, "Back", 1, from_screen=checkout, to_screen=details, trigger="Back", nav_type="action"))
    return ux_map


def served_by(node) -> tuple[list[str], list[str], list[str]]:
    return (node.story_keys, node.scenario_keys, node.step_keys)


def text_of(board: Whiteboard, role: str, starting: str) -> str:
    """The words of the board's element of role whose words start with starting."""
    return next(element.text for element in board.elements if element.role == role and element.text.startswith(starting))


with description("a mockup drawn as a Claude Whiteboard board"):
    with before.all:
        self.text = WhiteboardUxMap.create().render(mockup())
        self.board = Whiteboard.from_text(self.text)

    with it("should draw each screen as a section titled with its name"):
        expect([section.text for section in self.board.sections if section.role == "screen"]).to(equal(["Book Details", "Checkout"]))

    with it("should draw each region as a section titled with its name"):
        expect([section.text for section in self.board.sections if section.role == "region"]).to(
            equal(["Book Summary", "Add To Cart", "Payment"])
        )

    with it("should show under a screen the stories it serves, a linked one as a markdown link"):
        expect(text_of(self.board, "serves", "**Serves**")).to(contain(f"Stories: {_STORY_LINK} · View Book"))

    with it("should show under a screen the scenarios and the steps it serves"):
        expect(text_of(self.board, "serves", "**Serves**")).to(contain(f"Scenarios: {_SCENARIO_LINK}\nSteps: {_STEP_LINK}"))

    with it("should show a control with its type and the step it serves"):
        expect(text_of(self.board, "control", "**Quantity**")).to(equal(f"**Quantity**\n*number*\nSteps: {_STEP_LINK}"))

    with it("should show a control that serves nothing with its name and type alone"):
        expect(text_of(self.board, "control", "**Back to list**")).to(equal("**Back to list**\n*button*"))

    with it("should draw each control inside its region, and each region inside its screen"):
        screen = next(section for section in self.board.sections if section.text == "Book Details")
        region = next(section for section in self.board.sections if section.text == "Add To Cart")
        cards = [element for element in self.board.shapes if element.role == "control"]
        expect((screen.holds(region), [region.holds(card) for card in cards])).to(equal((True, [True, True, True])))

    with it("should draw each transition as an arrow labelled with its trigger, and its kind of navigation when it is no action"):
        expect([arrow.label for arrow in self.board.arrows]).to(equal(["[top nav] Check out", "Back"]))

    with context("that is read back"):
        with before.all:
            self.parsed = WhiteboardUxMap.create().parse(self.text)
            self.details = self.parsed.find_screen("Book Details")
            self.controls = {control.name: control for control in self.details.regions[1].controls}

        with it("should read back the screens"):
            expect([screen.name for screen in self.parsed.screens]).to(equal(["Book Details", "Checkout"]))

        with it("should read back each screen's regions with the area each fills"):
            expect([(region.name, region.area) for region in self.details.regions]).to(equal([("Book Summary", "panel"), ("Add To Cart", "body")]))

        with it("should read back a region's controls with their types"):
            expect([(control.name, control.control_type) for control in self.details.regions[1].controls]).to(
                equal([("Quantity", "number"), ("Add to cart", "button"), ("Back to list", "button")])
            )

        with it("should read back what the screen serves, each linked one with its target"):
            expect(served_by(self.details)).to(equal(([_STORY_LINK, "View Book"], [_SCENARIO_LINK], [_STEP_LINK])))

        with it("should read back the domain terms the screen names"):
            expect(self.details.domain_terms).to(equal(["Book", "Cart Line"]))

        with it("should read back the step a control serves"):
            expect(served_by(self.controls["Quantity"])).to(equal(([], [], [_STEP_LINK])))

        with it("should read back the story and the scenarios another control serves"):
            expect(served_by(self.controls["Add to cart"])).to(
                equal(([_STORY_LINK], [_SCENARIO_LINK, "Add Book To Cart › Add a second book"], []))
            )

        with it("should give a control that serves nothing no story, scenario or step"):
            expect(served_by(self.controls["Back to list"])).to(equal(([], [], [])))

        with it("should give a screen that serves nothing no story"):
            expect(served_by(self.parsed.find_screen("Checkout"))).to(equal(([], [], [])))

        with it("should read back each transition with the screens it joins and its kind of navigation"):
            expect([(t.trigger, t.from_screen.name, t.to_screen.name, t.nav_type) for t in self.parsed.transitions]).to(
                equal([("Check out", "Book Details", "Checkout", "top nav"), ("Back", "Checkout", "Book Details", "action")])
            )

        with it("should draw the same board again from what it read"):
            expect(WhiteboardUxMap.create().render(self.parsed)).to(equal(self.text))

    with context("on which a person moved a control's card to another region and wrote a story on it"):
        with before.all:
            board = Whiteboard.from_text(self.text)
            summary = next(section for section in board.sections if section.text == "Book Summary")
            card = next(element for element in board.elements if element.role == "control" and element.text.startswith("**Back to list**"))
            card.box = Box(summary.box.x + 8, summary.box.y + 8, 40, 40)
            card.text = f"**Back to list**\n*button*\nStories: {_STORY_LINK}"
            self.parsed = WhiteboardUxMap.create().parse(board.save())
            self.summary = self.parsed.find_screen("Book Details").regions[0]

        with it("should read the control in the region its card now sits in"):
            expect([control.name for control in self.summary.controls]).to(equal(["Back to list"]))

        with it("should read the story the person wrote on the card"):
            expect(self.summary.controls[0].story_keys).to(equal([_STORY_LINK]))

    with context("that is drawn again over a board on which a person moved a screen"):
        with before.all:
            board = Whiteboard.from_text(self.text)
            moved = next(section for section in board.sections if section.text == "Checkout")
            moved.box = Box(5000, 900, moved.box.w, moved.box.h)
            self.again = Whiteboard.from_text(WhiteboardUxMap.create().render(mockup(), Written(board.save())))

        with it("should leave the screen where the person put it"):
            checkout = next(section for section in self.again.sections if section.text == "Checkout")
            expect((checkout.box.x, checkout.box.y)).to(equal((5000, 900)))


with description("a board that draws no UX screen"):
    with it("should be refused as a board no UX map is read from"):
        story_map = Whiteboard("Story Map").save()
        expect(lambda: WhiteboardUxMap.create().parse(story_map)).to(raise_error(UnreadableBoard))

    with it("should not be taken for a UX map's file"):
        expect(WhiteboardUxMap.create().reads_file(Path("story-map.whiteboard"), Whiteboard("Story Map").save())).to(equal(False))
