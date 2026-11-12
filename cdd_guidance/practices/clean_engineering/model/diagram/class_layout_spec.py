"""Class cards and their arrows — where cards sit and how arrows find their way between them."""
from expects import be_above, be_false, be_true, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.diagram.class_layout import (
    ArrowRouter,
    CardPlacement,
    CardSpacing,
    DiagramArrow,
    paths_cross,
)
from cdd_guidance.practices.clean_engineering.model.diagram.diagram_node import DiagramClass
from cdd_guidance.practices.clean_engineering.model.diagram.geometry import Geometry


def _card(name, group="sales", box=(0, 0, 200, 100)):
    card = DiagramClass(name=name)
    card.cell_id = name
    card.group = group
    card.geometry = Geometry(*box)
    return card


def _hub_with_spokes():
    cards = [_card(name) for name in ("Order", "Line", "Payment", "Refund", "Customer", "Address")]
    arrows = [
        DiagramArrow("Order", "Line", "composition"),
        DiagramArrow("Order", "Payment", "association"),
        DiagramArrow("Refund", "Payment", "inheritance"),
        DiagramArrow("Order", "Customer", "association"),
        DiagramArrow("Customer", "Address", "composition"),
        DiagramArrow("Refund", "Order", "association"),
    ]
    return cards, arrows


def _laid_out():
    cards, arrows = _hub_with_spokes()
    CardPlacement(cards, arrows).place()
    return {card.cell_id: card for card in cards}, ArrowRouter(cards, arrows).route()


def _passes_through(path, card):
    card = card.geometry
    for a, b in zip(path, path[1:]):
        if (
            min(a[0], b[0]) < card.x + card.width
            and max(a[0], b[0]) > card.x
            and min(a[1], b[1]) < card.y + card.height
            and max(a[1], b[1]) > card.y
        ):
            return True
    return False


