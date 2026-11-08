"""Pattern overlays extend practice query packs without replacing them."""

from pathlib import Path

_HERE = Path(__file__).resolve().parent

from expects import equal, expect
from harness.installation.destination import data_of  # noqa: E402
from mamba import description, it

from harness.graph.graph import EdgeType, Graph, Node, Source
from harness.graph.pattern_overlays import PatternOverlays
import cdd_guidance.patterns  # noqa: F401 - registers the patterns with the graph's overlays


with description("pattern overlays"):
    with it("should resolve a pattern name and a practices folder path to the same root"):
        named = PatternOverlays(["lern_domain_driven"]).paths
        folder = _HERE.parents[1] / "cdd_guidance" / "patterns" / "lern_domain_driven"
        expect(PatternOverlays([str(folder)]).paths).to(equal(named))

    with it("should rebuild the tree from edges that still point at the practice root"):
        graph = Graph()
        graph.open(Path("."))
        practice = graph.practice("ddd")
        root = graph.root_of(practice)
        child = Node(
            practice,
            "Aggregate",
            "ddd:Aggregate:src/account",
            "account",
            Source("src/account.ts", 1, 10),
        )
        graph.hold(child)
        graph.record(EdgeType("owns", 2, "direct"), root, child)
        graph.rebuild_tree(practice)
        expect(len(root.children)).to(equal(1))
        expect(root.children[0].node_id).to(equal(child.node_id))

    with it("should add the lern nodes when that overlay is applied to the example"):
        from harness.graph.graph import Graph

        sample = _HERE / "_examples" / "input"
        graph = Graph()
        roots = {name: str(sample) for name in ("clean_engineering", "stories", "ddd", "bdd", "ux")}
        data_of(graph.load_working_copy(str(sample), roots, database=str(sample), overlays=["lern_domain_driven"], force=True))
        names = {node.type for node in graph.nodes_of(graph.practice("ddd"))}
        expect("NodeRoot" in names).to(equal(True))
        expect("ClientRoot" in names).to(equal(True))
        story_types = {node.type for node in graph.nodes_of(graph.practice("stories"))}
        expect("StoryShared" in story_types).to(equal(True))

    with it("should load the full source file for a lern domain node"):
        from harness.graph.graph import Graph

        sample = _HERE / "_examples" / "input"
        graph = Graph()
        roots = {name: str(sample) for name in ("clean_engineering", "stories", "ddd", "bdd", "ux")}
        data_of(graph.load_working_copy(str(sample), roots, database=str(sample), overlays=["lern_domain_driven"], force=True))
        domain_nodes = [node for node in graph.nodes_of(graph.practice("ddd")) if node.type == "NodeRoot"]
        expect(len(domain_nodes) > 0).to(equal(True))
        node = domain_nodes[0]
        expect(node.source.end_line > 1).to(equal(True))
        expect(len(node.source.text.splitlines()) > 1).to(equal(True))

    with it("should parent lern tier files on their aggregate in the explorer tree"):
        from harness.graph.graph import Graph

        sample = _HERE / "_examples" / "input"
        graph = Graph()
        roots = {name: str(sample) for name in ("clean_engineering", "stories", "ddd", "bdd", "ux")}
        data_of(graph.load_working_copy(str(sample), roots, database=str(sample), overlays=["lern_domain_driven"], force=True))
        ddd_tree = data_of(graph.root_of(graph.practice("ddd")).serialize())

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
