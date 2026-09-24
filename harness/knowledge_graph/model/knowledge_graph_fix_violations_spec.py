"""BDD spec — KnowledgeGraph.fix_violations copy-to-prompt instructions."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
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


with description("KnowledgeGraph.fix_violations"):
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
        op.source = SourceLocation(
            file="model/codeql.py", line=176, end_line=200, text="def ensure_database"
        )
        graph._violations_by_node[owner.node_id] = [
            Hit(
                "keep-classes-single-responsibility",
                "5 public operations",
            )
        ]
        graph._violations_by_node[op.node_id] = [
            Hit(
                "keep-operations-small-focused",
                "Operation 'ensure_database' is 25 lines (max 20).",
            ),
            Hit(
                "keep-operations-single-responsibility",
                "Operation 'ensure_database' does two jobs.",
            ),
        ]
        self.kg = KnowledgeGraph(practice_graphs=[graph], root=_REPO_ROOT)
        self.op = op

    with it("should be marked for mcp skill and agent instructions"):
        fn = KnowledgeGraph.fix_violations
        expect(getattr(fn, "_mcp", False)).to(equal(True))
        expect(getattr(fn, "_skill", False)).to(equal(True))
        expect(getattr(fn, "_is_agent_instructions", False)).to(equal(True))
        expect(getattr(fn, "_is_agent_tool", False)).to(equal(False))

    with it("should return copy-to-prompt text for a node and its violating children"):
        text = self.kg.fix_violations("CodeQL")
        expect(text).to(contain("keep-classes-single-responsibility"))
        expect(text).to(contain("keep-operations-small-focused"))
        expect(text).to(contain("Node: CodeQL.ensure_database (Operation)"))
        expect(text).to(contain("File: model/codeql.py:176-200"))
        expect(text).to(contain("Practice: clean_engineering"))
        expect(text).to(contain("Fidelity: code"))
        expect(text).to(contain("5 public operations"))
        expect(text).not_to(contain("populate"))
        expect(text).not_to(contain("def ensure_database"))

    with it("should keep only the named rule under the node"):
        text = self.kg.fix_violations(
            {"path": "CodeQL", "rule": "keep-operations-small-focused"}
        )
        expect(text).to(contain("keep-operations-small-focused"))
        expect(text).not_to(contain("keep-classes-single-responsibility"))
        expect(text).not_to(contain("keep-operations-single-responsibility"))

    with it("should keep only the named node type under the node"):
        text = self.kg.fix_violations(
            {"path": "CodeQL", "semantic_type": "Operation"}
        )
        expect(text).to(contain("ensure_database"))
        expect(text).not_to(contain("keep-classes-single-responsibility"))

    with it("should return no instruction when nothing in the subtree violates"):
        text = self.kg.fix_violations("CodeQL.populate")
        expect(text).to(equal(""))
