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

from expects import contain, equal, expect
from mamba import description, it

from harness.knowledge_graph.model import Kind, Node, PracticeGraph
from practices.stories.model.codeql.stories import Epic, Example, Step

_CATALOG = _REPO_ROOT / "practices" / "stories" / "catalog-examples"
_PML = Path(os.environ.get("PML_DOMAINMODEL", r"C:\dev\paradise-mobile\pml-domainmodel"))


with description("PracticeGraph dot_graph"):
    with it("should expose a DOT digraph from the stories root"):
        graph = PracticeGraph.load(_CATALOG)
        expect(graph.story_map is not None).to(equal(True))
        dot = graph.story_map.dot_graph
        expect(dot).to(contain("digraph"))
        expect(dot).to(contain("StoryMap"))
        expect(dot).to(contain("Epic"))
        expect(dot).to(contain("onboard-a-customer"))
        expect(dot).to(contain(f'[label="{Kind.OWNS}"]'))

    with it("should include owned descendants on any graph node"):
        graph = PracticeGraph.load(_CATALOG)
        epic = next(
            node
            for node in graph.nodes_of_type(Epic)
            if Node.slug(node.name) == "onboard-a-customer"
        )
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
            expect(graph.story_map is not None).to(equal(True))
            dot = graph.story_map.dot_graph
            expect(dot).to(contain("digraph"))
            expect(dot).to(contain("StoryMap"))
            expect(len(graph.nodes_of_type(Epic)) > 0).to(equal(True))
            expect(dot.count("->") > 0).to(equal(True))

        with it("should include create-customer stories in the stories dot graph"):
            graph = PracticeGraph.load(_PML)
            dot = graph.story_map.dot_graph.lower()
            expect("create-customer" in dot or "create_customer" in dot).to(equal(True))

        with it("should print the complete story graph hierarchy"):
            graph = PracticeGraph.load(_PML)
            text = graph.story_map.hierarchy_text
            print(text)
            expect(text).to(contain("StoryMap"))
            expect(text).to(contain("Onboard A Customer"))
            expect(text).to(contain("Create Customer"))
            expect(text).to(contain("Load Customer"))
            expect(any(depth == 0 for depth, _ in graph.story_map.hierarchy)).to(equal(True))
            expect(len(graph.story_map.hierarchy) > 1).to(equal(True))

        with it("should label steps with Given When Then And or But"):
            graph = PracticeGraph.load(_PML)
            keywords = {step.keyword for step in graph.nodes_of_type(Step)}
            expect("Given" in keywords).to(equal(True))
            expect("When" in keywords).to(equal(True))
            expect("Then" in keywords).to(equal(True))
            expect("And" in keywords).to(equal(True))
            expect("But" in keywords).to(equal(True))
            text = graph.story_map.hierarchy_text
            expect(text).to(contain("Step: Given"))
            expect(text).to(contain("Step: When"))
            expect(text).to(contain("Step: Then"))
            expect(text).to(contain("Step: And"))
            expect(text).to(contain("Step: But"))

        with it("should include story examples in the hierarchy"):
            graph = PracticeGraph.load(_PML)
            examples = graph.nodes_of_type(Example)
            expect(len(examples) > 0).to(equal(True))
            text = graph.story_map.hierarchy_text
            expect(text).to(contain("Example:"))
