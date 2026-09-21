"""BDD spec for practice graph DOT export."""

import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, contain, equal, expect
from mamba import description, it

from practices.knowledge_graph.model import Kind, PracticeGraph

_CATALOG = _REPO_ROOT / "practices" / "stories" / "catalog-examples"
_PML = Path(os.environ.get("PML_DOMAINMODEL", r"C:\dev\paradise-mobile\pml-domainmodel"))


with description("PracticeGraph dot_graph"):
    with it("should expose a DOT digraph from the stories root"):
        graph = PracticeGraph.load(_CATALOG)
        dot = graph.stories_dot_graph
        expect(dot).to(contain("digraph"))
        expect(dot).to(contain("StoryMap"))
        expect(dot).to(contain("Epic"))
        expect(dot).to(contain("onboard-a-customer"))
        expect(dot).to(contain(f'[label="{Kind.OWNS}"]'))

    with it("should include owned descendants on any graph node"):
        graph = PracticeGraph.load(_CATALOG)
        epic = graph.epics["onboard-a-customer"]
        dot = epic.dot_graph
        expect(dot).to(contain("SubEpic"))
        expect(dot).to(contain("Story"))
        expect(dot).to(contain("Scenario"))
        expect(dot).to(contain("Step"))

    with it("should merge practice roots on PracticeGraph.dot_graph"):
        graph = PracticeGraph.load(_CATALOG)
        dot = graph.dot_graph
        expect(dot).to(contain("StoryMap"))
        expect(dot.count("->") > 0).to(equal(True))


if _PML.is_dir():
    with description("PracticeGraph dot_graph on pml-domainmodel"):
        with it("should load stories hierarchy from the Paradise workspace"):
            graph = PracticeGraph.load(_PML)
            dot = graph.stories_dot_graph
            expect(dot).to(contain("digraph"))
            expect(dot).to(contain("StoryMap"))
            expect(len(graph.epics)).to(be_true)
            expect(dot.count("->") > 0).to(equal(True))

        with it("should include create-customer stories in the stories dot graph"):
            graph = PracticeGraph.load(_PML)
            dot = graph.stories_dot_graph.lower()
            expect("create-customer" in dot or "create_customer" in dot).to(equal(True))
