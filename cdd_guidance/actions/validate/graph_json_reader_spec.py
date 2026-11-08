"""BDD spec — graph JSON violation reader."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.actions.validate.checked_graph import CheckedGraph
from cdd_guidance.actions.validate.graph_json_reader import violations_from_graph_json_files
from cdd_guidance.actions.validate.report_files import ReportFiles
from harness.agent_tools.tool_call import ToolCall
from space.session.throwaway_project import ThrowawayProject

_SAVED_GRAPH = Path(__file__).with_name("fixtures") / "saved-graph" / ".context" / "graph.json"


with description("graph JSON reader"):
    with context("a saved graph document"):
        with it("should read every practice's violations"):
            violations = violations_from_graph_json_files([_SAVED_GRAPH])
            expect([violation.rule for violation in violations]).to(
                equal(["limit-operation-parameters", "load-with-identity-in-hand"])
            )

        with it("should place each violation at its node's file"):
            violations = violations_from_graph_json_files([_SAVED_GRAPH])
            expect(violations[1].location).to(equal("src/orders/order.ts"))

        with it("should name the practice that found each violation"):
            violations = violations_from_graph_json_files([_SAVED_GRAPH])
            expect(violations[1].practice).to(equal("ddd"))

        with it("should keep only the practices asked for"):
            violations = violations_from_graph_json_files([_SAVED_GRAPH], practices=["ddd"])
            expect([violation.rule for violation in violations]).to(equal(["load-with-identity-in-hand"]))


with description("a validate call's checked graph"):
    with context("that was named several graph files and is kept beside a report"):
        with before.each:
            self.throwaway = ThrowawayProject()
            session = ToolCall(project=self.throwaway.root).session
            graph = CheckedGraph(session, [], None, [str(_SAVED_GRAPH), str(_SAVED_GRAPH)])
            graph.check_beside(ReportFiles(session, []))
            self.saved = self.throwaway.root / "report.json"
            graph.save_at(self.saved)

        with after.each:
            self.throwaway.close()

        with it("should keep every hit of every graph"):
            expect(len(violations_from_graph_json_files([self.saved]))).to(equal(4))

        with it("should keep each hit's message"):
            messages = [violation.described for violation in violations_from_graph_json_files([self.saved])]
            expect(messages[:2]).to(equal([violation.described for violation in violations_from_graph_json_files([_SAVED_GRAPH])]))


    # One object answers for the saved graph file: the session's graph, which saves it and reads it back.
    with context("that checks the session's saved graph"):
        with before.each:
            self.throwaway = ThrowawayProject()
            session = ToolCall(project=self.throwaway.root).session
            self.saved = session.graph.saved_file.path
            self.saved.parent.mkdir(parents=True, exist_ok=True)
            self.saved.write_bytes(_SAVED_GRAPH.read_bytes())
            self.graph = CheckedGraph(session, [], None, True)
            self.files = self.graph.check_beside(ReportFiles(session, []))

        with after.each:
            self.throwaway.close()

        with it("should read the file the session's graph saves in"):
            expect(self.files).to(equal([self.saved]))

        with it("should report the violations that file holds"):
            expect([violation.rule for violation in self.graph.violations()]).to(
                equal(["limit-operation-parameters", "load-with-identity-in-hand"])
            )
