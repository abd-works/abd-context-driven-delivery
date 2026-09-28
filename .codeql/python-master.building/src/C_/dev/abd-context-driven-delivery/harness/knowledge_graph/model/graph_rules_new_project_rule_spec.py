"""BDD spec — GraphRulesCollection.new_project_rule placement instructions."""

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
from mamba import description, it

from harness.knowledge_graph.model.graph_rules import GraphRulesCollection


with description("GraphRulesCollection.new_project_rule"):
    with it("should be marked for mcp skill and agent instructions"):
        fn = GraphRulesCollection.new_project_rule
        expect(getattr(fn, "_mcp", False)).to(equal(True))
        expect(getattr(fn, "_skill", False)).to(equal(True))
        expect(getattr(fn, "_is_agent_instructions", False)).to(equal(True))
        expect(getattr(fn, "_is_agent_tool", False)).to(equal(False))

    with it("should make the correction and then codify a rule"):
        doc = GraphRulesCollection.new_project_rule.__doc__
        expect(doc).to(contain("background subagent"))
        expect(doc).to(contain("do not wait for the subagent"))
        expect(doc).to(contain("run_in_background true"))
        expect(doc).to(contain("Make the correction, then codify it as a project rule"))
        expect(doc).to(contain("correction is the fix to make there"))
        expect(doc).to(contain("write the rule and its CodeQL query"))
        text = GraphRulesCollection().new_project_rule(
            "Customer",
            "Put state-changing behaviour on the aggregate",
            r"C:\dev\paradise-mobile\pml-web",
            "Entity",
        )
        expect(text).to(contain("You are the background subagent"))
        expect(text).to(contain("Do not launch another subagent."))
        expect(text).to(contain("Make the correction on the subject first."))
        expect(text).to(contain("The correction is the fix."))

    with it("should tell the agent where to write the rule files"):
        text = GraphRulesCollection().new_project_rule(
            "Customer",
            "Put state-changing behaviour on the aggregate",
            r"C:\dev\paradise-mobile\pml-web",
            "Entity",
        )
        expect(text).to(contain(r"Project folder: C:\dev\paradise-mobile\pml-web"))
        expect(text).to(contain("Subject: Customer"))
        expect(text).to(contain("Put state-changing behaviour on the aggregate"))
        expect(text).to(
            contain(
                r"C:\dev\paradise-mobile\pml-web/.context/rules/{practice}/{fidelity}/rules.md"
            )
        )
        expect(text).to(
            contain(
                r"C:\dev\paradise-mobile\pml-web/.context/rules/{practice}/{fidelity}/codeql/{slug}.ql"
            )
        )
        expect(text).to(contain("import javascript"))