with description("a class diagram page"):
    with context("with cards placed from their relationships"):
        with before.each:
            self.cards, self.arrows = _laid_out()

        with it("should keep every card clear of every other"):
            boxes = [card.geometry for card in self.cards.values()]
            overlapping = [a for a in boxes for b in boxes if a is not b and a.overlaps(b)]
            expect(overlapping).to(equal([]))

        with it("should put a base above what derives from it"):
            expect(self.cards["Refund"].geometry.y).to(be_above(self.cards["Payment"].geometry.y))

        with it("should give the same layout every time"):
            again, _ = _laid_out()
            expect({key: card.geometry for key, card in again.items()}).to(
                equal({key: card.geometry for key, card in self.cards.items()})
            )

    with context("with arrows routed between the cards"):
        with before.each:
            self.cards, self.arrows = _laid_out()

        with it("should route every arrow"):
            expect(all(arrow.routed for arrow in self.arrows)).to(be_true)

        with it("should keep every arrow out of every card but its own two"):
            through = [
                (arrow.source, arrow.target, card.cell_id)
                for arrow in self.arrows
                for card in self.cards.values()
                if card.cell_id not in (arrow.source, arrow.target) and _passes_through(arrow.path, card)
            ]
            expect(through).to(equal([]))

        with it("should give every arrow its own end points"):
            ends = [point for arrow in self.arrows for point in (arrow.exit_point, arrow.entry_point)]
            expect(len(set(ends))).to(equal(len(ends)))

        # Inheritance fans out at angles from one arrowhead; every other arrow bends at right angles.
        with it("should bend every arrow but inheritance only at right angles"):
            slanted = [
                arrow.source
                for arrow in self.arrows
                if arrow.kind != "inheritance"
                for a, b in zip(arrow.path, arrow.path[1:])
                if a[0] != b[0] and a[1] != b[1]
            ]
            expect(slanted).to(equal([]))

        # Refund points up at Order against the layers, so its arrow crosses one of the arrows Order sends down.
        with it("should leave at most the one crossing of the arrow that runs up against the layers"):
            square = [arrow for arrow in self.arrows if not arrow.straight]
            crossed = [
                (first.source, second.source)
                for index, first in enumerate(square)
                for second in square[index + 1:]
                if paths_cross(first.path, second.path)
            ]
            expect(len(crossed) <= 1).to(be_true)

    with context("with a third card between two cards in one row"):
        with before.each:
            self.cards = [_card("Left"), _card("Middle"), _card("Right")]
            for card, x in zip(self.cards, (60, 400, 740)):
                card.geometry = card.geometry.moved_to(x, 200)
            self.arrow = DiagramArrow("Left", "Right", "association")
            ArrowRouter(self.cards, [self.arrow]).route()

        with it("should go around the card in the middle"):
            expect(_passes_through(self.arrow.path, self.cards[1])).to(be_false)

    with context("with three subclasses that share one base"):
        with before.each:
            self.base = _card("Payment", box=(400, 60, 200, 100))
            self.subclasses = [_card(name, box=(x, 300, 200, 100)) for name, x in (("Card", 60), ("Cash", 400), ("Voucher", 740))]
            self.cards = [self.base] + self.subclasses
            self.arrows = [DiagramArrow(card.cell_id, "Payment", "inheritance") for card in self.subclasses]
            ArrowRouter(self.cards, self.arrows).route()
            self.joining_point = self.arrows[0].path[-2]

        with it("should route every arrow"):
            expect(all(arrow.routed for arrow in self.arrows)).to(be_true)

        with it("should end every subclass arrow at one point on the base"):
            expect({arrow.entry_point for arrow in self.arrows}).to(equal({self.arrows[0].entry_point}))

        with it("should run one shared stem from the end of the fan to the base"):
            expect({tuple(arrow.path[-2:]) for arrow in self.arrows}).to(equal({(self.joining_point, self.arrows[0].entry_point)}))

        with it("should end the stem between the base and its subclasses"):
            expect(160 < self.joining_point[1] < 300).to(be_true)

        with it("should run a straight line from each subclass to the end of the stem"):
            expect([arrow.path[:-1] for arrow in self.arrows]).to(equal([[arrow.exit_point, self.joining_point] for arrow in self.arrows]))

        with it("should drop the stem straight from the arrowhead"):
            expect(self.joining_point[0]).to(equal(self.arrows[0].entry_point[0]))

        with it("should give each subclass its own point to leave from"):
            expect(len({arrow.exit_point for arrow in self.arrows})).to(equal(3))

        with it("should keep every arrow out of every card but its own two"):
            through = [
                (arrow.source, card.cell_id)
                for arrow in self.arrows
                for card in self.cards
                if card.cell_id not in (arrow.source, arrow.target) and _passes_through(arrow.path, card)
            ]
            expect(through).to(equal([]))

    with context("with one subclass of a base"):
        with before.each:
            self.cards = [_card("Payment", box=(400, 60, 200, 100)), _card("Cash", box=(400, 300, 200, 100))]
            self.arrow = DiagramArrow("Cash", "Payment", "inheritance")
            ArrowRouter(self.cards, [self.arrow]).route()

        with it("should draw one straight line up to the base"):
            expect({point[0] for point in self.arrow.path}).to(equal({self.arrow.entry_point[0]}))

    with context("with a card a person moved off the grid"):
        with before.each:
            self.source = _card("Source", box=(63, 47, 200, 87))
            self.target = _card("Target", box=(61, 401, 200, 93))
            self.arrow = DiagramArrow("Source", "Target", "association")
            ArrowRouter([self.source, self.target], [self.arrow]).route()

        with it("should still arrive at right angles"):
            bends = zip(self.arrow.path, self.arrow.path[1:])
            expect(all(a[0] == b[0] or a[1] == b[1] for a, b in bends)).to(be_true)

    with context("with subclasses both above and below their base"):
        with before.each:
            self.base = _card("Payment", box=(400, 300, 200, 100))
            above = [_card("Gift", box=(400, 60, 200, 100))]
            below = [_card(name, box=(x, 560, 200, 100)) for name, x in (("Card", 60), ("Cash", 400), ("Voucher", 740))]
            self.cards = [self.base] + above + below
            self.arrows = [DiagramArrow(card.cell_id, "Payment", "inheritance") for card in above + below]
            ArrowRouter(self.cards, self.arrows).route()

        with it("should route every arrow"):
            expect(all(arrow.routed for arrow in self.arrows)).to(be_true)

        with it("should end the whole family in one arrowhead"):
            expect({arrow.entry_point for arrow in self.arrows}).to(equal({self.arrows[0].entry_point}))

        with it("should bring it in on the side most of the subclasses face"):
            expect(self.arrows[0].entry_side).to(equal("bottom"))

        with it("should keep every arrow out of every card but its own two"):
            through = [
                (arrow.source, card.cell_id)
                for arrow in self.arrows
                for card in self.cards
                if card.cell_id not in (arrow.source, arrow.target) and _passes_through(arrow.path, card)
            ]
            expect(through).to(equal([]))

    with context("with a card a person placed right against another one's port"):
        with before.each:
            self.cards = [
                _card("Payment", box=(400, 60, 200, 100)),
                _card("Receipt", box=(380, 190, 240, 60)),
                _card("Cash", box=(800, 400, 200, 100)),
            ]
            self.arrow = DiagramArrow("Cash", "Payment", "association")
            ArrowRouter(self.cards, [self.arrow]).route()

        with it("should still route the arrow"):
            expect(self.arrow.routed).to(be_true)

        with it("should keep it out of the card in the way"):
            expect(_passes_through(self.arrow.path, self.cards[1])).to(be_false)


