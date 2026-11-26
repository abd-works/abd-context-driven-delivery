"""One module's class model, created from its code in each language, then one common set of examples.

Each language's part is only the setup that creates the project from that language's file (Python, TypeScript,
JavaScript, which hold the same two classes). Every example after that is shared and names no language: it asks the
model for its classes, the graph for its nodes and edges, and a render into each code format for the files it saves,
each of which must be a file the model fidelity declares."""

from expects import contain, equal, expect
from mamba import before, context, description, included_context, it, shared_context

from cdd_guidance.practices.clean_engineering.model.fixtures.ordering_code import OrderingProject

_EXTENSIONS = {"python": "py", "typescript": "ts", "javascript": "js"}

with shared_context("the class model of Ordering"):
    with it("should hold the module's classes in the order its file declares them"):
        expect(self.project.class_names()).to(equal(["CartLine", "Cart"]))

    with it("should give a class the operations its code declares"):
        expect(self.project.operations_of("Cart")).to(equal(["add"]))


with shared_context("the graph of Ordering"):
    with it("should hold a node for each class"):
        expect(self.project.graph_classes()).to(equal(["Cart", "CartLine"]))

    with it("should have a class own the operation it declares"):
        expect(self.project.owned_by("Cart")).to(contain("add"))


with shared_context("the files a render of Ordering saves"):
    with it("should save the module's classes in the module's own file, in each code format"):
        saved = {format: self.project.saved_by_render_to(format) for format in _EXTENSIONS}
        expect(saved).to(equal({format: [f"ordering/ordering.{extension}"] for format, extension in _EXTENSIONS.items()}))

    with it("should save every file at a path the model fidelity declares for its format"):
        undeclared = [path for format in _EXTENSIONS for path in self.project.saved_by_render_to(format) if not self.project.declares(path, format)]
        expect(undeclared).to(equal([]))


with description("a class model created from a module's code") as self:
    with context("written in Python"):
        with before.all:
            self.project = OrderingProject("python")

        with included_context("the class model of Ordering"):
            pass

        with included_context("the graph of Ordering"):
            pass

        with included_context("the files a render of Ordering saves"):
            pass

    with context("written in TypeScript"):
        with before.all:
            self.project = OrderingProject("typescript")

        with included_context("the class model of Ordering"):
            pass

        with included_context("the graph of Ordering"):
            pass

        with included_context("the files a render of Ordering saves"):
            pass

    with context("written in JavaScript"):
        with before.all:
            self.project = OrderingProject("javascript")

        with included_context("the class model of Ordering"):
            pass

        with included_context("the graph of Ordering"):
            pass

        with included_context("the files a render of Ordering saves"):
            pass
