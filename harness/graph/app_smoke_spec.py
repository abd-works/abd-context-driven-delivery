"""The graph's tools report the same practice counts as Graph, a node-type filter keeps that type, and a node opens on its source."""

import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent

from expects import contain, equal, expect
from harness.installation.data_class import data_of  # noqa: E402
from mamba import before, context, description, it

from harness.graph.graph import Graph
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

_SAMPLE = _HERE / "_examples" / "input"
_PRACTICES = ["clean_engineering", "stories", "ddd", "bdd", "ux"]


def direct_counts(graph: Graph, practice: str) -> dict[str, int]:
    loaded = graph.practice(practice)
    return {name: len(loaded.reading.in_graph.nodes(name)) for name in loaded.reading.in_graph.node_types}


with description("an example graph"):
    with context("that the app has loaded"):
        with before.all:
            self.graph = Graph()
            roots = {name: str(_SAMPLE) for name in _PRACTICES}
            data_of(self.graph.load_working_copy(str(_HERE), roots, database=tempfile.mkdtemp(prefix="cdd-graph-spec-")))
            self.inventory = data_of(self.graph.inventory())["practices"]

        with context("with clean engineering"):
            with it("should count the same nodes as the graph"):
                expect(self.inventory["clean_engineering"]["node_counts"]).to(equal(direct_counts(self.graph, "clean_engineering")))

            with it("should count the same edges as the graph"):
                expect(self.inventory["clean_engineering"]["edge_count"]).to(equal(len(self.graph.practice("clean_engineering").reading.in_graph.edges())))

            with it("should list the same node types as the graph"):
                expect(self.inventory["clean_engineering"]["node_types"]).to(equal(sorted(self.graph.practice("clean_engineering").reading.in_graph.node_types)))

        with context("with stories"):
            with it("should count the same nodes as the graph"):
                expect(self.inventory["stories"]["node_counts"]).to(equal(direct_counts(self.graph, "stories")))

            with it("should count the same edges as the graph"):
                expect(self.inventory["stories"]["edge_count"]).to(equal(len(self.graph.practice("stories").reading.in_graph.edges())))

            with it("should list the same node types as the graph"):
                expect(self.inventory["stories"]["node_types"]).to(equal(sorted(self.graph.practice("stories").reading.in_graph.node_types)))

        with context("with domain driven design"):
            with it("should count the same nodes as the graph"):
                expect(self.inventory["ddd"]["node_counts"]).to(equal(direct_counts(self.graph, "ddd")))

            with it("should count the same edges as the graph"):
                expect(self.inventory["ddd"]["edge_count"]).to(equal(len(self.graph.practice("ddd").reading.in_graph.edges())))

            with it("should list the same node types as the graph"):
                expect(self.inventory["ddd"]["node_types"]).to(equal(sorted(self.graph.practice("ddd").reading.in_graph.node_types)))

        with context("with behavior driven development"):
            with it("should count the same nodes as the graph"):
                expect(self.inventory["bdd"]["node_counts"]).to(equal(direct_counts(self.graph, "bdd")))

            with it("should count the same edges as the graph"):
                expect(self.inventory["bdd"]["edge_count"]).to(equal(len(self.graph.practice("bdd").reading.in_graph.edges())))

            with it("should list the same node types as the graph"):
                expect(self.inventory["bdd"]["node_types"]).to(equal(sorted(self.graph.practice("bdd").reading.in_graph.node_types)))

        with context("with experience design"):
            with it("should count the same nodes as the graph"):
                expect(self.inventory["ux"]["node_counts"]).to(equal(direct_counts(self.graph, "ux")))

            with it("should count the same edges as the graph"):
                expect(self.inventory["ux"]["edge_count"]).to(equal(len(self.graph.practice("ux").reading.in_graph.edges())))

            with it("should list the same node types as the graph"):
                expect(self.inventory["ux"]["node_types"]).to(equal(sorted(self.graph.practice("ux").reading.in_graph.node_types)))

        with context("with operations selected"):
            with before.all:
                self.rows = data_of(self.graph.return_nodes({"practices": ["clean_engineering"], "types": ["Operation"]}))

            with it("should return operation nodes"):
                expect({row["type"] for row in self.rows}).to(equal({"Operation"}))

            with it("should count the same operations as the graph"):
                expect(len(self.rows)).to(equal(len(self.graph.practice("clean_engineering").reading.in_graph.nodes("Operation"))))

        with context("with clean engineering chosen in the filter"):
            with it("should offer the node types clean engineering holds"):
                expect(data_of(self.graph.filter_choices(["clean_engineering"], []))["offered_node_types"]).to(contain("Operation"))

            with it("should offer the relationships of every node type when none is chosen"):
                expect(data_of(self.graph.filter_choices(["clean_engineering"], []))["relationships"]).not_to(equal([]))

            with it("should leave nothing chosen for the next filter"):
                data_of(self.graph.filter_choices(["clean_engineering"], ["Operation"]))
                expect(self.graph.filter.practices).to(equal([]))

        with context("with no practice chosen in the filter"):
            with it("should offer every node type the loaded practices hold"):
                offered = data_of(self.graph.filter_choices([], []))["offered_node_types"]
                expect(set(offered)).to(equal({node_type for name in _PRACTICES for node_type in self.graph.practice(name).reading.in_graph.node_types}))

            with it("should offer the rules of every practice"):
                rules = data_of(self.graph.filter_choices([], []))["rules"]
                expect({rule.split(".")[0] for rule in rules}).to(contain("stories", "clean_engineering"))

        with context("with clean engineering narrowed to operations and stories added"):
            with before.all:
                self.changed = data_of(self.graph.filter_choices(["clean_engineering", "stories"], ["Operation"], practices_before=["clean_engineering"]))

            with it("should keep operations chosen"):
                expect(self.changed["node_types"]).to(contain("Operation"))

            with it("should leave the other clean engineering node types unchosen"):
                expect(self.changed["node_types"]).not_to(contain("OoadClass"))

            with it("should choose every node type stories holds"):
                expect(set(self.graph.practice("stories").reading.in_graph.node_types) - set(self.changed["node_types"])).to(equal(set()))

            with it("should offer every node type of both practices"):
                expect(self.changed["offered_node_types"]).to(contain("OoadClass"))

            with it("should offer the relationships of the chosen node types"):
                chosen = data_of(self.graph.filter_choices(["clean_engineering", "stories"], self.changed["node_types"]))
                expect(self.changed["relationships"]).to(equal(chosen["relationships"]))

        with context("with an operation opened"):
            with before.all:
                operation = data_of(self.graph.return_nodes({"practices": ["clean_engineering"], "types": ["Operation"]}))[0]
                self.opened = data_of(self.graph.source(operation["node_id"]))

            with it("should name the file the operation sits in"):
                expect(self.opened["file"]).to(contain("."))

            with it("should hold the classes and operations a call in it can open"):
                expect({member["type"] for member in self.opened["members"]}).to(contain("Operation"))

        with context("with an id the graph holds no node for, such as a rule's row"):
            with it("should have no source to show"):
                expect(self.graph.source("no-such-node")).to(equal(None))

