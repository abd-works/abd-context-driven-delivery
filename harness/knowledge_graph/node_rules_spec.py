"""BDD spec for Node.rules violation access."""

import sys
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from harness.knowledge_graph.model import CodeQL, Kind, PracticeGraph
from harness.knowledge_graph.model.graph_rules import RuleRegistry
from practices.clean_engineering.model.codeql.codeql_model import OoadClass, Operation
from practices.stories.model.codeql.codeql_model import Example, Scenario, Step
from practices.stories.model.scenario import Phase
from practices.stories.model.source_location import SourceLocation

_SLICE = _REPO_ROOT / "harness" / "knowledge_graph" / "examples" / "codeql-slice"
_EXPORT = _SLICE / ".codeql" / "results" / "practice-graph.json"
_CATALOG = _REPO_ROOT / "practices" / "stories" / "catalog-examples"


with description("Rule registry"):
    with it("should load practice guidance rules from markdown"):
        registry = RuleRegistry.load()
        slugs = {r.slug for r in registry}
        expect("gwt-steps-trace-to-domain-operations" in slugs).to(equal(True))
        expect("verb-noun-format" in slugs).to(equal(True))


with description("Node.rules on PracticeGraph"):
    with it("should expose violations on scenario without examples"):
        graph = PracticeGraph(_SLICE)
        scenario = Scenario("Empty scenario", 1)
        graph.register(scenario)
        graph.evaluate_rules()
        slugs = {v.rule_slug for v in scenario.rules.direct.violations}
        expect("scenario-scopes-example" in slugs).to(equal(True))

    with it("should expose acceptance_tests violations filtered on step"):
        graph = PracticeGraph(_SLICE)
        step = Step(
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
        graph = PracticeGraph.load(_SLICE, codeql_results=_EXPORT)
        step = Step(
            text="My Paradise loads the customer from Mavenir",
            phase=Phase.WHEN,
            sequential_order=1,
            source=SourceLocation(
                "stories/onboard-a-customer/create-customer/load-customer/load_customer_story.test.ts",
                24,
            ),
        )
        graph.register(step)
        CodeQL(_SLICE).populate(graph, results_path=_EXPORT)
        graph.evaluate_rules(codeql_results=_EXPORT)
        invokes = step.related(Kind.INVOKES)
        expect(len(invokes)).to(equal(1))
        slugs = {v.rule_slug for v in step.rules.direct.violations}
        expect("gwt-steps-trace-to-domain-operations" in slugs).to(equal(False))

    with it("should flag example without demonstrates edge"):
        graph = PracticeGraph(_SLICE)
        example = Example("orphan example", 1, {}, scope="scenario")
        graph.register(example)
        graph.evaluate_rules()
        slugs = {v.rule_slug for v in example.rules.violations}
        expect("examples-trace-domain-model" in slugs).to(equal(True))

    with it("should flag a class with more than ten public operations"):
        graph = PracticeGraph(_SLICE)
        busy = OoadClass("Busy", 1)
        graph.register(busy)
        for index in range(11):
            operation = Operation(f"act{index}", index + 1)
            graph.register(operation)
            busy.relate(Kind.OWNS, operation)
        rows = [
            {
                "name": "Busy",
                "message": "Class 'Busy' has 11 public methods.",
                "contributor": f"act{index}",
            }
            for index in range(11)
        ]
        with patch(
            "harness.knowledge_graph.model.codeql.CodeQL.run",
            return_value=rows,
        ):
            graph.evaluate_rules()
        hits = busy.rules.slug("keep-classes-single-responsibility").violations
        expect(len(hits)).to(equal(1))
        expect(hits[0].node_id).to(equal(busy.node_id))
        expect(len(hits[0].contributors)).to(equal(11))
        expect(hits[0].rule_slug).to(equal("keep-classes-single-responsibility"))

    with it("should not flag a class with ten public operations"):
        graph = PracticeGraph(_SLICE)
        lean = OoadClass("Lean", 1)
        graph.register(lean)
        for index in range(10):
            operation = Operation(f"act{index}", index + 1)
            graph.register(operation)
            lean.relate(Kind.OWNS, operation)
        graph.evaluate_rules()
        expect(len(lean.rules.slug("keep-classes-single-responsibility").violations)).to(
            equal(0)
        )

    with it("should return no class-responsibility hits on a step"):
        graph = PracticeGraph(_SLICE)
        step = Step(
            text="loads customer",
            phase=Phase.WHEN,
            sequential_order=1,
            source=SourceLocation("story.test.ts", 10),
        )
        graph.register(step)
        graph.evaluate_rules()
        expect(len(step.rules.slug("keep-classes-single-responsibility").violations)).to(
            equal(0)
        )

    with it("should point keep-classes-single-responsibility at its graphQuery file"):
        registry = RuleRegistry.load()
        rule = next(r for r in registry if r.slug == "keep-classes-single-responsibility")
        expect(rule.graphQuery is not None).to(equal(True))
        expect(rule.graphQuery.name).to(equal("keep-classes-single-responsibility.ql"))
        expect("publicCount > 10" in rule.load_graph_query()).to(equal(True))

    with it("should evaluate rules on full catalog load"):
        graph = PracticeGraph.load(_CATALOG)
        steps = graph.nodes_of_type(Step)
        expect(len(steps) > 0).to(equal(True))
        expect(len(graph.rule_registry.rules) > 0).to(equal(True))
