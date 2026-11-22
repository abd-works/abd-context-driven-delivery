"""Each DDD format reads back the map it wrote: markdown, sketch, and draw.io, at bounded-context and model fidelity."""

from pathlib import Path

from expects import equal, expect
from mamba import before, description, context, it

from cdd_guidance.practices.ddd.model.drawio.drawio_bounded_context_map import DrawIOBoundedContextMap
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.sketch.sketch_ddd_model import SketchDddModel
from cdd_guidance.practices.ddd.model.whiteboard.whiteboard_bounded_context_map import WhiteboardBoundedContextMap
from harness.guidance.practice_formats import Written

_EXAMPLES = Path(__file__).resolve().parent / "_examples" / "expected"
_BOUNDED_CONTEXT_MAP = (_EXAMPLES / "bounded-context-map.md").read_text(encoding="utf-8")
_DOMAIN_MODEL = (_EXAMPLES / "domain-model.md").read_text(encoding="utf-8")
# A bookshop's map and domain model as a person writes them after the templates, taken there and back whole.
_TRIP = _EXAMPLES.parent / "trip"
_BOOKSHOP_MAP = (_TRIP / "bounded-context-map.md").read_text(encoding="utf-8")
_BOOKSHOP_MODEL = (_TRIP / "domain-model.md").read_text(encoding="utf-8")

_SKETCH_WITH_NOTES = """\
## domain driven design:

### Sales | custom

```
note: the sales context
```

#### checkout/

```
// seam: take payment
entry: cart_id
```

##### Cart

```
addItem
removeItem
LineItem
```

### event_map:

```
- CartCheckedOut: emitted by Cart; consumed by Inventory
```
"""


def _round_trip(adapter, model):
    return adapter.parse(adapter.render(model))


def _integrations(aggregate):
    return [
        (item.target_name, item.pattern, item.direction, item.crosses, item.integration)
        for item in aggregate.integrations
    ]


def _drawn_integrations(aggregate):
    return [(item.target_name, item.pattern) for item in aggregate.integrations]


def _card(card):
    return (
        card.name,
        card.stereotypes,
        [(prop.name, prop.type_hint, prop.stereotype) for prop in card.plain_properties],
        [(op.name, [item.save() for item in op.parameters], op.return_type, op.callees) for op in card.operations],
        card.invariants,
    )


def _drawn_card(card):
    # The root card draws its repository's operations only, so a repository's properties are not on the page.
    return (
        card.name,
        card.stereotypes,
        [] if card.is_repository else [(prop.name, prop.type_hint) for prop in card.plain_properties],
        [(op.name, [item.name for item in op.parameters]) for op in card.operations],
    )


def _aggregate(aggregate):
    return (
        aggregate.name,
        aggregate.root.name,
        [item.name for item in aggregate.members],
        [item.name for item in aggregate.root.operations],
        _integrations(aggregate),
        [(event.name, [item.name for item in event.consumers]) for event in aggregate.events],
        [_card(card) for card in aggregate.classes],
    )


def _shape(model):
    return [
        (item.name, item.owner, item.notes, item.module_name, item.module_notes, [_aggregate(a) for a in item.aggregates])
        for item in model.contexts
    ]


def _drawn_map(model):
    return [
        (
            item.name,
            item.owner,
            [
                (a.name, a.root.name, [m.name for m in a.members], _drawn_integrations(a))
                for a in item.aggregates
            ],
        )
        for item in model.contexts
    ]


def _drawn_model(model):
    return [
        (item.name, [(a.name, a.root.name, [_drawn_card(card) for card in a.classes]) for a in item.aggregates])
        for item in model.contexts
    ]


