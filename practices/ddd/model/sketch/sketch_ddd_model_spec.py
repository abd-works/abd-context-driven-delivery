"""Sketch DDD model — parse bounded-context map from sketch notation."""

from mamba import description, context, it
from expects import expect, equal, contain

from practices.ddd.model.sketch.sketch_ddd_model import SketchDddModel
from practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap

_SKETCH = """\
# Example sketch

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
Line Item
```

### event_map:

```
- CartCheckedOut: emitted by Cart; consumed by Inventory
```
"""


with description("SketchDddModel"):
    with context("parse"):
        with it("should map module entities to aggregates and skip prose sections"):
            model = SketchDddModel().parse(_SKETCH)
            expect(len(model.contexts)).to(equal(1))
            context = model.contexts[0]
            expect(context.name).to(equal("Sales"))
            expect(len(context.aggregates)).to(equal(1))
            expect(context.aggregates[0].name).to(equal("Cart"))

        with it("should render markdown bounded-context map from sketch"):
            model = SketchDddModel().parse(_SKETCH)
            body = MarkdownBoundedContextMap().render(model, _SKETCH)
            expect(body).to(contain("## Sales | custom"))
            expect(body).to(contain("### Cart"))
            expect(body).to(contain("## event map"))
            expect(body).to(contain("CartCheckedOut"))
            expect(body.find("false cognates")).to(equal(-1))
