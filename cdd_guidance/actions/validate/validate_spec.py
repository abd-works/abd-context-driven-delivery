"""BDD spec — Validate action."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, expect
from mamba import before, context, description, it

from harness.agent_tools.agent_tools import AgentInstructions
from harness.guidance.fixtures.sample_tool.sample_tool_host import (
    SamplePracticeGuidance,
)
from validate.validate import Validate


def _expanded_validate(action, arguments):
    return AgentInstructions.for_callable(Validate.validate, action).expand(
        {}, arguments
    ).instructions


with description("a validate action on practice guidance") as self:
    with before.each:
        self.guidance = SamplePracticeGuidance(format="markdown")
        self.action = Validate()

    with context("with no rule passed"):
        with it("should document graph JSON in validate instructions"):
            prose = _expanded_validate(self.action, {"guidance": [self.guidance]})
            expect(prose).to(contain("graph_return_nodes"))

        with it("should return validate instructions for every rule in one shot"):
            report = self.action.validate(guidance=[self.guidance])
            expect(report).to(contain("sample-rule-one"))

    with context("with one rule passed"):
        with it("should return validate instructions for that rule only"):
            rule = self.guidance.rules.entries["sample-rule-one"]
            report = self.action.validate(guidance=[self.guidance], rule=rule)
            expect(report).to(contain("sample-rule-one"))

    with context("with a fidelity active"):
        with it("should pass that fidelity's rules with the shared rules"):
            guidance = SamplePracticeGuidance(format="markdown", fidelity="sketch")
            report = self.action.validate(guidance=[guidance])
            expect(report).to(contain("sample-rule-one"))
            expect(report).to(contain("sketch-rule"))
            expect(report).not_to(contain("spec-rule"))

    with context("with stories practice guidance"):
        with it("should load the shared rules collection from the whole practice slug"):
            report = self.action.validate(guidance=["stories"])
            expect(report).to(contain("vocabulary-traces-to-domain-source"))

        with it("should load shared and fidelity rules when the fidelity slug is scenarios"):
            report = self.action.validate(guidance=["scenarios"])
            expect(report).to(contain("vocabulary-traces-to-domain-source"))
            expect(report).to(contain("gwt-steps-trace-to-domain-operations"))

    with context("with ddd and stories guidance"):
        with it("should return shared and active-fidelity rules from each practice"):
            report = self.action.validate(guidance=["ddd", "stories"])
            expect(report).to(contain("ubiquitous-language-everywhere"))
            expect(report).to(contain("experts-words-preferred"))
            expect(report).to(contain("do-not-invent-requirements"))
            expect(report).to(contain("verb-noun-format"))

    with context("with graph JSON paths"):
        with it("should append a graph-rule report from summary JSON and still include AI rules"):
            fixture = Path(__file__).with_name("fixtures") / "sample-graph-violations.json"
            report = self.action.validate(
                guidance=[self.guidance],
                graph=str(fixture),
            )
            expect(report).to(contain("Graph rule validation"))
            expect(report).to(contain("limit-operation-parameters"))
            expect(report).to(contain("**[graph rule]**"))
            expect(report).to(contain("sample-rule-one"))
            expect(report).not_to(contain("vscode://"))
            expect(report).not_to(contain("file://"))
            expect(report).to(contain("#L10"))
            expect(report).to(contain("[src/example.ts]("))
            expect(report).not_to(contain("[src\\example.ts]"))

        with it("should return the graph-rule report when the MCP prompt expands validate"):
            fixture = Path(__file__).with_name("fixtures") / "sample-graph-violations.json"
            prose = _expanded_validate(
                self.action,
                {"guidance": [self.guidance], "graph": str(fixture)},
            )
            expect(prose).to(contain("limit-operation-parameters"))
            expect(prose).to(contain("[src/example.ts]("))
            expect(prose).to(contain("sample-rule-one"))

    with context("with the saved graph"):
        with before.each:
            self.folder = Path(__file__).with_name("fixtures") / "saved-graph"
            self.action._validate_workspace = lambda: self.folder
            self.action._session_path = lambda: None

        with it("should report the guidance practice's graph hits from graph.json when graph is true"):
            prose = _expanded_validate(self.action, {"guidance": ["ddd-tactics"], "graph": True})
            expect(prose).to(contain("load-with-identity-in-hand"))
            expect(prose).to(contain("[src/orders/order.ts]("))
            expect(prose).not_to(contain("sampleOp"))

        with it("should read a saved graph document passed as the graph path"):
            report = self.action.validate(
                guidance=["clean-engineering-code"],
                graph=str(self.folder / ".context" / "graph.json"),
            )
            expect(report).to(contain("sampleOp"))
            expect(report).not_to(contain("OrderRepository"))
