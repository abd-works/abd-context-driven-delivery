"""A schema type: the fields written optional, and the relationships its nodes must have."""

from expects import contain, equal, expect
from mamba import before, description, it

from harness.guidance.schema import Schema

_ORDER = """\
order:
  fidelity: model
  id: dotPath
  name: string
  belongsTo: customer
  lines: [line]
  payment: card | voucher
  coupon?: [coupon]
  total: money | number
  status: "open" | "paid"
"""


with description("a schema type"):
    with before.each:
        self.order = Schema(_ORDER).types["order"]

    with it("should keep the fields written optional"):
        expect(self.order.optional).to(equal({"coupon"}))

    with it("should keep an optional field among its fields"):
        expect(self.order.fields).to(contain(("coupon", "[coupon]")))

    with it("should require each field naming only other schema types"):
        expect(self.order.required_relationships).to(equal({"lines": ("line",), "payment": ("card", "voucher")}))
