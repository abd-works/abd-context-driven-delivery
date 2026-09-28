"""BDD spec for CodeQL populate pass on PracticeGraph."""

import mcp.types  # SDK, before harness/mcp is on PYTHONPATH
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect, have_length
from mamba import description, it

from harness.knowledge_graph.model import CodeQL, Kind, PracticeGraph
from harness.knowledge_graph.model.nodes import GraphStep
from practices.clean_engineering.model.codeql.codeql_model import (
    CleanEngineeringModel,
    GraphMemberRows,
    Operation,
)
from practices.stories.model.codeql.codeql_model import Example, Step
from practices.stories.model.scenario import Phase
from practices.stories.model.source_location import SourceLocation

_SLICE = _REPO_ROOT / "harness" / "knowledge_graph" / "examples" / "codeql-slice"
_EXPORT = _SLICE / ".codeql" / "results" / "practice-graph.json"


with description("CodeQL practice-graph export"):
    with it("should parse the fixture JSON schema"):
        import json

        export = json.loads(_EXPORT.read_text(encoding="utf-8"))
        expect(export.get("version")).to(equal(1))
        expect(export.get("classes")).to(have_length(4))
        expect(export.get("story_calls")).to(have_length(1))


with description("CodeQL populate on PracticeGraph"):
    with it("should create CE nodes and operation invokes edges from export"):
        graph = PracticeGraph(_SLICE)
        CodeQL(_SLICE).populate(graph, results_path=_EXPORT)
        load_op = graph.operation_named("CustomerRepository", "load")
        expect(load_op is not None).to(equal(True))
        invokes = [r for r in graph.relationships if r.kind == Kind.INVOKES]
        expect(len(invokes) >= 1).to(equal(True))
        fetch = graph.operation_named("IMavenirClient", "fetchCustomer")
        expect(fetch in load_op.invoked_operations()).to(equal(True))
        expect(load_op in fetch.called_by).to(equal(True))

    with it("should wire step invokes operation when story source lines match"):
        graph = PracticeGraph(_SLICE)
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
        load_op = graph.operation_named("CustomerRepository", "load")
        expect(isinstance(load_op, Operation)).to(equal(True))
        targets = step.related(Kind.INVOKES)
        expect(any(t is load_op for t in targets)).to(equal(True))

    with it("should wire example demonstrates class from example_exports"):
        graph = PracticeGraph(_SLICE)
        example = Example("stored customer", 1, {"identity": "valid"}, scope="scenario")
        graph.register(example)
        CodeQL(_SLICE).populate(graph, results_path=_EXPORT)
        customer = graph.class_named("Customer")
        expect(customer is not None).to(equal(True))
        demos = example.related(Kind.DEMONSTRATES)
        expect(any(d is customer for d in demos)).to(equal(True))

    with it("should not treat another class __init__ as a dependency of this __init__"):
        graph = PracticeGraph(_SLICE)
        rows = GraphMemberRows(
            [
                {"name": "CreateAgentToolset", "module": "builders.create_agent_toolset"},
                {"name": "Ddd", "module": "practices.ddd"},
            ],
            [],
        )
        rows.operations = [
            {"class_name": "CreateAgentToolset", "name": "__init__"},
            {"class_name": "Ddd", "name": "__init__"},
        ]
        model = CleanEngineeringModel("CleanEngineering", 1)
        model.ensure(graph, rows)
        model.wire_calls(
            graph,
            [
                {
                    "caller_class": "CreateAgentToolset",
                    "caller_operation": "__init__",
                    "callee_class": "Ddd",
                    "callee_operation": "__init__",
                }
            ],
        )
        toolset = graph.operation_named("CreateAgentToolset", "__init__")
        ddd_init = graph.operation_named("Ddd", "__init__")
        expect(ddd_init in toolset.invoked_operations()).to(equal(False))
        modules = [
            edge
            for edge in graph.relationships
            if edge.kind == Kind.DEPENDS_ON
        ]
        expect(modules).to(equal([]))
        graph = PracticeGraph(_SLICE)
        rows = GraphMemberRows(
            [
                {
                    "name": "CustomerRepository",
                    "module": "Customer",
                    "file": "domain/customer/Customer.ts",
                    "line": 120,
                    "end_line": 160,
                }
            ],
            [],
        )
        rows.operations = [
            {
                "class_name": "CustomerRepository",
                "name": "load",
                "return_type": "Customer",
                "file": "domain/customer/Customer.ts",
                "line": 130,
                "end_line": 138,
                "text": "load(customerId: string): Customer {",
            }
        ]
        CleanEngineeringModel("CleanEngineering", 1).ensure(graph, rows)
        load_op = graph.operation_named("CustomerRepository", "load")
        expect(load_op.source.file).to(equal("domain/customer/Customer.ts"))
        expect(load_op.source.line).to(equal(130))
        expect(load_op.source.end_line).to(equal(138))
        expect("load(" in load_op.source.text).to(equal(True))
        from harness.knowledge_graph.write_practice_hierarchy import explorer_dto

        payload = explorer_dto(graph, _SLICE)
        listed = [
            node
            for group in payload["practice_graphs"]
            for node in group["nodes"]
            if node["name"] == "load"
        ]
        expect(listed[0]["source"]["file"]).to(equal("domain/customer/Customer.ts"))
        expect(listed[0]["source"]["start_line"]).to(equal(130))
        expect("load(" in listed[0]["source"]["text"]).to(equal(True))

    with it("should parent module-level operations on the file"):
        graph = PracticeGraph(_SLICE)
        rows = GraphMemberRows([], [])
        rows.operations = [
            {
                "class_name": "harness/knowledge_graph/model/dot_graph.py",
                "name": "walk_hierarchy",
                "return_type": "",
                "file": "harness/knowledge_graph/model/dot_graph.py",
                "line": 45,
                "end_line": 72,
            }
        ]
        CleanEngineeringModel("CleanEngineering", 1).ensure(graph, rows)
        walk = graph.operation_named(
            "harness/knowledge_graph/model/dot_graph.py",
            "walk_hierarchy",
        )
        expect(walk is not None).to(equal(True))
        owner = next(iter(walk.related(Kind.BELONGS_TO)), None)
        expect(owner.semantic_type()).to(equal("File"))
        expect(owner.name).to(equal("harness/knowledge_graph/model/dot_graph.py"))

    with it("should load catalog stories and merge CodeQL when export is present"):
        catalog = _REPO_ROOT / "practices" / "stories" / "catalog-examples"
        graph = PracticeGraph.load(catalog, codeql_results=_EXPORT)
        expect(graph.operation_named("CustomerRepository", "load") is not None).to(equal(True))
        expect(len(graph.nodes_of_type(GraphStep)) > 0).to(equal(True))
