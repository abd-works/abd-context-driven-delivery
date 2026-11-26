"""A UX map rendered onto a document or a drawing that is already there keeps what only that file holds: a person's
notes and headings in the UX context, the cards, notes and associations a person put on the board, and where they put
them. The drawing made through the drawio-ux command line is in ``drawio_ux_map_heavy_spec.py``."""

import sys
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.whiteboard.whiteboard import Box, Whiteboard  # noqa: E402

from cdd_guidance.practices.ux.model.markdown.nodes import MarkdownUxMap  # noqa: E402
from cdd_guidance.practices.ux.model.nodes import ContentType, Control, NavComponent, Region, Screen, Transition  # noqa: E402
from cdd_guidance.practices.ux.model.ux_map import UxMap  # noqa: E402
from cdd_guidance.practices.ux.model.ux_map_spec_fixture import made  # noqa: E402
from cdd_guidance.practices.ux.model.whiteboard.nodes import WhiteboardUxMap  # noqa: E402
from harness.guidance.practice_formats import Written

_STORY_LINK = "[Add Book To Cart](story_tests/shop/fill_cart_story.test.md#story-add-book-to-cart)"
_PERSONS_LINK = "[View Book](story_tests/shop/view_book_story.test.md#story-view-book)"

_UX_CONTEXT = (
    "# UX context\n\n"
    "Scope: Browse Books\n\n"
    "The shop sells to walk-in customers only.\n\n"
    "## Invariants\n- A Cart Line shows one Book and its quantity.\n\n"
    "## Open questions\n- Does a gift card pay for shipping?\n\n"
    "## Notes\n- A Customer reaches the Cart from every screen.\n"
)


def mockup() -> UxMap:
    """Book Details, whose region Add To Cart holds Quantity, which serves a story, and Back to list; and Checkout."""
    ux_map = UxMap.create("Bookshop")
    details = Screen("Book Details", 0)
    details.attach_domain_term("Book")
    details.append_region(made(Region, "Book Summary", 0, area="panel"))
    add = made(Region, "Add To Cart", 1, area="body")
    quantity = made(Control, "Quantity", 0, control_type="number")
    quantity.show_story(_STORY_LINK)
    add.append_control(quantity)
    add.append_control(made(Control, "Back to list", 1, control_type="button"))
    details.append_region(add)
    checkout = Screen("Checkout", 1)
    ux_map.append_screen(details)
    ux_map.append_screen(checkout)
    ux_map.transitions.append(made(Transition, "Check out", 0, from_screen=details, to_screen=checkout, trigger="Check out", nav_type="action"))
    return ux_map


def context_of(scope: str, invariants: list[str], notes: list[str]) -> UxMap:
    ux_map = UxMap.create("Bookshop")
    ux_map.scope = scope
    ux_map.context.invariants = invariants
    ux_map.context.notes = notes
    return ux_map


def lines_lost(before: str, after: str) -> list[str]:
    """Each line of before that carried content and is nowhere in after."""
    held = after.splitlines()
    return [line for line in before.splitlines() if line.strip() and not any(line.strip() in kept for kept in held)]


