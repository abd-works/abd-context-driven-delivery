"""Pattern overlays extend practice query packs without replacing them."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import equal, expect
from mamba import description, it

from graph import Edge, EdgeType, Node, PracticeGraph, Source, normalize_overlay, resolve_overlay_root


with description("pattern overlays"):
    with it("should resolve a pattern name and a practices folder path to the same root"):
        named = resolve_overlay_root("lern_domain_driven")
        folder = _HERE.parents[1] / "patterns" / "lern_domain_driven"
        expect(normalize_overlay(str(folder))).to(equal(str(named.resolve())))

    with it("should rebuild the tree from edges that still point at the practice root"):
        practice = PracticeGraph("ddd")
        practice.source_root = "."
        root = practice.root_node
        child = Node(
            practice,
            "Aggregate",
            "ddd:Aggregate:src/account",
            "account",
            Source("src/account.ts", 1, 10),
        )
        practice.by_id[child.node_id] = child
        practice.nodes.setdefault("Aggregate", []).append(child)
        practice.edge_types["owns"] = EdgeType("owns", 2, "direct")
        practice.edges["owns"] = [Edge("owns", 2, "direct", root, child)]
        practice.rebuild_tree()
        expect(len(practice.root_node.children)).to(equal(1))
        expect(practice.root_node.children[0].node_id).to(equal(child.node_id))

    with it("should add the lern nodes when that overlay is applied to the example"):
        from graph import Graph

        sample = _HERE / "examples" / "input"
        graph = Graph()
        roots = {name: str(sample) for name in ("clean_engineering", "stories", "ddd", "bdd", "ux")}
        graph.load_working_copy(str(sample), roots, database=str(sample), overlays=["lern_domain_driven"])
        names = {node.type for node in graph.practice("ddd").by_id.values()}
        expect("DomainNode" in names).to(equal(True))
        expect("DomainClient" in names).to(equal(True))
        story_types = {node.type for node in graph.practice("stories").by_id.values()}
        expect("StoryShared" in story_types).to(equal(True))
