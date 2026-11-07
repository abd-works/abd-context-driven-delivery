"""Each DDD format reads back the map it wrote: markdown, sketch, and draw.io, at bounded-context and model fidelity."""

from pathlib import Path

from expects import equal, expect
from mamba import before, description, context, it

from cdd_guidance.practices.ddd.model.drawio.drawio_bounded_context_map import DrawIOBoundedContextMap
from cdd_guidance.practices.ddd.model.markdown.class_cards import plain_properties
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.sketch.sketch_ddd_model import SketchDddModel

_EXAMPLES = Path(__file__).resolve().parent / "_examples" / "expected"
_BOUNDED_CONTEXT_MAP = (_EXAMPLES / "bounded-context-map.md").read_text(encoding="utf-8")
_DOMAIN_MODEL = (_EXAMPLES / "domain-model.md").read_text(encoding="utf-8")

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
    node = card.node
    return (
        node.name,
        card.stereotypes,
        [(prop.name, prop.type_hint, prop.stereotype) for prop in plain_properties(node)],
        [(op.name, [item.save() for item in op.parameters], op.return_type, op.callees) for op in node.operations],
        card.invariants,
    )


def _drawn_card(card):
    # The root card draws its repository's operations only, so a repository's properties are not on the page.
    node = card.node
    return (
        node.name,
        card.stereotypes,
        [] if card.is_repository else [(prop.name, prop.type_hint) for prop in plain_properties(node)],
        [(op.name, [item.name for item in op.parameters]) for op in node.operations],
    )


def _aggregate(aggregate):
    return (
        aggregate.name,
        aggregate.root.name,
        [item.name for item in aggregate.root.invariant_objects],
        [item.name for item in aggregate.root.operations],
        _integrations(aggregate),
        [(event.name, [item.name for item in event.consumers]) for event in aggregate.events],
        [_card(card) for card in aggregate.cards],
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
                (a.name, a.root.name, [m.name for m in a.root.invariant_objects], _drawn_integrations(a))
                for a in item.aggregates
            ],
        )
        for item in model.contexts
    ]


def _drawn_model(model):
    return [
        (item.name, [(a.name, a.root.name, [_drawn_card(card) for card in a.cards]) for a in item.aggregates])
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
