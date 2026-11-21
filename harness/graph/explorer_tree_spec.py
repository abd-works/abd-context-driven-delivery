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
