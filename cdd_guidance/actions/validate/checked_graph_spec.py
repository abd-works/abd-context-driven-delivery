"""BDD spec — the graph a validate call checks: built from its files, the session's saved graph, or the graph files it
names, each read through the one reader of graph files, SavedGraph.from_file."""

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

from cdd_guidance.actions.validate.checked_graph import CheckedGraph, NamedToCheck
from cdd_guidance.actions.validate.report_files import ReportFiles
from harness.agent_tools.tool_call import ToolCall
from harness.graph.saved_graph import SavedGraph
from space.session.throwaway_project import ThrowawayProject

_FIXTURES = Path(__file__).with_name("fixtures")
_SAVED_GRAPH = _FIXTURES / "saved-graph" / ".context" / "graph.json"
_NODE_LIST = _FIXTURES / "sample-graph-violations.json"


def _checked(named):
    """A validate call's checked graph for the graph files named, in a throwaway project, and the project."""
    throwaway = ThrowawayProject()
    session = ToolCall(project=throwaway.root).session
    graph = CheckedGraph(session, [], NamedToCheck(graph=named))
    graph.check_beside(ReportFiles(session, []))
    return graph, throwaway


with description("a validate call's checked graph"):
    with context("that was named a saved graph document"):
        with before.each:
            self.graph, self.throwaway = _checked(str(_SAVED_GRAPH))
            self.violations = self.graph.violations()

        with after.each:
            self.throwaway.close()

        with it("should read every practice's violations"):
            expect([violation.rule for violation in self.violations]).to(
                equal(["limit-operation-parameters", "load-with-identity-in-hand"])
            )

        with it("should place each violation at its node's file"):
            expect(self.violations[1].location).to(equal("src/orders/order.ts"))

        with it("should name the practice that found each violation"):
            expect(self.violations[1].practice).to(equal("ddd"))

    with context("that was named the node list graph.return_nodes answers with"):
        with before.each:
            self.graph, self.throwaway = _checked(str(_NODE_LIST))
            self.violations = self.graph.violations()

        with after.each:
            self.throwaway.close()

        with it("should read the violation on each violating rule"):
            expect([violation.rule for violation in self.violations]).to(equal(["limit-operation-parameters"]))

        with it("should name the practice of the node each violation was found on"):
            expect(self.violations[0].practice).to(equal("clean_engineering"))

    with context("that was named several graph files and is kept beside a report"):
        with before.each:
            self.graph, self.throwaway = _checked([str(_SAVED_GRAPH), str(_SAVED_GRAPH), str(_NODE_LIST)])
            self.saved = self.throwaway.root / "report.json"
            self.graph.save_at(self.saved)

        with after.each:
            self.throwaway.close()

        with it("should keep every hit of every graph"):
            expect(len(SavedGraph.from_file(self.saved).violations())).to(equal(5))

        with it("should keep each hit's message"):
            messages = sorted({violation.described for violation in SavedGraph.from_file(self.saved).violations()})
            named = [*SavedGraph.from_file(_SAVED_GRAPH).violations(), *SavedGraph.from_file(_NODE_LIST).violations()]
            expect(messages).to(equal(sorted({violation.described for violation in named})))

        with it("should keep only the practices asked for, as the board's report reads them"):
            rules = {violation.rule for violation in SavedGraph.from_file(self.saved).violations(["ddd"])}
            expect(rules).to(equal({"load-with-identity-in-hand"}))

    # One object answers for the saved graph file: the session's graph, which saves it and reads it back.
    with context("that checks the session's saved graph"):
        with before.each:
            self.throwaway = ThrowawayProject()
            session = ToolCall(project=self.throwaway.root).session
            self.saved = session.graph.saved_file.path
            self.saved.parent.mkdir(parents=True, exist_ok=True)
            self.saved.write_bytes(_SAVED_GRAPH.read_bytes())
            self.graph = CheckedGraph(session, [], NamedToCheck(graph=True))
            self.files = self.graph.check_beside(ReportFiles(session, []))

        with after.each:
            self.throwaway.close()

        with it("should read the file the session's graph saves in"):
            expect(self.files).to(equal([self.saved]))

        with it("should report the violations that file holds"):
            expect([violation.rule for violation in self.graph.violations()]).to(
                equal(["limit-operation-parameters", "load-with-identity-in-hand"])
            )
