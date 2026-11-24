"""A markdown step's realization names the model operations the step leads to: each is an edge from the step to that
operation in the domain model or the class model its domain terms link to, as a story test's step links to the code it
calls; and code-steps-invoke-code reports a When whose realization names none."""

from expects import be_empty, contain, equal, expect, have_len
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.fixtures.bookshop_project import BookshopWorkingCopy

_ADD_BOOK = "story_tests/fill-cart/add-books/add_book_to_cart_story.test.md"
_ADD_TINY_TALES = "when the Customer adds ++Book++ ++Tiny Tales++ to the ++Cart++"
_ADD_GRAND_ATLAS = "when the Customer adds ++Book++ ++Grand Atlas++ to the ++Cart++"
_REALIZED_CALL = "Cart.addBook(book, 1)"
_DOMAIN_MODEL = ".context/domain-model.md"
_DDD_ADD_BOOK = "ddd:Operation:.context/domain-model.md:addBook:Cart"
_DDD_PUT_BOOK = "ddd:Operation:.context/domain-model.md:putBook:Cart"
_CLASS_MODEL_ADD_BOOK = "clean_engineering:Operation:.context/class-model.md:addBook:Cart"
# A Clean Engineering class model of the Cart and the Book, which the scenarios' links name instead of the domain model.
_CLASS_MODEL = """# ordering

## Cart <<Aggregate Root>> <<Entity>>

------
+ cartId: CartId
----
+ addBook(bookId: BookId, quantity: Quantity): CartLine
+ total(): Money

## Book <<Aggregate Root>> <<Entity>>

------
+ bookId: BookId
----
+ reprice(amount: Money): void
"""
_AS_CLASS_MODEL = {
    "written": {".context/class-model.md": _CLASS_MODEL},
    "rewritten": {_ADD_BOOK: ("domain-model.md#", "class-model.md#")},
}
_RULE = "code-steps-invoke-code"


def _when(project: BookshopWorkingCopy, name: str):
    return project.node_named("When", name, _ADD_BOOK)[0]


def _invoked_by(project: BookshopWorkingCopy, step) -> list[str]:
    """The ids of the operations step has an ``invokes`` edge to."""
    return sorted(edge.child.node_id for edge in project.graph.edges.from_parent("invokes", step))


def _realization_findings(project: BookshopWorkingCopy) -> list[str]:
    return [found for found in project.findings(_RULE) if "has a realization" in found]


with description("a markdown When whose realization names a model operation") as self:
    with context("with the domain model its domain terms link to"):
        with before.all:
            self.project = BookshopWorkingCopy(("stories", "ddd"))
            self.when = _when(self.project, _ADD_TINY_TALES)

        with it("should invoke the operation its realization calls on a class the model holds"):
            expect(_invoked_by(self.project, self.when)).to(equal([_DDD_ADD_BOOK]))

        with it("should be invoked by that operation in turn"):
            operation = self.project.graph.practices.named("ddd").reading.in_graph.node(_DDD_ADD_BOOK)
            invoking = [edge.child.node_id for edge in self.project.graph.edges.from_parent("invokedBy", operation)]
            expect(invoking).to(contain(self.when.node_id))

        with it("should leave out a call to an operation the model does not declare"):
            expect([found for found in _invoked_by(self.project, self.when) if "reserve" in found]).to(be_empty)

        with it("should not be reported by code-steps-invoke-code"):
            expect(_realization_findings(self.project)).to(be_empty)

        with it("should leave a When with no realization unlinked and unreported"):
            grand_atlas = _when(self.project, _ADD_GRAND_ATLAS)
            expect((_invoked_by(self.project, grand_atlas), grand_atlas.get_fact("realization_reach"))).to(equal(([], None)))

    with context("with the class model its domain terms link to"):
        with before.all:
            self.project = BookshopWorkingCopy(("stories", "clean_engineering"), **_AS_CLASS_MODEL)

        with it("should invoke that operation of the class model"):
            expect(_invoked_by(self.project, _when(self.project, _ADD_TINY_TALES))).to(equal([_CLASS_MODEL_ADD_BOOK]))

    with context("whose realization calls the operation on an example rather than its class"):
        with before.all:
            self.project = BookshopWorkingCopy(("stories", "ddd"), rewritten={_ADD_BOOK: (_REALIZED_CALL, "empty cart.addBook(book, 1)")})

        with it("should invoke the operation of the one linked class that declares it"):
            expect(_invoked_by(self.project, _when(self.project, _ADD_TINY_TALES))).to(equal([_DDD_ADD_BOOK]))

    with context("whose realization names an operation the model has since renamed"):
        with before.all:
            self.project = BookshopWorkingCopy(("stories", "ddd"), rewritten={_ADD_BOOK: (_REALIZED_CALL, "Cart.putBook(book, 1)")})
            self.when = _when(self.project, _ADD_TINY_TALES)

        with it("should invoke nothing"):
            expect(_invoked_by(self.project, self.when)).to(be_empty)

        with it("should be reported by code-steps-invoke-code"):
            expect(_realization_findings(self.project)).to(have_len(1))

        with it("should name the When in the finding"):
            expect(_realization_findings(self.project)[0]).to(contain(_ADD_TINY_TALES))

    with context("whose operation the domain model renames after the graph is read"):
        with before.all:
            self.project = BookshopWorkingCopy(("stories", "ddd"))
            model = self.project.root / _DOMAIN_MODEL
            model.write_text(model.read_text(encoding="utf-8").replace("+ addBook(", "+ putBook("), encoding="utf-8")
            self.project.graph.refresh([_DOMAIN_MODEL])
            self.when = _when(self.project, _ADD_TINY_TALES)

        with it("should invoke nothing once the model is read again"):
            expect(_invoked_by(self.project, self.when)).to(be_empty)

        with it("should be reported by code-steps-invoke-code"):
            expect(_realization_findings(self.project)).to(have_len(1))

        with context("that the realization then names as well"):
            with before.all:
                scenarios = self.project.root / _ADD_BOOK
                scenarios.write_text(scenarios.read_text(encoding="utf-8").replace(_REALIZED_CALL, "Cart.putBook(book, 1)"), encoding="utf-8")
                self.project.graph.refresh([_ADD_BOOK])

            with it("should invoke the renamed operation"):
                expect(_invoked_by(self.project, _when(self.project, _ADD_TINY_TALES))).to(equal([_DDD_PUT_BOOK]))

    with context("whose domain terms link to no model document"):
        with before.all:
            unlinked = "*When* the Customer adds Tiny Tales to the Cart"
            linked = (
                "*When* the Customer adds ++[Book](../../../.context/domain-model.md#book-aggregate-root-entity)++ ++Tiny Tales++ "
                "to the ++[Cart](../../../.context/domain-model.md#cart-aggregate-root-entity)++"
            )
            self.project = BookshopWorkingCopy(("stories", "ddd"), rewritten={_ADD_BOOK: (linked, unlinked)})
            self.when = _when(self.project, "when the Customer adds Tiny Tales to the Cart")

        with it("should invoke nothing, though its realization names a class of the model"):
            expect(_invoked_by(self.project, self.when)).to(be_empty)

        with it("should leave the When unjudged, as its scenarios may be written before the model"):
            expect(_realization_findings(self.project)).to(be_empty)

    with context("with no model read beside the scenarios"):
        with before.all:
            self.project = BookshopWorkingCopy(("stories",), rewritten={_ADD_BOOK: (_REALIZED_CALL, "Cart.putBook(book, 1)")})

        with it("should leave the When unjudged"):
            expect(_realization_findings(self.project)).to(be_empty)
