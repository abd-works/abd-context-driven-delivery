"""Server health as the tool the band calls (cdd MCP), through the MCP server.

Each signature here has a test of the same name in `harness/chat-ui/pane/hooks/register.test.ts`."""
import json
import shutil
import socket
import tempfile
from pathlib import Path

from expects import be_false, be_none, equal, expect
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from harness.health.server_health import ServerHealth  # noqa: E402
from harness.installation.destination import data_of  # noqa: E402
from harness.mcp.mcp_server import McpServer  # noqa: E402


def closed_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


with description("server health") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="server-health-"))

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("with the graph app listening on the second of its ports"):
        with before.each:
            self.listener = socket.socket()
            self.listener.bind(("127.0.0.1", 0))
            self.listener.listen()
            self.port = self.listener.getsockname()[1]
            self.health = ServerHealth(self.root, graph_ports=(closed_port(), self.port), kanban_ports=(closed_port(),))

        with after.each:
            self.listener.close()

        with it("should report the port the graph app answers on"):
            expect(data_of(self.health.report())["graph_app_port"]).to(equal(self.port))

    with context("with nothing listening on the graph app's ports"):
        with it("should report no graph app port"):
            health = ServerHealth(self.root, graph_ports=(closed_port(),), kanban_ports=(closed_port(),))
            expect(data_of(health.report())["graph_app_port"]).to(be_none)

    with context("with the Kanban app listening on its port"):
        with before.each:
            self.listener = socket.socket()
            self.listener.bind(("127.0.0.1", 0))
            self.listener.listen()
            self.port = self.listener.getsockname()[1]

        with after.each:
            self.listener.close()

        with it("should report the port the Kanban app answers on"):
            health = ServerHealth(self.root, graph_ports=(closed_port(),), kanban_ports=(self.port,))
            expect(data_of(health.report())["kanban_app_port"]).to(equal(self.port))

    with context("with nothing listening on the Kanban app's port"):
        with it("should report no Kanban app port"):
            health = ServerHealth(self.root, graph_ports=(closed_port(),), kanban_ports=(closed_port(),))
            expect(data_of(health.report())["kanban_app_port"]).to(be_none)

    with context("with no hook server state in the project"):
        with it("should report the hook server is not running"):
            expect(data_of(ServerHealth(self.root).report())["is_hook_server_running"]).to(be_false)

    with context("with a hook server state file whose process has gone"):
        with it("should report the hook server is not running"):
            state = self.root / ".cursor" / "hook-server.json"
            state.parent.mkdir()
            state.write_text(json.dumps({"port": closed_port()}), encoding="utf-8")
            expect(data_of(ServerHealth(self.root).report())["is_hook_server_running"]).to(be_false)

    with context("called through the MCP server for the project the call names"):
        with before.each:
            self.server = McpServer(project=self.root)
            self.server.start(("harness.health.server_health:ServerHealth",))

        with it("should answer the band's call with every part"):
            result = self.server.invoke_tool("server-health.report", {})
            answer = json.loads(json.dumps(result, default=data_of))
            expect(sorted(answer)).to(equal(["graph_app_port", "is_hook_server_running", "kanban_app_port"]))

        with it("should leave the session log alone"):
            self.server.invoke_tool("server-health.report", {})
            logged = [log.read_text(encoding="utf-8") for log in self.root.glob(".sessions/**/session.log")]
            expect("server-health" in "".join(logged)).to(be_false)