with description("a UX map rendered onto the UX context a person wrote"):
    with context("with an invariant and a note the file does not hold, and a new scope"):
        with before.all:
            source = context_of("Browse Books, Fill Cart", ["A Book has one price."], ["Checkout is one page."])
            self.rendered = MarkdownUxMap.create().render(source, Written(_UX_CONTEXT))

        with it("should keep every line the person wrote, the scope line going on to say the map's scope"):
            expect(lines_lost(_UX_CONTEXT, self.rendered)).to(equal([]))

        with it("should write the map's scope where the scope was"):
            expect(self.rendered).to(contain("# UX context\n\nScope: Browse Books, Fill Cart\n\nThe shop sells"))

        with it("should add the invariant after the invariants the file holds"):
            expect(self.rendered).to(contain("## Invariants\n- A Cart Line shows one Book and its quantity.\n- A Book has one price.\n"))

        with it("should add the note after the notes the file holds"):
            expect(self.rendered).to(contain("## Notes\n- A Customer reaches the Cart from every screen.\n- Checkout is one page.\n"))

        with it("should leave the heading a person added, and what is under it, where it was"):
            expect(self.rendered).to(contain("## Open questions\n- Does a gift card pay for shipping?\n\n## Notes"))

        with it("should change nothing when the same map is rendered onto it again"):
            source = context_of("Browse Books, Fill Cart", ["A Book has one price."], ["Checkout is one page."])
            expect(MarkdownUxMap.create().render(source, Written(self.rendered))).to(equal(self.rendered))

    with context("with what the file already holds, and nothing more"):
        with it("should leave the file exactly as it is"):
            source = context_of("Browse Books", ["A Cart Line shows one Book and its quantity."], ["A Customer reaches the Cart from every screen."])
            expect(MarkdownUxMap.create().render(source, Written(_UX_CONTEXT))).to(equal(_UX_CONTEXT))

    with context("with an invariant, onto a file that has no invariants yet"):
        with it("should add an Invariants section after what the file holds"):
            rendered = MarkdownUxMap.create().render(context_of("", ["A Book has one price."], []), Written("# UX context\n\nScope: Browse Books\n"))
            expect(rendered).to(equal("# UX context\n\nScope: Browse Books\n\n## Invariants\n- A Book has one price.\n"))


with description("a mockup rendered onto the board a person worked on"):
    with before.all:
        board = Whiteboard.from_text(WhiteboardUxMap.create().render(mockup()))
        sections = {section.text: section for section in board.sections}
        cards = {element.text.splitlines()[0]: element for element in board.elements if element.role == "control"}
        # The person wrote a story on a card, put a card of their own in Book Summary, stuck a note on the board, drew
        # a screen of their own, and moved Checkout.
        cards["**Back to list**"].text += f"\nStories: {_PERSONS_LINK}"
        summary = sections["Book Summary"].box
        saved = board.save().rstrip()[:-1].rstrip()[:-1].rstrip()
        own = (
            f',\n  "control.own": {{"type": "shape", "text": "**Cover**\\n*image*", "x": {summary.x + 8}, "y": {summary.y + 8}, "w": 40, "h": 40}}'
            ',\n  "sticker1": {"type": "note", "text": "ask Dana about gift cards", "x": 5, "y": 5}'
            ',\n  "screen.own": {"type": "container", "text": "Wish List", "x": 4000, "y": 100, "w": 300, "h": 200}\n }\n}'
        )
        self.worked_on = Whiteboard.from_text(saved + own)
        moved = next(section for section in self.worked_on.sections if section.text == "Checkout")
        moved.box = Box(2500, 700, moved.box.w, moved.box.h)
        self.previous = self.worked_on.save()
        self.rendered = WhiteboardUxMap.create().render(mockup(), Written(self.previous))
        self.board = Whiteboard.from_text(self.rendered)
        self.read = WhiteboardUxMap.create().parse(self.rendered)

    with it("should keep the story the person wrote on a control's card, beside what the mockup's control serves"):
        back = self.read.find_screen("Book Details").regions[1].controls[1]
        expect((back.name, back.story_keys)).to(equal(("Back to list", [_PERSONS_LINK])))

    with it("should keep the card the person put in a region, in that region"):
        expect([(control.name, control.control_type) for control in self.read.find_screen("Book Details").regions[0].controls]).to(equal([("Cover", "image")]))

    with it("should keep the note the person stuck on the board"):
        expect(self.board.element("sticker1").record).to(equal({"type": "note", "text": "ask Dana about gift cards", "x": 5, "y": 5}))

    with it("should keep the screen the person drew"):
        expect([screen.name for screen in self.read.screens]).to(equal(["Book Details", "Checkout", "Wish List"]))

    with it("should keep Checkout where the person moved it"):
        checkout = next(section for section in self.board.sections if section.text == "Checkout")
        expect((checkout.box.x, checkout.box.y)).to(equal((2500, 700)))

    with it("should still draw what the mockup holds"):
        expect(self.read.find_screen("Book Details").regions[1].controls[0].story_keys).to(equal([_STORY_LINK]))

    with it("should change nothing when the same mockup is rendered onto it again"):
        expect(WhiteboardUxMap.create().render(mockup(), Written(self.rendered))).to(equal(self.rendered))

    with context("after the mockup loses a control the board still draws"):
        with before.all:
            smaller = mockup()
            smaller.find_screen("Book Details").regions[1].controls.refill([smaller.find_screen("Book Details").regions[1].controls[0]])
            self.after = WhiteboardUxMap.create().parse(WhiteboardUxMap.create().render(smaller, Written(self.rendered)))

        with it("should keep the control's card on the board, with the story written on it"):
            kept = self.after.find_screen("Book Details").regions[1].controls
            expect([(control.name, control.story_keys) for control in kept]).to(equal([("Quantity", [_STORY_LINK]), ("Back to list", [_PERSONS_LINK])]))


