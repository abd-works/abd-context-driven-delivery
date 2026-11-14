"""Pattern overlays extend practice query packs without replacing them."""

import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent

from expects import equal, expect
from harness.installation.data_class import data_of  # noqa: E402
from mamba import before, context, description, it

from harness.graph.edge import EdgeType
from harness.graph.graph import Graph, Node, Source
from harness.graph.pattern_overlays import PatternOverlays
import cdd_guidance.patterns  # noqa: F401 - registers the patterns with the graph's overlays


def _sample_copy() -> Path:
    """A throwaway copy of the example working copy, so the graph a load saves in its ``.context`` never lands in the
    shared sample that other specs, such as validate's, copy and read back."""
    import shutil

    copy = Path(tempfile.mkdtemp(prefix="cdd-graph-spec-")) / "input"
    shutil.copytree(_HERE / "_examples" / "input", copy, ignore=shutil.ignore_patterns("graph.json"))
    return copy


with description("pattern overlays") as self:
    with it("should resolve a pattern name and a practices folder path to the same root"):
        named = PatternOverlays(["lern_domain_driven"]).paths
        folder = _HERE.parents[1] / "cdd_guidance" / "patterns" / "lern_domain_driven"
        expect(PatternOverlays([str(folder)]).paths).to(equal(named))

    with it("should rebuild the tree from edges that still point at the practice root"):
        graph = Graph()
        graph.open(Path("."))
        practice = graph.practice("ddd")
        root = practice.reading.in_graph.root
        child = Node(
            practice,
            "Aggregate",
            "ddd:Aggregate:src/account",
            "account",
            Source("src/account.ts", 1, 10),
        )
        child.practice.reading.in_graph.hold(child)
        graph.record(EdgeType("owns", 2, "direct"), root, child)
        practice.reading.in_graph.rebuild_tree()
        expect(len(root.children)).to(equal(1))
        expect(root.children[0].node_id).to(equal(child.node_id))

    # Every example here only reads the graph, so the example is loaded once for them all.
    with context("with the lern overlay applied to a copy of the example"):
        with before.all:
            sample = _sample_copy()
            self.graph = Graph()
            roots = {name: str(sample) for name in ("clean_engineering", "stories", "ddd", "bdd", "ux")}
            data_of(self.graph.load_working_copy(str(sample), roots, database=str(sample), overlays=["lern_domain_driven"], force=True))

        with it("should add the lern nodes"):
            names = {node.type for node in self.graph.practice("ddd").reading.in_graph.nodes()}
            expect("NodeRoot" in names).to(equal(True))
            expect("ClientRoot" in names).to(equal(True))
            story_types = {node.type for node in self.graph.practice("stories").reading.in_graph.nodes()}
            expect("StoryShared" in story_types).to(equal(True))

        with it("should load the full source file for a lern domain node"):
            domain_nodes = [node for node in self.graph.practice("ddd").reading.in_graph.nodes() if node.type == "NodeRoot"]
            expect(len(domain_nodes) > 0).to(equal(True))
            node = domain_nodes[0]
            expect(node.source.end_line > 1).to(equal(True))
            expect(len(node.source.text.splitlines()) > 1).to(equal(True))

        with it("should parent lern tier files on their aggregate in the explorer tree"):
            ddd_tree = data_of(self.graph.practice("ddd").reading.in_graph.root.serialize())

            def walk(node):
                yield node
                for child in node.get("children") or []:
                    yield from walk(child)

            aggregate = next(
                item for item in walk(ddd_tree) if item.get("type") == "Aggregate" and item.get("name") == "account-credentials"
            )
            child_names = [child.get("name") for child in aggregate.get("children") or []]
            expect("account-credentials-node" in child_names).to(equal(True))
            expect("account-credentials-client" in child_names).to(equal(True))


with description("pattern overlays recording what content is generated with") as self:
    with it("should give each pattern's roles from its layer table"):
        overlay = PatternOverlays(["cdd_web_domain_access"]).patterns[0].graph_overlay
        expect(overlay.roles).to(equal(["Domain", "Tool", "Contract", "Annotation", "Language adapter", "Connection"]))

    with it("should name the patterns recorded for content where it was generated"):
        root = Path(tempfile.mkdtemp())
        app = root / "app"
        (app / "src").mkdir(parents=True)
        overlays = PatternOverlays(["lern_domain_driven", "cdd_web_domain_access"])
        overlays.record_content([app])
        expect(PatternOverlays().recorded_for([app / "src" / "board.tsx"], root)).to(equal(["lern_domain_driven", "cdd_web_domain_access"]))

    with it("should name none for content no folder records"):
        root = Path(tempfile.mkdtemp())
        expect(PatternOverlays().recorded_for([root / "board.tsx"], root)).to(equal([]))
