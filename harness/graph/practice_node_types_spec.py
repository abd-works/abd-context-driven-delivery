"""The node type tables a graph reads, joined from what each registered practice and pattern says of its own types."""
from expects import be_none, be_true, equal, expect, raise_error
from mamba import before, context, description, it

from harness.graph.practice_node_types import NodeTypeTables, NodeTypeTablesDisagree, PracticeNodeTypes


class _CodeTypes(PracticeNodeTypes):
    schema_node_types = {"class": "OoadClass"}
    child_lists = frozenset({"participants"})
    edge_order = {"participants": 1, "invokes": 12}


class _StepTypes(PracticeNodeTypes):
    schema_node_types = {"given": "Step", "then": "Step"}
    child_lists = frozenset({"steps"})
    edge_order = {"steps": 4, "invokes": 12}


class _OtherInvokes(PracticeNodeTypes):
    edge_order = {"invokes": 3}


class _Registered:
    """What a registry gives the tables: the node types of each class registered with it."""

    def __init__(self, *types: PracticeNodeTypes) -> None:
        self.types = list(types)

    def node_types(self) -> tuple[PracticeNodeTypes, ...]:
        return tuple(self.types)


def _tables(*types: PracticeNodeTypes) -> NodeTypeTables:
    return NodeTypeTables(_Registered(*types))


with description("node type tables") as self:
    with context("joined from two practices"):
        with before.each:
            self.tables = _tables(_CodeTypes(), _StepTypes())

        with it("should give a kind the place its practice names"):
            expect(self.tables.order_of("steps")).to(equal(4))

        with it("should give a kind two practices name the one place both give it"):
            expect(self.tables.order_of("invokes")).to(equal(12))

        with it("should give the graph's own kinds their place whichever practices it holds"):
            expect((self.tables.order_of("owns"), self.tables.order_of("belongsTo"))).to(equal((2, 5)))

        with it("should place no kind no practice names"):
            expect(self.tables.order_of("route")).to(be_none)

        with it("should name the node type of a schema key a practice names"):
            expect(self.tables.node_type_of("class")).to(equal("OoadClass"))

        with it("should write a node type as the first key that names it"):
            expect(self.tables.key_of("Step")).to(equal("given"))

        with it("should hold each practice's child lists and the graph's back-edge"):
            expect([self.tables.is_child_list(kind) for kind in ("participants", "steps", "belongsTo", "invokes")]).to(equal([True, True, True, False]))

    with context("whose practices place one kind in two places"):
        with it("should refuse to choose one, naming the kind"):
            tables = _tables(_CodeTypes(), _OtherInvokes())
            expect(lambda: tables.order_of("invokes")).to(raise_error(NodeTypeTablesDisagree, "the edge order gives 'invokes' both 12 and 3; give it one, in every practice and pattern that names it"))

    with context("before any practice is registered"):
        with it("should still place the graph's own kinds"):
            expect(_tables().order_of("root")).to(equal(1))

    with context("whose registered practices change"):
        with it("should join the tables again"):
            practices = _Registered(_CodeTypes())
            tables = NodeTypeTables(practices)
            tables.order_of("participants")
            practices.types = [_StepTypes()]
            expect(tables.is_child_list("steps")).to(be_true)

    with context("that a source joins later"):
        with it("should read its node types from then on"):
            tables = _tables(_CodeTypes())
            tables.order_of("participants")
            tables.read_from(_Registered(_StepTypes()))
            expect(tables.order_of("steps")).to(equal(4))
