"""BDD development — GraphRulesCollection mixed bag and glob inject.

Hierarchy 1:1 with knowledge-graph-file-change-sketch.md
theme: bdd behavior / a repo … that is injecting on postToolUse
plus increment: it should use GraphRule when a .ql exists.
"""
from pathlib import Path
import sys
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[3]
_HARNESS = (_REPO_ROOT / "harness").resolve()
sys.path[:] = [
    item
    for item in sys.path
    if not item or Path(item).resolve() != _HARNESS
]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
import mcp.types  # SDK; harness/mcp must not shadow this
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, contain, equal, expect
from mamba import before, context, description, it

from practices.clean_engineering.clean_engineering import CleanEngineering
from harness.knowledge_graph.model.graph_rules import GraphRule, GraphRulesCollection, RuleRegistry


with description("a repo"):
    with context("that has been captured as a kg database"):
        with before.each:
            self.database = _REPO_ROOT / ".codeql" / "python-db"

        with context("with production code and story tests already defined"):
            with before.each:
                self.production = _REPO_ROOT / "harness" / "session" / "session.py"
                self.story_test = (
                    _REPO_ROOT
                    / "harness"
                    / "knowledge_graph"
                    / "app"
                    / "tests"
                    / "explore-knowledge-graph"
                    / "explore-practice-graphs"
                    / "explore-practice-graphs_e2e.spec.ts"
                )
                self.practice = CleanEngineering(fidelity="code")
                self.code_rules = self.practice.fidelities["code"].rules

            with it("should load practice rules as a GraphRulesCollection"):
                expect(self.practice.rules).to(be_a(GraphRulesCollection))
                expect(len(list(self.practice.rules)) > 0).to(equal(True))

            with it("should load fidelity rules as a GraphRulesCollection"):
                expect(self.code_rules).to(be_a(GraphRulesCollection))
                expect(len(list(self.code_rules)) > 0).to(equal(True))

            with it("should use GraphRule when a .ql exists"):
                expect(self.code_rules["keep-operations-small-focused"]).to(be_a(GraphRule))

            with it("should register those rules for graph nodes"):
                registry = RuleRegistry.load()
                slugs = {
                    rule.slug
                    for rule in registry.rules_for_node(
                        practice="clean_engineering",
                        semantic_type="Operation",
                    )
                }
                expect("keep-operations-small-focused" in slugs).to(equal(True))

            with context("that is injecting on postToolUse"):
                with before.each:
                    self.path = str(self.production)
                    self.payload = {
                        "hook_event_name": "postToolUse",
                        "tool_name": "Write",
                        "tool_input": {"path": self.path},
                        "workspace_roots": [str(_REPO_ROOT)],
                    }

                with it("should still match bags with AppliesTo.globs"):
                    expect(self.code_rules.matches(self.path)).to(equal(True))

                with it("should not use graph matching for inject yet"):
                    from harness.knowledge_graph.model.codeql import CodeQL

                    with patch.object(CodeQL, "populate") as populate:
                        self.practice.rules.inject_rules(self.payload)
                    expect(populate.call_count).to(equal(0))

                with it("should still return markdown additional_context from matches"):
                    result = self.practice.rules.inject_rules(self.payload)
                    expect(result.get("additional_context") or "").to(
                        contain("keep-operations-small-focused")
                    )

                with it("should not run graph-rule validate"):
                    with patch.object(GraphRule, "validate", return_value="ran") as validate:
                        self.practice.rules.inject_rules(self.payload)
                    expect(validate.call_count).to(equal(0))
