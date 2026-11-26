"""A practice's explorer tree, built from its edges: a long chain of relationship edges, such as operations each
invoking the next, is placed whole, however much deeper it runs than Python's call stack."""

import sys

from expects import equal, expect
from mamba import before, description, it

from harness.graph.graph import Graph
from harness.graph.location import Location
import cdd_guidance.practices  # noqa: F401 - registers the practices a graph holds

# Deeper than the call stack a node placing its children by calling itself could reach.
_CHAIN = sys.getrecursionlimit() * 2


with description("a practice's explorer tree"):
    with description("with a chain of operations each invoking the next"):
        with before.all:
            graph = Graph()
            practice = graph.practices.named("clean_engineering")
            self.part = practice.reading.in_graph
            cart = self.part.add_file("OoadClass", "cart.py", "Cart")
            graph.edges.link("owns", self.part.root, cart)
            operations = [
                self.part.add_file("Operation", f"step{index}")
                for index in range(_CHAIN)
            ]
            for caller, called in zip(operations, operations[1:]):
                graph.edges.link("owns", cart, caller)
                graph.edges.relate("invokes", caller, called)
            graph.edges.link("owns", cart, operations[-1])
            self.part.root.tree.rebuild()
            self.last = operations[-1]
            self.cart = cart

        with it("should place the last operation of the chain under its class"):
            expect(self.last.parent).to(equal(self.cart))

    with description("with parts of two kinds its practice lists in source order, written in turn in one file"):
        with before.all:
            graph = Graph()
            self.part = graph.practices.named("stories").reading.in_graph
            story = self.part.add_file("Story", "order.md", "Place Order")
            graph.edges.link("owns", self.part.root, story)
            placed = [("Scenario", "scenarios", "first", 2), ("Background", "background", "shared", 5), ("Scenario", "scenarios", "second", 8)]
            for type, kind, name, line in placed:
                node = self.part.add_file(type, f"{name}.md", name)
                node.place(Location("order.md", line, line))
                graph.edges.link(kind, story, node)
            self.part.root.tree.rebuild()
            self.story = story

        with it("should place them in the order the file writes them, whatever their kind"):
            expect([child.name for child in self.story.children]).to(equal(["first", "shared", "second"]))

    with description("with packages read from folders, some placed at its root and one under another package"):
        with before.all:
            graph = Graph()
            self.part = graph.practices.named("clean_engineering").reading.in_graph
            self.packages = {}
            for relative in ["src", "bookshop/src", "story_tests"]:
                self.packages[relative] = self.part.add_file("Package", relative, relative.rsplit("/", 1)[-1])
                graph.edges.link("owns", self.part.root, self.packages[relative])
            confirm = self.part.add_file("Package", "story_tests/check-out/confirm-order", "confirm-order")
            graph.edges.link("owns", self.packages["story_tests"], confirm)
            self.part.root.tree.rebuild()
            self.top = self.part.root.tree.serialize().children
            self.confirm = confirm

        with it("should label each package at the root by its path from the root"):
            expect([entry.label for entry in self.top]).to(equal(["src", "bookshop/src", "story_tests"]))

        with it("should label a package under another by its path from that package's folder"):
            expect(self.top[2].children[0].label).to(equal("check-out/confirm-order"))

        with it("should keep the label when its branch is read on its own"):
            expect(self.confirm.tree.serialize(via=self.confirm.parent).label).to(equal("check-out/confirm-order"))

    with description("with two classes of one name in two files and a class whose name no other shares"):
        with before.all:
            graph = Graph()
            self.part = graph.practices.named("clean_engineering").reading.in_graph
            for relative, name in [("ordering/order.py", "Order"), ("ordering/order.ts", "Order"), ("ordering/cart.py", "Cart")]:
                graph.edges.link("owns", self.part.root, self.part.add_file("OoadClass", relative, name))
            self.part.root.tree.rebuild()
            self.labels = [entry.label for entry in self.part.root.tree.serialize().children]

        with it("should label each of the two by its name and its file"):
            expect(self.labels[:2]).to(equal(["Order (order.py)", "Order (order.ts)"]))

        with it("should label the class no other shares a name with by its name alone"):
            expect(self.labels[2]).to(equal("Cart"))

    with description("with two classes of one name in two files of one name"):
        with before.all:
            graph = Graph()
            self.part = graph.practices.named("clean_engineering").reading.in_graph
            for relative in ["catalogue/views.py", "ordering/views.py"]:
                graph.edges.link("owns", self.part.root, self.part.add_file("OoadClass", relative, "_module"))
            self.part.root.tree.rebuild()
            self.labels = [entry.label for entry in self.part.root.tree.serialize().children]

        with it("should label each by its name and its file's path"):
            expect(self.labels).to(equal(["_module (catalogue/views.py)", "_module (ordering/views.py)"]))

    with description("with a step whose text links a term to its definition"):
        with before.all:
            graph = Graph()
            self.part = graph.practices.named("stories").reading.in_graph
            step = self.part.add_file("Step", "submit_order_story.test.py", "given the Customer has [Cart](../../.context/domain-model.md#cart) cart with Tiny Tales")
            graph.edges.link("owns", self.part.root, step)
            self.part.root.tree.rebuild()
            self.entry = self.part.root.tree.serialize().children[0]

        with it("should label the step by its sentence, with the link's text in place of the link"):
            expect(self.entry.label).to(equal("given the Customer has Cart cart with Tiny Tales"))

        with it("should keep the step's name as its text holds it"):
            expect(self.entry.name).to(equal("given the Customer has [Cart](../../.context/domain-model.md#cart) cart with Tiny Tales"))
