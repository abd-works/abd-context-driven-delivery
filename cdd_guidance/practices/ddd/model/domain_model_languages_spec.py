"""One bounded context's domain model, created from its code in each language, then one common set of examples.

Each language's part is only the setup that creates the project from that language's files (Python, TypeScript,
JavaScript, which hold the same aggregates). Every example after that is shared and names no language: it asks the
domain model for its contexts, aggregates and building blocks, the graph for its nodes, and a render into each code
format for the files it saves, each of which must be a file the model fidelity declares."""

from expects import equal, expect
from mamba import before, context, description, included_context, it, shared_context

from cdd_guidance.practices.ddd.model.fixtures.ordering_domain import OrderingDomain

_EXTENSIONS = {"python": "py", "typescript": "ts", "javascript": "js"}

with shared_context("the domain model of Ordering"):
    with it("should hold the bounded context the code's classes place themselves in"):
        expect(self.domain.context_names()).to(equal(["Ordering"]))

    with it("should hold the context's aggregates in the order the code declares them"):
        expect(self.domain.aggregate_names()).to(equal(["Cart", "Order"]))

    with it("should give each class of an aggregate the building block its code marks it as"):
        expect(self.domain.stereotypes_of("Cart")).to(equal({"Cart": ["Aggregate Root", "Entity"], "CartRepository": ["Repository"]}))


with shared_context("the graph of Ordering"):
    with it("should hold the bounded context its marker file names"):
        expect(self.domain.graph_names("BoundedContext")).to(equal(["Ordering"]))

    with it("should hold an aggregate for each folder of the context that holds an aggregate root, named as its folder is"):
        expect(self.domain.graph_names("Aggregate")).to(equal(["cart", "order"]))


with shared_context("the files a render of Ordering saves"):
    with it("should save each aggregate's classes in the aggregate's own file, in each code format"):
        saved = {format: self.domain.saved_by_render_to(format) for format in _EXTENSIONS}
        expect(saved).to(equal({format: [f"ordering/cart/cart.{extension}", f"ordering/order/order.{extension}"] for format, extension in _EXTENSIONS.items()}))

    with it("should save every file at a path the model fidelity declares for its format"):
        undeclared = [path for format in _EXTENSIONS for path in self.domain.saved_by_render_to(format) if not self.domain.declares(path, format)]
        expect(undeclared).to(equal([]))


with description("a domain model created from a bounded context's code") as self:
    with context("written in Python"):
        with before.all:
            self.domain = OrderingDomain("python")

        with included_context("the domain model of Ordering"):
            pass

        with included_context("the graph of Ordering"):
            pass

        with included_context("the files a render of Ordering saves"):
            pass

    with context("written in TypeScript"):
        with before.all:
            self.domain = OrderingDomain("typescript")

        with included_context("the domain model of Ordering"):
            pass

        with included_context("the graph of Ordering"):
            pass

        with included_context("the files a render of Ordering saves"):
            pass

    with context("written in JavaScript"):
        with before.all:
            self.domain = OrderingDomain("javascript")

        with included_context("the domain model of Ordering"):
            pass

        with included_context("the graph of Ordering"):
            pass

        with included_context("the files a render of Ordering saves"):
            pass