with description("a UX map that takes what only another map of the same screens holds"):
    with before.all:
        self.drawn = mockup()
        held = mockup()
        details = held.find_screen("Book Details")
        details.show_story(_PERSONS_LINK)
        details.attach_domain_term("Cart Line")
        details.regions[1].controls[1].show_story(_PERSONS_LINK)
        details.regions[0].append_control(made(Control, "Cover", 0, control_type="image"))
        details.append_region(made(Region, "Reviews", 2, area="footer"))
        wish_list = Screen("Wish List", 2)
        held.append_screen(wish_list)
        held.transitions.append(made(Transition, "Save for later", 1, from_screen=details, to_screen=wish_list, trigger="Save for later", nav_type="action"))
        held.content_types.append(made(ContentType, "Book", 0, hierarchy="Book List > Book", key_actions=["Add to cart"]))
        held.nav_components.append(made(NavComponent, "Main Nav", 0, ux_type="top nav", destinations=[details, wish_list]))
        self.drawn.keep_what_only(held)
        self.details = self.drawn.find_screen("Book Details")

    with it("should serve the story only the other map's screen serves, after its own"):
        expect(self.details.story_keys).to(equal([_PERSONS_LINK]))

    with it("should name the domain term only the other map's screen names, after its own"):
        expect(self.details.domain_terms).to(equal(["Book", "Cart Line"]))

    with it("should serve the story only the other map's control serves"):
        expect(self.details.regions[1].controls[1].story_keys).to(equal([_PERSONS_LINK]))

    with it("should hold the control only the other map's region holds, with its type"):
        expect([(control.name, control.control_type) for control in self.details.regions[0].controls]).to(equal([("Cover", "image")]))

    with it("should hold the region only the other map's screen holds, with its area"):
        expect([(region.name, region.area) for region in self.details.regions]).to(equal([("Book Summary", "panel"), ("Add To Cart", "body"), ("Reviews", "footer")]))

    with it("should hold the screen only the other map holds"):
        expect([screen.name for screen in self.drawn.screens]).to(equal(["Book Details", "Checkout", "Wish List"]))

    with it("should hold the transition only the other map holds, joining its own screens"):
        expect([(t.trigger, t.from_screen is self.details, t.to_screen.name) for t in self.drawn.transitions]).to(
            equal([("Check out", True, "Checkout"), ("Save for later", True, "Wish List")])
        )

    with it("should hold the content type only the other map holds"):
        expect([(kind.name, kind.hierarchy, kind.key_actions) for kind in self.drawn.content_types]).to(equal([("Book", "Book List > Book", ["Add to cart"])]))

    with it("should hold the nav component only the other map holds, reaching its own screens"):
        nav = self.drawn.nav_components[0]
        expect((nav.name, nav.ux_type, [screen is self.drawn.find_screen(screen.name) for screen in nav.destinations])).to(equal(("Main Nav", "top nav", [True, True])))

    with it("should take nothing more when it takes from the same map again"):
        before_again = len(self.details.regions[0].controls), len(self.drawn.transitions)
        self.drawn.keep_what_only(mockup())
        expect((len(self.details.regions[0].controls), len(self.drawn.transitions))).to(equal(before_again))