with description("a bounded context map written to a format and read back"):
    with context("that is a bounded context map with integrations and events"):
        with before.all:
            self.model = MarkdownBoundedContextMap().parse(_BOUNDED_CONTEXT_MAP)

        with it("should keep every context, aggregate, integration, and event through markdown"):
            adapter = MarkdownBoundedContextMap()
            expect(_shape(_round_trip(adapter, self.model))).to(equal(_shape(self.model)))

        with it("should keep every context, aggregate, integration, and event through sketch"):
            adapter = SketchDddModel()
            expect(_shape(_round_trip(adapter, self.model))).to(equal(_shape(self.model)))

        with it("should keep the contexts, owners, aggregates, members, and integration arrows through draw.io"):
            adapter = DrawIOBoundedContextMap()
            expect(_drawn_map(_round_trip(adapter, self.model))).to(equal(_drawn_map(self.model)))

    with context("that is a domain model with class cards"):
        with before.all:
            self.model = MarkdownBoundedContextMap().parse(_DOMAIN_MODEL)

        with it("should keep every card, member, operation, and call through markdown"):
            adapter = MarkdownBoundedContextMap()
            expect(_shape(_round_trip(adapter, self.model))).to(equal(_shape(self.model)))

        with it("should keep every card, member, operation, and call through sketch"):
            adapter = SketchDddModel()
            expect(_shape(_round_trip(adapter, self.model))).to(equal(_shape(self.model)))

        with it("should keep the contexts, aggregates, and cards drawn in the aggregate view through draw.io"):
            adapter = DrawIOBoundedContextMap()
            expect(_drawn_model(_round_trip(adapter, self.model))).to(equal(_drawn_model(self.model)))

    with context("that was read from a sketch with context notes and a module"):
        with before.all:
            self.model = SketchDddModel().parse(_SKETCH_WITH_NOTES)

        with it("should keep the notes and the module through markdown"):
            adapter = MarkdownBoundedContextMap()
            expect(_shape(_round_trip(adapter, self.model))).to(equal(_shape(self.model)))

        with it("should keep the notes and the module through sketch"):
            adapter = SketchDddModel()
            expect(_shape(_round_trip(adapter, self.model))).to(equal(_shape(self.model)))


def _member_lines(markdown: str) -> list:
    """The property and operation lines of every class card, as the markdown writes them."""
    return [line for line in markdown.splitlines() if line.startswith(("+ ", "- ")) and not line.startswith("- the ")]


def _there_and_back(adapter, markdown: str) -> str:
    """markdown written into the adapter's format, read back from it, and written as markdown again."""
    return MarkdownBoundedContextMap().render(type(adapter)().parse(adapter.render(MarkdownBoundedContextMap().parse(markdown))))


with description("a domain model a person wrote in markdown, taken to another format and back"):
    with context("that is read and written again as markdown"):
        with before.all:
            self.back = MarkdownBoundedContextMap().render(MarkdownBoundedContextMap().parse(_BOOKSHOP_MODEL))

        with it("should keep the front matter and the title it was written under"):
            expect(self.back.splitlines()[:8]).to(equal(_BOOKSHOP_MODEL.splitlines()[:8]))

        with it("should bring back every property and operation line as written"):
            expect(_member_lines(self.back)).to(equal(_member_lines(_BOOKSHOP_MODEL)))

        with it("should add no rule over operations to a class that has none"):
            expect(self.back.count("\n----\n")).to(equal(_BOOKSHOP_MODEL.count("\n----\n")))

        with it("should keep the invariants, notes, and calls"):
            kept = [line.strip() for line in self.back.splitlines() if line.strip().startswith(("//", "->", "- the "))]
            expect(kept).to(equal([
                "// held by identity — Book lives in Catalog", "-> OrderLine.price",
                "// an order already shipped is refused", "- the total is the sum of the lines' prices",
            ]))

    with context("that is drawn in draw.io and written back as markdown"):
        with before.all:
            self.back = _there_and_back(DrawIOBoundedContextMap(), _BOOKSHOP_MODEL)

        with it("should bring back every property and operation line as written, adding no relationship"):
            expect(_member_lines(self.back)).to(equal(_member_lines(_BOOKSHOP_MODEL)))

    with context("that is drawn on a whiteboard and written back as markdown"):
        with before.all:
            self.back = _there_and_back(WhiteboardBoundedContextMap(), _BOOKSHOP_MODEL)

        with it("should bring back every property and operation line as written, adding no relationship"):
            expect(_member_lines(self.back)).to(equal(_member_lines(_BOOKSHOP_MODEL)))


