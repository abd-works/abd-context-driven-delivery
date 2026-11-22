"""A node answers the fidelity it was read at, which its practice's reading records as it reads. The fidelity is a
matter of what the content holds, never of the format it is written in: a class whose operations have no bodies is at
the model fidelity, in code, in a model document, or in a drawing, and once an operation has a body the class is at the
code fidelity. A rule of the code fidelity leaves a node at the model fidelity out."""

from pathlib import Path

from expects import be_false, be_true, equal, expect
from mamba import before, context, description, included_context, it, shared_context

from harness.graph.graph import Graph, Node, Source
from harness.graph.rule_fixture import RuleFixture
from harness.graph.saved_graph import NodeIdentity
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering

# One class in each language, first with no body in any operation, then with a body in one.
_SOURCES = {
    "python": {
        "file": "order.py",
        "without_bodies": 'class Order:\n    total: int\n\n    def place(self, customer):\n        """Place the order for customer."""\n\n    def cancel(self):\n        raise NotImplementedError\n',
        "with_a_body": 'class Order:\n    total: int\n\n    def place(self, customer):\n        self.total = customer.basket.total\n\n    def cancel(self):\n        raise NotImplementedError\n',
    },
    "typescript": {
        "file": "order.ts",
        "without_bodies": "export class Order {\n  total: number = 0;\n\n  place(customer: Customer): void {}\n\n  cancel(): void {\n    throw new Error('not implemented');\n  }\n}\n",
        "with_a_body": "export class Order {\n  total: number = 0;\n\n  place(customer: Customer): void {\n    this.total = customer.basket.total;\n  }\n\n  cancel(): void {\n    throw new Error('not implemented');\n  }\n}\n",
    },
}
_MODEL_DOCUMENT = "# Order model\n\n## Module: orders\n\n**Order**\n- total: Number\n- place(customer)\n- cancel()\n"


def _read(file: str, text: str) -> dict[str, str]:
    """The fidelity each node read from one file answers, by the node's type and name."""
    nodes = RuleFixture(CleanEngineering, {file: text}).practice.reading.in_graph.nodes()
    return {f"{node.type} {node.name}": node.fidelity_read_at for node in nodes if node.type in ("OoadClass", "Operation", "Property", "Parameter")}


def _class_with_an_operation() -> tuple[Node, Node]:
    """A class node and an operation node under it, as a reading holds them, with no fidelity recorded yet."""
    graph = Graph()
    graph.reads.open(Path("."))
    practice = graph.practices.named("clean_engineering")
    order = Node(practice, NodeIdentity(type="OoadClass", node_id="clean_engineering:OoadClass:Order", name="Order"), Source("order.py", 1, 8))
    place = Node(practice, NodeIdentity(type="Operation", node_id="clean_engineering:Operation:Order.place", name="place"), Source("order.py", 4, 5))
    place.parent = order
    return order, place


with description("the fidelity a node was read at"):
    with context("on a class a reading recorded at the code fidelity"):
        with before.each:
            self.order, self.place = _class_with_an_operation()
            self.order.read_at("code")

        with it("should be answered by the class"):
            expect(self.order.fidelity_read_at).to(equal("code"))

        with it("should be answered by an operation of the class, which takes its class's fidelity"):
            expect(self.place.fidelity_read_at).to(equal("code"))

        with it("should say the operation is read at the code fidelity, for a rule of that fidelity to judge it"):
            expect(self.place.is_read_at("code")).to(be_true)

        with it("should say the operation is not read at the model fidelity"):
            expect(self.place.is_read_at("model")).to(be_false)

    with context("on a class no reading recorded a fidelity for"):
        with it("should be none, so no rule mistakes it for either fidelity"):
            order, _ = _class_with_an_operation()
            expect((order.fidelity_read_at, order.is_read_at("code"), order.is_read_at("model"))).to(equal(("", False, False)))


# Clean Engineering's reading records the fidelity of each class it reads, the same way in every language.
with shared_context("a class read from code"):
    with context("whose operations have no bodies"):
        with before.all:
            self.read = _read(self.source["file"], self.source["without_bodies"])

        with it("should be at the model fidelity"):
            expect(self.read["OoadClass Order"]).to(equal("model"))

        with it("should have its operations, properties and parameters at the model fidelity"):
            expect({self.read[part] for part in ("Operation place", "Operation cancel", "Property total", "Parameter customer")}).to(equal({"model"}))

    with context("one of whose operations has a body"):
        with before.all:
            self.read = _read(self.source["file"], self.source["with_a_body"])

        with it("should be at the code fidelity"):
            expect(self.read["OoadClass Order"]).to(equal("code"))

        with it("should have its operations, properties and parameters at the code fidelity, the one with no body too"):
            expect({self.read[part] for part in ("Operation place", "Operation cancel", "Property total", "Parameter customer")}).to(equal({"code"}))


with description("the fidelity Clean Engineering reads a class at") as self:
    with context("in Python"):
        with before.all:
            self.source = _SOURCES["python"]

        with included_context("a class read from code"):
            pass

    with context("in TypeScript"):
        with before.all:
            self.source = _SOURCES["typescript"]

        with included_context("a class read from code"):
            pass

    with context("in a model document, which holds no bodies"):
        with it("should be at the model fidelity"):
            read = _read(".context/order-model.md", _MODEL_DOCUMENT)
            expect({fidelity for name, fidelity in read.items() if name.startswith("OoadClass")}).to(equal({"model"}))
