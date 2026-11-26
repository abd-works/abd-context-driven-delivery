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

    with it("should relate it by every field with a value that does not describe the type itself"):
        names = [relationship.name for relationship in self.order.relationships]
        expect(names).to(equal(["id", "belongsTo", "lines", "payment", "coupon", "total", "status"]))

    with it("should name the types a relationship's value names, value types left out"):
        total = next(relationship for relationship in self.order.relationships if relationship.name == "total")
        expect(total.targets).to(equal(("money",)))

    with it("should name no type for a quoted value"):
        status = next(relationship for relationship in self.order.relationships if relationship.name == "status")
        expect(status.targets).to(equal(()))

    with it("should not require the back-edge of a child list, though it names a type"):
        belongs = next(relationship for relationship in self.order.relationships if relationship.name == "belongsTo")
        expect((belongs.references, belongs.is_required)).to(equal((("customer",), False)))