with description("a bounded context map a person wrote in markdown, taken to another format and back"):
    with context("that is read and written again as markdown"):
        with before.all:
            self.back = MarkdownBoundedContextMap().render(MarkdownBoundedContextMap().parse(_BOOKSHOP_MAP))

        with it("should keep the Integrations block as written"):
            expect(self.back[self.back.index("Integrations:"):self.back.index("## Catalog")]).to(
                equal(_BOOKSHOP_MAP[_BOOKSHOP_MAP.index("Integrations:"):_BOOKSHOP_MAP.index("## Catalog")])
            )

    with context("that is drawn in draw.io and written back as markdown"):
        with before.all:
            self.back = _there_and_back(DrawIOBoundedContextMap(), _BOOKSHOP_MAP)

        with it("should keep the title it was written under"):
            expect(self.back.splitlines()[0]).to(equal("# Bounded Context Map — Bookshop"))

    with context("that is drawn on a whiteboard and written back as markdown"):
        with before.all:
            self.back = _there_and_back(WhiteboardBoundedContextMap(), _BOOKSHOP_MAP)

        with it("should keep the title it was written under"):
            expect(self.back.splitlines()[0]).to(equal("# Bounded Context Map — Bookshop"))


# A bookshop of three bounded contexts, its map and its domain model as a person writes them after the templates:
# a sentence under each heading, integrations with every field, events emitted and consumed, notes, calls, invariants.
_THREE_CONTEXTS = _TRIP / "three-contexts"
_SHOP_MAP = (_THREE_CONTEXTS / "bounded-context-map.md").read_text(encoding="utf-8")
_SHOP_MODEL = (_THREE_CONTEXTS / "domain-model.md").read_text(encoding="utf-8")


def _written_lines(markdown: str) -> list:
    """Each line of a document with words on it, without the `---` rules that part its sections."""
    return [line.strip() for line in markdown.splitlines() if line.strip() and line.strip() != "---"]


def _written_over(adapter, markdown: str) -> str:
    """markdown drawn in the adapter's format, then the drawing written as markdown over the file it was drawn from."""
    drawn = type(adapter)().parse(adapter.render(MarkdownBoundedContextMap().parse(markdown)))
    return MarkdownBoundedContextMap().render(drawn, Written(markdown))


def _arcs(model) -> list:
    return [
        (aggregate.name, [(arc.context, arc.aggregate, arc.entity, arc.pattern) for arc in aggregate.integrations])
        for aggregate in model.every_aggregate
        if aggregate.integrations
    ]


def _calls_across(model) -> list:
    """Each operation that calls a class of another aggregate, with the classes it calls."""
    found = []
    for aggregate in model.every_aggregate:
        local = {card.name for card in aggregate.classes}
        for card in aggregate.classes:
            for operation in card.operations:
                called = [callee.partition(".")[0].strip() for callee in operation.callees]
                across = [name for name in called if name[:1].isupper() and name not in local]
                if across:
                    found.append((card.name, operation.name, across))
    return found


def _arrows(drawio: str) -> list:
    """Each arrow of a drawing: the cards it joins and what it is labelled."""
    from xml.etree import ElementTree

    cells = ElementTree.fromstring(drawio).iter("mxCell")
    return sorted((cell.get("source"), cell.get("target"), cell.get("value")) for cell in cells if cell.get("edge") == "1")