def _spread_out():
    """Order with Line far to its right and Payment far below, Refund close beside Payment, and an arrow from Order to
    Line."""
    cards = {
        "Order": _card("Order", box=(0, 0, 200, 100)),
        "Line": _card("Line", box=(900, 0, 200, 100)),
        "Payment": _card("Payment", box=(0, 800, 200, 100)),
        "Refund": _card("Refund", box=(240, 800, 200, 100)),
    }
    spacing = CardSpacing(list(cards.values()), [DiagramArrow("Order", "Line", "association")])
    spacing.close_gaps()
    return cards, spacing


with description("a page with empty space between its cards"):
    with context("whose space is closed up"):
        with before.each:
            self.cards, self.spacing = _spread_out()

        with it("should bring a card beside another to the gap between cards side by side"):
            expect(self.cards["Line"].geometry.x).to(equal(200 + self.spacing.gap_between("Order", "Line", across=True)))

        with it("should bring a card below another to the gap between cards one above the other"):
            expect(self.cards["Payment"].geometry.y).to(equal(100 + self.spacing.gap_between("Order", "Payment", across=False)))

        # Each arrow either card sends or takes needs its own lane through the gap between them.
        with it("should leave more room between cards joined by arrows"):
            expect(self.spacing.gap_between("Order", "Line", across=True)).to(be_above(self.spacing.gap_between("Payment", "Refund", across=True)))

        with it("should keep a card on the side of its neighbour it was on"):
            expect(self.cards["Line"].geometry.x > self.cards["Order"].geometry.x).to(be_true)

        # A person who put two cards close together meant it, so a gap already smaller stays as it was.
        with it("should keep a gap already smaller than the gap between cards"):
            expect(self.cards["Refund"].geometry.x - 200).to(equal(40))

        with it("should keep every card clear of every other"):
            boxes = [card.geometry for card in self.cards.values()]
            expect(any(first.overlaps(second) for index, first in enumerate(boxes) for second in boxes[index + 1:])).to(be_false)

    with context("that a layout made itself"):
        with before.each:
            self.cards, _ = _laid_out()

        with it("should leave no gap wider than the most room between cards"):
            boxes = sorted((card.geometry for card in self.cards.values()), key=lambda box: box.x)
            gaps = [
                later.x - (earlier.x + earlier.width) for earlier, later in zip(boxes, boxes[1:])
                if later.x > earlier.x + earlier.width and abs(later.y - earlier.y) < 100
            ]
            expect(all(gap <= CardSpacing.MOST_GAP for gap in gaps)).to(be_true)
