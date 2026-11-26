"""Server health as the tool the band calls (cdd MCP), through the MCP server. Its servers reached over real sockets, and
every report that checks the registered apps' ports, are in server_health_heavy_spec.py.

The chat bar draws this report as its server health mark, panel and toasts (`harness/chat-ui/pane/hooks/health/`), which
have no plugin test yet: the TypeScript tests of the same names were removed in 8c56ab052."""
import json
import shutil
import tempfile
from pathlib import Path

from expects import be_false, be_none, equal, expect
from mamba import after, before, context, description, it

from harness.agent_tools.agent_tools import ToolsetReference
from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from harness.mcp.mcp_server import ProjectToolsets  # noqa: E402
from harness.diagnostics.server_health import ServerHealth  # noqa: E402
from harness.release.test_runs import TestCadence, TestRunRecord  # noqa: E402

STEP = "Delete Ticket › Refuse to delete a ticket the board does not have › 3 Then the board says no ticket named 'no-such-ticket' on the board"


with description("server health") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="server-health-"))

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("called through the MCP server for the project the call names"):
        with before.each:
            self.server = ProjectToolsets(project=self.root)
            self.server.start((ToolsetReference.parsed("harness.diagnostics.server_health:ServerHealth"),))

        with it("should leave the session log alone"):
            self.server.invoke("server-health.report", {})
            logged = [log.read_text(encoding="utf-8") for log in self.root.glob(".sessions/**/session.log")]
            expect("server-health" in "".join(logged)).to(be_false)

    with context("with no scheduled e2e run that captured its screens"):
        with it("should report no e2e review"):
            expect(ServerHealth(self.root, cadence=TestCadence(TestRunRecord(self.root / "home"))).e2e_review).to(be_none)

    with context("with a scheduled e2e run whose screen review missed a step"):
        with before.each:
            run = self.root / ".sessions" / "scheduled" / "e2e-test-results" / "move-work-forward-on-session-board" / "maintain-tickets" / "run-2"
            run.mkdir(parents=True)
            (run / "results.json").write_text(json.dumps([{"key": STEP}]), encoding="utf-8")
            summary = {"steps": 1, "changed_steps": [STEP], "unjudged_steps": [], "missed_steps": [STEP]}
            (run / "changed.json").write_text(json.dumps(summary), encoding="utf-8")
            self.health = ServerHealth(self.root, cadence=TestCadence(TestRunRecord(self.root / "home")))

        with it("should report the run's name"):
            expect(self.health.e2e_review.run).to(equal("run-2"))

        with it("should report the missed step with its sub-epic"):
            expect(self.health.e2e_review.missed_steps).to(equal([f"move-work-forward-on-session-board/maintain-tickets: {STEP}"]))

        with it("should link the e2e story map report"):
            expect(self.health.e2e_review.report.name).to(equal("story-map.html"))
