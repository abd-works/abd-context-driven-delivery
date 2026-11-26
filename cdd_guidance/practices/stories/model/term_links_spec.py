"""The domain terms a step links to the domain model: each is an edge from the step to the class the link names, and
an example written beside a linked term demonstrates that class."""

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.fixtures.bookshop_project import BookshopProject

_ADD_BOOK = "story_tests/fill-cart/add-books/add_book_to_cart_story.test.md"
_PACK_ORDER = "story_tests/fulfil-order/pack-order/pack_order_story.test.py"
_BOOK = "ddd:EntityRoot:.context/domain-model.md:Book"
_CART = "ddd:EntityRoot:.context/domain-model.md:Cart"
_ORDER = "ddd:EntityRoot:.context/domain-model.md:Order"


def _named_by(project: BookshopProject, step) -> list[str]:
    """The ids of the nodes step has a ``names`` edge to."""
    return sorted(edge.child.node_id for edge in project.graph.edges.from_parent("names", step))


def _demonstrated_by(project: BookshopProject, example) -> list[str]:
    return sorted(edge.child.node_id for edge in project.graph.edges.from_parent("demonstrates", example))


with description("a step that links a domain term to its heading in the domain model") as self:
    with before.all:
        self.project = BookshopProject((".context", "story_tests"), ("stories", "ddd"))

    with context("that is written in a markdown scenarios file"):
        with before.all:
            self.when = self.project.node_named("When", "when the Customer adds ++Book++ ++Tiny Tales++ to the ++Cart++", _ADD_BOOK)[0]

        with it("should name each class its links name"):
            expect(_named_by(self.project, self.when)).to(equal([_BOOK, _CART]))

        with it("should be named by the class in turn"):
            book = self.project.graph.practices.named("ddd").reading.in_graph.node(_BOOK)
            expect([edge.child.node_id for edge in self.project.graph.edges.from_parent("namedBy", book)]).to(contain(self.when.node_id))

        with it("should have the example written after a linked term demonstrate that term's class"):
            tiny_tales = self.project.node_named("Example", "Tiny Tales", _ADD_BOOK)[0]
            expect(_demonstrated_by(self.project, tiny_tales)).to(equal([_BOOK]))

    with context("that is written in a story test in code"):
        with before.all:
            self.given = [node for node in self.project.stories.nodes("Given") if node.source.file == _PACK_ORDER and "paid order" in node.name][0]

        with it("should name the class its link names"):
            expect(_named_by(self.project, self.given)).to(equal([_ORDER]))

        with it("should have the example its text names after the link demonstrate that class"):
            paid_order = self.project.node_named("Example", "paid_order", _PACK_ORDER)[0]
            expect(_demonstrated_by(self.project, paid_order)).to(equal([_ORDER]))

    with context("whose link names a heading the domain model does not hold"):
        with before.all:
            scenarios = self.project.root / _ADD_BOOK
            scenarios.write_text(scenarios.read_text(encoding="utf-8").replace("#cart-aggregate-root-entity", "#basket-aggregate-root-entity"), encoding="utf-8")
            self.project.graph.refresh([_ADD_BOOK])
            self.when = self.project.node_named("When", "when the Customer adds ++Book++ ++Tiny Tales++ to the ++Cart++", _ADD_BOOK)[0]

        with it("should name no class for that link"):
            expect(_named_by(self.project, self.when)).to(equal([_BOOK]))
