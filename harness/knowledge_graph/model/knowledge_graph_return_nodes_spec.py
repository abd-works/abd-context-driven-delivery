"""BDD spec — KnowledgeGraph.return_nodes dotted filter as JSON MCP tool."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import json

from expects import equal, expect
from mamba import before, description, it

from harness.knowledge_graph.model.graph_node import Kind, Node, Relationship
from harness.knowledge_graph.model.knowledge_graph import KnowledgeGraph
from harness.knowledge_graph.model.practice_graph import PracticeGraph
from practices.stories.model.source_location import SourceLocation


class NamedNode(Node):
    def __init__(self, name: str, kind: str) -> None:
        self.name = name
        self.practice = "clean_engineering"
        self._kind = kind

    def semantic_type(self) -> str:
        return self._kind


class Hit:
    def __init__(self, slug: str, message: str) -> None:
        self.rule_slug = slug
        self.message = message
        self.practice = "clean_engineering"
        self.fidelity = "code"


class _EmptyRegistry:
    rules = []


with description("KnowledgeGraph.return_nodes"):
    with before.each:
        graph = PracticeGraph(_REPO_ROOT, rule_registry=_EmptyRegistry())
        owner = NamedNode("CodeQL", "OoadClass")
        op = NamedNode("ensure_database", "Operation")
        other = NamedNode("populate", "Operation")
        graph.register(owner)
        graph.register(op)
        graph.register(other)
        graph.relate(Relationship(Kind.OWNS, owner, op))
        graph.relate(Relationship(Kind.OWNS, owner, other))
        op.source = SourceLocation(file="model/codeql.py", line=176, end_line=200, text="def ensure_database")
        graph._violations_by_node[op.node_id] = [
            Hit(
                "keep-operations-small-focused",
                "Operation 'ensure_database' is 25 lines (max 20).",
            )
        ]
        self.kg = KnowledgeGraph(practice_graphs=[graph], root=_REPO_ROOT)
        self.op = op

    with it("should be marked for mcp skill and agent tool"):
        fn = KnowledgeGraph.return_nodes
        expect(getattr(fn, "_mcp", False)).to(equal(True))
        expect(getattr(fn, "_skill", False)).to(equal(True))
        expect(getattr(fn, "_is_agent_tool", False)).to(equal(True))
        expect(getattr(KnowledgeGraph, "_is_agent_toolset", False)).to(equal(True))

    with it("should advertise filter as a JSON object on MCP"):
        from harness.mcp.mcp_server import McpHost

        schema = McpHost.input_schema_for_callable(KnowledgeGraph.return_nodes)
        filt = schema["properties"]["filter"]
        types = [filt.get("type")] + [item.get("type") for item in filt.get("anyOf") or []]
        expect("object" in types).to(equal(True))
        expect("string" in types).to(equal(False))

    with it("should return the operation as json for a dotted Class.operation path"):
        payload = json.loads(self.kg.return_nodes("CodeQL.ensure_database"))
        names = {item["name"]: item for item in payload}
        expect("ensure_database" in names).to(equal(True))
        expect("CodeQL" in names).to(equal(True))
        expect("populate" in names).to(equal(False))
        expect(names["ensure_database"]["seed"]).to(equal(True))
        expect(names["CodeQL"]["seed"]).to(equal(False))
        expect(names["ensure_database"]["violations"][0]["rule_slug"]).to(
            equal("keep-operations-small-focused")
        )

    with it("should filter violations-only dict accessors"):
        payload = json.loads(self.kg.return_nodes({"violations": True}))
        names = {item["name"] for item in payload}
        expect("ensure_database" in names).to(equal(True))
        expect("CodeQL" in names).to(equal(True))
        expect("populate" in names).to(equal(False))

    with it("should keep children of a type filter"):
        payload = json.loads(self.kg.return_nodes({"semantic_types": ["OoadClass"]}))
        names = {item["name"] for item in payload}
        expect("CodeQL" in names).to(equal(True))
        expect("ensure_database" in names).to(equal(True))
        expect("populate" in names).to(equal(True))

    with it("should keep nodes related to another node"):
        payload = json.loads(
            self.kg.return_nodes({"related_to": {"name": "CodeQL", "kind": "owns"}})
        )
        names = {item["name"] for item in payload}
        expect("ensure_database" in names).to(equal(True))
        expect("populate" in names).to(equal(True))
        expect("CodeQL" in names).to(equal(True))
