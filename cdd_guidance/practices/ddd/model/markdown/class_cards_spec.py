"""Model fidelity — aggregate class cards in markdown and sketch."""

from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import context, description, it

from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.sketch.sketch_ddd_model import SketchDddModel

_EXPECTED = Path(__file__).resolve().parent.parent / "_examples" / "expected" / "domain-model.md"

_SKETCH = """\
## domain driven design:

### Revenue | custom

#### billing/

##### BillingAccount <<Aggregate Root>> <<Entity>>

```
id
CreditAdjustment <<Value Object>>
applyCredit amount
   -> CreditAdjustment.record
payNow()
refs:
  - Subscription (by subscriptionId)
repo: BillingAccountRepository <<Repository>>
  create / load / update
```

##### CreditAdjustment <<Value Object>>

```
amount
```
"""


def _aggregate(model, context_name, aggregate_name):
    found = next(item for item in model.contexts if item.name == context_name)
    return next(item for item in found.aggregates if item.name == aggregate_name)


with description("Model fidelity class cards"):
    with context("reading domain-model.md"):
        with it("should take the root from the aggregate root card"):
            model = MarkdownBoundedContextMap().parse(_EXPECTED.read_text(encoding="utf-8"))
            aggregate = _aggregate(model, "Customer", "Customer Profile")
            expect(aggregate.root.name).to(equal("CustomerProfile"))
            expect(aggregate.root.is_root).to(be_true)
            expect([item.name for item in aggregate.root.operations]).to(
                equal(["enterProfileDetails", "sendSupportRequest"])
            )

        with it("should keep the repository's collection operations apart from the root's"):
            model = MarkdownBoundedContextMap().parse(_EXPECTED.read_text(encoding="utf-8"))
            aggregate = _aggregate(model, "Customer", "Customer Profile")
            expect([item.name for item in aggregate.repository.node.operations]).to(
                equal(["create", "load", "update"])
            )
            expect(aggregate.repository.node.accesses is aggregate.root).to(be_true)

        with it("should list the members the root composes"):
            model = MarkdownBoundedContextMap().parse(_EXPECTED.read_text(encoding="utf-8"))
            aggregate = _aggregate(model, "Customer", "Customer Profile")
            expect([item.name for item in aggregate.root.invariant_objects]).to(equal(["Identity", "Address"]))

        with it("should keep the call to another aggregate on the operation that makes it"):
            model = MarkdownBoundedContextMap().parse(_EXPECTED.read_text(encoding="utf-8"))
            aggregate = _aggregate(model, "Service", "Subscription")
            change_plan = aggregate.root.operations[0]
            expect(change_plan.callees).to(equal(["PlanRepository.load(planId)"]))
            expect(aggregate.integrations[0].context).to(equal("Customer"))

        with it("should write the same document it read"):
            model = MarkdownBoundedContextMap().parse(_EXPECTED.read_text(encoding="utf-8"))
            written = model.save()
            expect(MarkdownBoundedContextMap().parse(written).save()).to(equal(written))
            expect(written).to(contain("# Domain Model"))

    with context("reading a model sketch"):
        with it("should name the aggregate after its heading and give the root its repository"):
            model = SketchDddModel().parse(_SKETCH)
            aggregate = _aggregate(model, "Revenue", "billing")
            expect(aggregate.root.name).to(equal("BillingAccount"))
            expect([item.node.name for item in aggregate.cards]).to(
                equal(["BillingAccount", "BillingAccountRepository", "CreditAdjustment"])
            )
            expect([item.name for item in aggregate.repository.node.operations]).to(
                equal(["create", "load", "update"])
            )

        with it("should read operations, properties, members, and references from the fence"):
            model = SketchDddModel().parse(_SKETCH)
            root = _aggregate(model, "Revenue", "billing").root
            expect([item.name for item in root.operations]).to(equal(["applyCredit", "payNow"]))
            expect([(item.name, item.stereotype) for item in root.properties]).to(
                equal([("id", ""), ("creditAdjustment", "composition"), ("subscriptionId", "association")])
            )
