"""Class cards and their arrows — where cards sit and how arrows find their way between them."""
from expects import be_above, be_false, be_true, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.diagram.class_layout import (
    ArrowRouter,
    CardPlacement,
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

        with it("should bend only at right angles"):
            slanted = [
                arrow.source
                for arrow in self.arrows
                for a, b in zip(arrow.path, arrow.path[1:])
                if a[0] != b[0] and a[1] != b[1]
            ]
            expect(slanted).to(equal([]))

        with it("should leave no crossing on a model that can be drawn flat"):
            crossed = [
                (first.source, second.source)
                for index, first in enumerate(self.arrows)
                for second in self.arrows[index + 1:]
                if paths_cross(first.path, second.path)
            ]
            expect(crossed).to(equal([]))

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

        with it("should run one shared line straight from the bar to the base"):
            expect({tuple(arrow.path[-2:]) for arrow in self.arrows}).to(equal({(self.joining_point, self.arrows[0].entry_point)}))

        with it("should put the bar between the base and its subclasses"):
            expect(160 < self.joining_point[1] < 300).to(be_true)

        with it("should drop each subclass straight to the bar"):
            drops = [(arrow.path[0][0] == arrow.path[1][0], arrow.path[1][1]) for arrow in self.arrows]
            expect(drops).to(equal([(True, self.joining_point[1])] * 3))

        with it("should run along the bar from each drop to the shared line"):
            bars = [arrow.path[-3][1] == arrow.path[-2][1] for arrow in self.arrows if len(arrow.path) > 3]
            expect(bars).to(equal([True, True]))

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

        with it("should draw one straight arrow to the base"):
            expect(len(self.arrow.path)).to(equal(2))

    with context("with two subclasses whose shared bar would run through another card"):
        with before.each:
            self.cards = [
                _card("Payment", box=(400, 60, 200, 100)),
                _card("Card", box=(60, 300, 200, 100)),
                _card("Ledger", box=(400, 230, 200, 40)),
                _card("Voucher", box=(740, 300, 200, 100)),
            ]
            self.arrows = [DiagramArrow("Card", "Payment", "inheritance"), DiagramArrow("Voucher", "Payment", "inheritance")]
            ArrowRouter(self.cards, self.arrows).route()

        with it("should still route every arrow"):
            expect(all(arrow.routed for arrow in self.arrows)).to(be_true)

        with it("should give each arrow its own point on the base"):
            expect(self.arrows[0].entry_point).not_to(equal(self.arrows[1].entry_point))

        with it("should keep every arrow out of the card in the way"):
            expect([_passes_through(arrow.path, self.cards[2]) for arrow in self.arrows]).to(equal([False, False]))

    with context("with a card a person moved off the grid"):
        with before.each:
            self.source = _card("Source", box=(63, 47, 200, 87))
            self.target = _card("Target", box=(61, 401, 200, 93))
            self.arrow = DiagramArrow("Source", "Target", "association")
            ArrowRouter([self.source, self.target], [self.arrow]).route()

        with it("should still arrive at right angles"):
            bends = zip(self.arrow.path, self.arrow.path[1:])
            expect(all(a[0] == b[0] or a[1] == b[1] for a, b in bends)).to(be_true)
