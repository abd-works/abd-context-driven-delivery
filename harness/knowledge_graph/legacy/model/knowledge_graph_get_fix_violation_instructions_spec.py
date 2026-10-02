"""BDD spec — KnowledgeGraph.get_fix_violation_instructions copy-to-prompt instructions."""

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


with description("KnowledgeGraph.get_fix_violation_instructions"):
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
        fn = KnowledgeGraph.get_fix_violation_instructions
        expect(getattr(fn, "_mcp", False)).to(equal(True))
        expect(getattr(fn, "_skill", False)).to(equal(True))
        expect(getattr(fn, "_is_agent_instructions", False)).to(equal(True))
        expect(getattr(fn, "_is_agent_tool", False)).to(equal(False))

    with it("should say it does not fix anything"):
        expect(KnowledgeGraph.get_fix_violation_instructions.__doc__).to(
            contain("does not fix anything")
        )

    with it("should say not to call it when the violations are already in hand"):
        expect(KnowledgeGraph.get_fix_violation_instructions.__doc__).to(
            contain("If you already have the violations, do not call this method")
        )

    with it("should return copy-to-prompt text for a node and its violating children"):
        text = self.kg.get_fix_violation_instructions("CodeQL")
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
        text = self.kg.get_fix_violation_instructions(
            {"path": "CodeQL", "rule": "keep-operations-small-focused"}
        )
        expect(text).to(contain("keep-operations-small-focused"))
        expect(text).not_to(contain("keep-classes-single-responsibility"))
        expect(text).not_to(contain("keep-operations-single-responsibility"))

    with it("should keep only the named node type under the node"):
        text = self.kg.get_fix_violation_instructions(
            {"path": "CodeQL", "semantic_type": "Operation"}
        )
        expect(text).to(contain("ensure_database"))
        expect(text).not_to(contain("keep-classes-single-responsibility"))

    with it("should return no instruction when nothing in the subtree violates"):
        text = self.kg.get_fix_violation_instructions("CodeQL.populate")
        expect(text).to(equal(""))

    with it("should tell the agent to complete each violation as a task"):
        text = self.kg.get_fix_violation_instructions("CodeQL")
        expect(text).to(contain("Fix the following violations, follow this process"))
        expect(text).to(contain("save the below as a violation task list"))
        expect(text).to(contain("use a non-blocking sub agent if available to you"))
        expect(text).to(contain("fix each violation as a separate turn"))
        expect(text).to(contain("ignore violations that are marked as fixed"))
        expect(text).to(contain("[ ] done"))
