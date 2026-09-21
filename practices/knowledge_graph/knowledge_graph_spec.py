"""BDD spec for PracticeGraph — loads catalog examples and checks graph shape."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, equal, expect
from mamba import description, it

from practices.knowledge_graph.model import GraphStep, Kind, PracticeGraph
from practices.knowledge_graph.model.nodes import slug


_CATALOG = _REPO_ROOT / "practices" / "stories" / "catalog-examples"


with description("PracticeGraph"):
    with it("should load catalog story map epics by slug"):
        graph = PracticeGraph.load(_CATALOG)
        expect(len(graph.epics)).to(be_true)
        expect("onboard-a-customer" in graph.epics).to(be_true)

    with it("should register scenario steps as graph nodes"):
        graph = PracticeGraph.load(_CATALOG)
        steps = graph.nodes_of_type(GraphStep)
        expect(len(steps)).to(be_true)
        expect(len(graph.relationships)).to(be_true)

    with it("should expose explicit from-kind-to relationships"):
        graph = PracticeGraph.load(_CATALOG)
        owns = [r for r in graph.relationships if r.kind == Kind.OWNS]
        expect(len(owns)).to(be_true)

    with it("should load BDD descriptions from bdd examples"):
        graph = PracticeGraph.load(_REPO_ROOT / "practices" / "bdd" / "examples")
        expect(len(graph.descriptions)).to(be_true)
        expect("a-character" in graph.descriptions).to(be_true)
