"""BDD spec for Node.rules violation access."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from practices.knowledge_graph.model import Kind, PracticeGraph
from practices.knowledge_graph.model.graph_rules import get_rule_registry
from practices.knowledge_graph.model.nodes import GraphExample, GraphScenario, GraphStep
from practices.stories.model.scenario import Phase
from practices.stories.model.source_location import SourceLocation

_SLICE = _REPO_ROOT / "practices" / "knowledge_graph" / "examples" / "codeql-slice"
_EXPORT = _SLICE / ".codeql" / "results" / "practice-graph.json"
_CATALOG = _REPO_ROOT / "practices" / "stories" / "catalog-examples"


with description("Rule registry"):
    with it("should load practice guidance rules from markdown"):
        registry = get_rule_registry()
        slugs = {r.slug for r in registry}
        expect("gwt-steps-trace-to-domain-operations" in slugs).to(equal(True))
        expect("verb-noun-format" in slugs).to(equal(True))


with description("Node.rules on PracticeGraph"):
    with it("should expose violations on scenario without examples"):
        graph = PracticeGraph(_SLICE)
        scenario = GraphScenario("Empty scenario", 1)
        graph.register(scenario)
        graph.evaluate_rules()
        slugs = {v.rule_slug for v in scenario.rules.direct.violations}
        expect("scenario-scopes-example" in slugs).to(equal(True))

    with it("should expose acceptance_tests violations filtered on step"):
        graph = PracticeGraph(_SLICE)
        step = GraphStep(
            text="loads customer",
            phase=Phase.WHEN,
            sequential_order=1,
            source=SourceLocation("story.test.ts", 10),
        )
        graph.register(step)
        graph.evaluate_rules()
        filtered = step.rules.practice("stories").fidelity("acceptance_tests").violations
        slugs = {v.rule_slug for v in filtered}
        expect("gwt-steps-trace-to-domain-operations" in slugs).to(equal(True))

    with it("should clear step invoke violation after CodeQL populate and evaluate"):
        from practices.knowledge_graph.model.codeql_populate import populate_from_codeql

        graph = PracticeGraph.load(_SLICE, codeql_results=_EXPORT)
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
        graph.evaluate_rules(codeql_results=_EXPORT)
        invokes = graph.outgoing_nodes(step, Kind.INVOKES)
        expect(len(invokes)).to(equal(1))
        slugs = {v.rule_slug for v in step.rules.direct.violations}
        expect("gwt-steps-trace-to-domain-operations" in slugs).to(equal(False))

    with it("should flag example without demonstrates edge"):
        graph = PracticeGraph(_SLICE)
        example = GraphExample("orphan example", 1, {}, scope="scenario")
        graph.register(example)
        graph.evaluate_rules()
        slugs = {v.rule_slug for v in example.rules.violations}
        expect("examples-trace-domain-model" in slugs).to(equal(True))

    with it("should evaluate rules on full catalog load"):
        graph = PracticeGraph.load(_CATALOG)
        steps = graph.nodes_of_type(GraphStep)
        expect(len(steps) > 0).to(equal(True))
        expect(len(graph.rule_registry.rules) > 0).to(equal(True))
