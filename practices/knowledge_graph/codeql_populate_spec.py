"""BDD spec for CodeQL populate pass on PracticeGraph."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect, have_length
from mamba import description, it

from practices.knowledge_graph.model import Kind, PracticeGraph
from practices.knowledge_graph.model.codeql_export import load_codeql_export
from practices.knowledge_graph.model.codeql_populate import populate_from_codeql
from practices.knowledge_graph.model.nodes import GraphExample, GraphOperation, GraphStep
from practices.stories.model.scenario import Phase
from practices.stories.model.source_location import SourceLocation

_SLICE = _REPO_ROOT / "practices" / "knowledge_graph" / "examples" / "codeql-slice"
_EXPORT = _SLICE / ".codeql" / "results" / "practice-graph.json"


with description("CodeQL practice-graph export"):
    with it("should parse the fixture JSON schema"):
        export = load_codeql_export(_EXPORT)
        expect(export.version).to(equal(1))
        expect(export.classes).to(have_length(3))
        expect(export.story_calls).to(have_length(1))


with description("CodeQL populate on PracticeGraph"):
    with it("should create CE nodes and operation invokes edges from export"):
        graph = PracticeGraph(_SLICE)
        applied = populate_from_codeql(graph, _SLICE, results_path=_EXPORT)
        expect(applied).to(equal(True))
        load_op = graph.find_operation("CustomerRepository", "load")
        expect(load_op is not None).to(equal(True))
        invokes = [r for r in graph.relationships if r.kind == Kind.INVOKES]
        expect(len(invokes)).to(equal(1))

    with it("should wire step invokes operation when story source lines match"):
        graph = PracticeGraph(_SLICE)
        step = GraphStep(
            text="My Paradise loads the customer from Mavenir",
            phase=Phase.WHEN,
            sequential_order=1,
            source=SourceLocation(
                "stories/onboard-a-customer/create-customer/load-customer/load_customer_story.test.ts",
                24,
            ),
        )
        graph.register(step)
        populate_from_codeql(graph, _SLICE, results_path=_EXPORT)
        load_op = graph.find_operation("CustomerRepository", "load")
        expect(isinstance(load_op, GraphOperation)).to(equal(True))
        targets = graph.outgoing_nodes(step, Kind.INVOKES)
        expect(any(t is load_op for t in targets)).to(equal(True))

    with it("should wire example demonstrates class from example_exports"):
        graph = PracticeGraph(_SLICE)
        example = GraphExample("stored customer", 1, {"identity": "valid"}, scope="scenario")
        graph.register(example)
        populate_from_codeql(graph, _SLICE, results_path=_EXPORT)
        customer = graph.find_class("Customer")
        expect(customer is not None).to(equal(True))
        demos = graph.outgoing_nodes(example, Kind.DEMONSTRATES)
        expect(any(d is customer for d in demos)).to(equal(True))

    with it("should load catalog stories and merge CodeQL when export is present"):
        catalog = _REPO_ROOT / "practices" / "stories" / "catalog-examples"
        graph = PracticeGraph.load(catalog, codeql_results=_EXPORT)
        expect(graph.find_operation("CustomerRepository", "load") is not None).to(equal(True))
        expect(len(graph.nodes_of_type(GraphStep)) > 0).to(equal(True))
