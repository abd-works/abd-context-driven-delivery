"""The graph's tools report the same practice counts as Graph, a node-type filter keeps that type, and a node opens on its source."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import contain, equal, expect
from mamba import before, context, description, it

from graph import Graph

_SAMPLE = _HERE / "_examples" / "input"
_PRACTICES = ["clean_engineering", "stories", "ddd", "bdd", "ux"]


def direct_counts(graph: Graph, practice: str) -> dict[str, int]:
    loaded = graph.practice(practice)
    return {name: loaded.node_count(name) for name in loaded.node_types}


with description("an example graph"):
    with context("that the app has loaded"):
        with before.all:
            self.graph = Graph()
            roots = {name: str(_SAMPLE) for name in _PRACTICES}
            self.graph.load_working_copy(str(_HERE), roots, database=str(_SAMPLE))
            self.inventory = self.graph.inventory()["practices"]

        with context("with clean engineering"):
            with it("should count the same nodes as the graph"):
                expect(self.inventory["clean_engineering"]["node_counts"]).to(equal(direct_counts(self.graph, "clean_engineering")))

            with it("should count the same edges as the graph"):
                expect(self.inventory["clean_engineering"]["edge_count"]).to(equal(self.graph.practice("clean_engineering").edge_count))

            with it("should list the same node types as the graph"):
                expect(self.inventory["clean_engineering"]["node_types"]).to(equal(sorted(self.graph.practice("clean_engineering").node_types)))

        with context("with stories"):
            with it("should count the same nodes as the graph"):
                expect(self.inventory["stories"]["node_counts"]).to(equal(direct_counts(self.graph, "stories")))

            with it("should count the same edges as the graph"):
                expect(self.inventory["stories"]["edge_count"]).to(equal(self.graph.practice("stories").edge_count))

            with it("should list the same node types as the graph"):
                expect(self.inventory["stories"]["node_types"]).to(equal(sorted(self.graph.practice("stories").node_types)))

        with context("with domain driven design"):
            with it("should count the same nodes as the graph"):
                expect(self.inventory["ddd"]["node_counts"]).to(equal(direct_counts(self.graph, "ddd")))

            with it("should count the same edges as the graph"):
                expect(self.inventory["ddd"]["edge_count"]).to(equal(self.graph.practice("ddd").edge_count))

            with it("should list the same node types as the graph"):
                expect(self.inventory["ddd"]["node_types"]).to(equal(sorted(self.graph.practice("ddd").node_types)))

        with context("with behavior driven development"):
            with it("should count the same nodes as the graph"):
                expect(self.inventory["bdd"]["node_counts"]).to(equal(direct_counts(self.graph, "bdd")))

            with it("should count the same edges as the graph"):
                expect(self.inventory["bdd"]["edge_count"]).to(equal(self.graph.practice("bdd").edge_count))

            with it("should list the same node types as the graph"):
                expect(self.inventory["bdd"]["node_types"]).to(equal(sorted(self.graph.practice("bdd").node_types)))

        with context("with experience design"):
            with it("should count the same nodes as the graph"):
                expect(self.inventory["ux"]["node_counts"]).to(equal(direct_counts(self.graph, "ux")))

            with it("should count the same edges as the graph"):
                expect(self.inventory["ux"]["edge_count"]).to(equal(self.graph.practice("ux").edge_count))

            with it("should list the same node types as the graph"):
                expect(self.inventory["ux"]["node_types"]).to(equal(sorted(self.graph.practice("ux").node_types)))

        with context("with operations selected"):
            with before.all:
                self.rows = self.graph.return_nodes({"practices": ["clean_engineering"], "types": ["Operation"]})

            with it("should return operation nodes"):
                expect({row["type"] for row in self.rows}).to(equal({"Operation"}))

            with it("should count the same operations as the graph"):
                expect(len(self.rows)).to(equal(self.graph.practice("clean_engineering").node_count("Operation")))

        with context("with clean engineering chosen in the filter"):
            with it("should offer the node types clean engineering holds"):
                expect(self.graph.filter_choices(["clean_engineering"], [])["node_types"]).to(contain("Operation"))

            with it("should leave nothing chosen for the next filter"):
                self.graph.filter_choices(["clean_engineering"], ["Operation"])
                expect(self.graph.filter.practices).to(equal([]))

        with context("with an operation opened"):
            with before.all:
                operation = self.graph.return_nodes({"practices": ["clean_engineering"], "types": ["Operation"]})[0]
                self.opened = self.graph.source(operation["node_id"])

            with it("should name the file the operation sits in"):
                expect(self.opened["file"]).to(contain("."))

            with it("should hold the classes and operations a call in it can open"):
                expect({member["kind"] for member in self.opened["members"]}).to(contain("Operation"))

        with context("with an id the graph holds no node for, such as a rule's row"):
            with it("should have no source to show"):
                expect(self.graph.source("no-such-node")).to(equal(None))

