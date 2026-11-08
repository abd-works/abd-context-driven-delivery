"""A graph saved to its folder's .context and read back holds the same nodes, edges, and violations, each by name."""

import json
import shutil
import tempfile
from pathlib import Path

from expects import be_none, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.graph.graph import Graph
from harness.graph.spec_support import GraphsMade
from harness.installation.destination import data_of
from harness.graph.saved_graph import SavedGraph, SavedGraphFile, SavedGraphOutdated
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.patterns  # noqa: F401 - registers the patterns with the graph's overlays
from harness.graph.pattern_overlays import PatternOverlays
from harness.guidance.practice_catalogue import PracticeCatalogue

_CART = "export class Cart {\n  total() { return 1; }\n  place(a, b, c, d, e, f) { return a; }\n}\n"


def _nodes(graph: Graph) -> list[tuple]:
    practice = graph.practice("clean_engineering")
    found = practice.in_graph.nodes()
    return sorted((node.node_id, node.name, node.type, node.source.file, node.source.start_line, node.source.end_line, node.stage) for node in found)


def _edges(graph: Graph) -> list[tuple]:
    practice = graph.practice("clean_engineering")
    return sorted((edge.parent.node_id, edge.child.node_id, edge.kind, edge.order, edge.display) for edge in practice.in_graph.edges())


def _violations(graph: Graph) -> list[tuple]:
    practice = graph.practice("clean_engineering")
    found = [violation for node in practice.in_graph.nodes() for violation in node.rules.violations]
    return sorted((violation.rule, violation.node_id, violation.subject, violation.location, violation.line, violation.message) for violation in found)


with description("a saved graph"):
    with before.all:
        self.root = Path(tempfile.mkdtemp())
        (self.root / "src").mkdir()
        (self.root / "src" / "cart.ts").write_text(_CART, encoding="utf-8")
        self.graph = Graph()
        self.graph.load_files(str(self.root), ["clean_engineering"], ["src"])
        self.text = self.graph.saved().text
        self.restored = Graph()
        self.restored.restored_from(SavedGraph.from_text(self.text))

    with after.all:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("that is read back"):
        with it("should hold the same nodes at the same lines and stages"):
            expect(_nodes(self.restored)).to(equal(_nodes(self.graph)))

        with it("should hold the same edges"):
            expect(_edges(self.restored)).to(equal(_edges(self.graph)))

        with it("should hold the same violations at the same places"):
            expect(_violations(self.restored)).to(equal(_violations(self.graph)))

        with it("should keep the facts about the practice as a whole on its root"):
            expect(self.restored.practice("clean_engineering").in_graph.root.data).to(
                equal(self.graph.practice("clean_engineering").in_graph.root.facts)
            )

    with context("as its document"):
        with it("should name each node's fields"):
            node = json.loads(self.text)["practices"]["clean_engineering"]["nodes"][0]
            expect(sorted(node)).to(equal(["end_line", "facts", "file", "line", "name", "node_id", "practice", "stage", "type"]))

        with it("should name each edge's fields"):
            edge = json.loads(self.text)["practices"]["clean_engineering"]["edges"][0]
            expect(sorted(edge)).to(equal(["child", "display", "kind", "order", "parent"]))

        with it("should keep each violation as the data a returned node's rule lists"):
            saved = json.loads(self.text)["practices"]["clean_engineering"]["violations"][0]
            returned = data_of(self.graph.return_nodes({"violations": True}))
            hit = next(hit for node in returned for rule in node["rules"] for hit in rule["violations"] if hit["rule"] == saved["rule"])
            expect(saved).to(equal(hit))

        with it("should answer its violations by practice"):
            expect(len(SavedGraph.from_text(self.text).violations(["clean_engineering"]))).to(equal(len(_violations(self.graph))))

    with context("in the shape that kept nodes as lists"):
        with before.all:
            self.old = {"overlays": [], "practices": {"clean_engineering": {"source_root": ".", "nodes": [["id", "Cart", "OoadClass"]]}}}

        with it("should be refused by name"):
            expect(lambda: SavedGraph.from_document(self.old, "graph.json")).to(raise_error(SavedGraphOutdated))

        with it("should read as no saved graph, so the next load reads the folder"):
            saved = self.root / "old" / ".context" / "graph.json"
            saved.parent.mkdir(parents=True)
            saved.write_text(json.dumps(self.old), encoding="utf-8")
            expect(SavedGraphFile(self.root / "old", lambda message: None).read()).to(be_none)




with description("a saved graph asked which rules a practice checks"):
    with before.all:
        self.practice = PracticeCatalogue.create("ddd")
        saved = SavedGraph(PatternOverlays(["lern_domain_driven"]).paths, {})
        with GraphsMade() as self.graphs:
            self.checks = saved.checks_of(self.practice)

    with it("should answer the practice's own rules"):
        expect(list(self.checks)).to(contain(*self.practice.graph_checks()))

    with it("should answer the rules the overlays it was saved with add"):
        expect(list(self.checks)).to(contain("node-repository-parses-on-read"))

    with it("should read no graph back to answer"):
        expect(self.graphs.made).to(equal(0))

    with it("should leave the practice it was asked about out of any graph"):
        expect(self.practice.graph).to(be_none)
