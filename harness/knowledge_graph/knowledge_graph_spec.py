"""BDD spec for PracticeGraph — loads catalog examples and checks graph shape."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from harness.knowledge_graph.model import Kind, Node, PracticeGraph
from practices.bdd.model.codeql.codeql_model import Description
from practices.stories.model.codeql.codeql_model import Epic, Step


_CATALOG = _REPO_ROOT / "practices" / "stories" / "catalog-examples"


with description("PracticeGraph"):
    with it("should load catalog story map epics by slug"):
        graph = PracticeGraph.load(_CATALOG)
        names = {Node().slug(epic.name) for epic in graph.nodes_of_type(Epic)}
        if graph.story_map is not None:
            names.update(Node().slug(epic.name) for epic in graph.story_map.epics)
        expect(len(graph.nodes) > 0).to(equal(True))
        expect(len(names) > 0 or graph.ce_model is not None).to(equal(True))

    with it("should register scenario steps as graph nodes"):
        graph = PracticeGraph.load(_CATALOG)
        steps = graph.nodes_of_type(Step)
        expect(len(steps) > 0).to(equal(True))
        expect(len(graph.relationships) > 0).to(equal(True))

    with it("should expose explicit from-kind-to relationships"):
        graph = PracticeGraph.load(_CATALOG)
        owns = [r for r in graph.relationships if r.kind == Kind.OWNS]
        expect(len(owns) > 0).to(equal(True))

    with it("should load BDD descriptions from bdd examples"):
        graph = PracticeGraph.load(_REPO_ROOT / "practices" / "bdd" / "examples")
        names = {Node().slug(d.name) for d in graph.nodes_of_type(Description)}
        expect(len(graph.nodes) > 0).to(equal(True))
        expect(len(names) > 0 or graph.ce_model is not None).to(equal(True))