with description("a bounded context map of three contexts a person wrote after the template"):
    with context("that is read and written again as markdown"):
        with it("should bring back every line the person wrote, and no other"):
            back = MarkdownBoundedContextMap().render(MarkdownBoundedContextMap().parse(_SHOP_MAP))
            expect(_written_lines(back)).to(equal(_written_lines(_SHOP_MAP)))

    with context("that is drawn in draw.io, and the drawing written as markdown over the file it was drawn from"):
        with before.all:
            self.back = _written_over(DrawIOBoundedContextMap(), _SHOP_MAP)

        with it("should bring back every line the person wrote, and no other"):
            expect(_written_lines(self.back)).to(equal(_written_lines(_SHOP_MAP)))

    with context("that is drawn on a whiteboard, and the board written as markdown over the file it was drawn from"):
        with before.all:
            self.back = _written_over(WhiteboardBoundedContextMap(), _SHOP_MAP)

        with it("should bring back every line the person wrote, and no other"):
            expect(_written_lines(self.back)).to(equal(_written_lines(_SHOP_MAP)))

    with context("whose drawing lost the arrow of one integration before it is written over the file"):
        with it("should leave out the integration whose arrow is gone and keep the others whole"):
            drawn = DrawIOBoundedContextMap().parse(DrawIOBoundedContextMap().render(MarkdownBoundedContextMap().parse(_SHOP_MAP)))
            next(item for item in drawn.every_aggregate if item.name == "Cart").integrations.clear()
            back = MarkdownBoundedContextMap().parse(MarkdownBoundedContextMap().render(drawn, Written(_SHOP_MAP)))
            kept = [(aggregate.name, [(arc.pattern, arc.crosses) for arc in aggregate.integrations]) for aggregate in back.every_aggregate]
            expect(kept).to(equal([
                ("Cart", []),
                ("Order", [("Open Host / Published Language", "the paid order's lines and delivery address")]),
                ("Book", []),
                ("Shipment", [("Conformist", "the order's identity and delivery address")]),
            ]))


with description("a domain model of three contexts a person wrote after the template"):
    with context("that is read and written again as markdown"):
        with it("should bring back every line the person wrote, and no other"):
            back = MarkdownBoundedContextMap().render(MarkdownBoundedContextMap().parse(_SHOP_MODEL))
            expect(_written_lines(back)).to(equal(_written_lines(_SHOP_MODEL)))

    with context("that is drawn in draw.io, and the drawing written as markdown over the file it was drawn from"):
        with before.all:
            self.back = _written_over(DrawIOBoundedContextMap(), _SHOP_MODEL)

        with it("should bring back every line the person wrote, and no other"):
            expect(_written_lines(self.back)).to(equal(_written_lines(_SHOP_MODEL)))

    with context("that is drawn on a whiteboard, and the board written as markdown over the file it was drawn from"):
        with before.all:
            self.back = _written_over(WhiteboardBoundedContextMap(), _SHOP_MODEL)

        with it("should bring back every line the person wrote, and no other"):
            expect(_written_lines(self.back)).to(equal(_written_lines(_SHOP_MODEL)))

    with context("whose drawing is read with no markdown beside it"):
        with before.all:
            self.written = MarkdownBoundedContextMap().parse(_SHOP_MODEL)
            self.drawing = DrawIOBoundedContextMap().render(self.written)
            self.read = DrawIOBoundedContextMap().parse(self.drawing)
            again = MarkdownBoundedContextMap().parse(MarkdownBoundedContextMap().render(DrawIOBoundedContextMap().parse(self.drawing)))
            self.drawn_again = DrawIOBoundedContextMap().render(again)

        with it("should read each integration's arrow as an integration to the class it points at, with its pattern"):
            expect(_arcs(self.read)).to(equal(_arcs(self.written)))

        with it("should read each arrow named by an operation as a call that operation makes to the class it points at"):
            expect(_calls_across(self.read)).to(equal(_calls_across(self.written)))

        with it("should draw the same arrows again from the markdown it writes"):
            expect(_arrows(self.drawn_again)).to(equal(_arrows(self.drawing)))

    with context("whose whiteboard is read with no markdown beside it"):
        with before.all:
            self.written = MarkdownBoundedContextMap().parse(_SHOP_MODEL)
            self.read = WhiteboardBoundedContextMap().parse(WhiteboardBoundedContextMap().render(self.written))

        with it("should read each integration's arrow as an integration to the class it points at, with its pattern"):
            expect(_arcs(self.read)).to(equal(_arcs(self.written)))

        with it("should read each arrow named by an operation as a call that operation makes to the class it points at"):
            expect(_calls_across(self.read)).to(equal(_calls_across(self.written)))
