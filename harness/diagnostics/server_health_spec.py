"""Server health as the tool the band calls (cdd MCP), through the MCP server.

Each signature here has a test of the same name in `harness/chat-ui/pane/hooks/register.test.ts`."""
import json
import shutil
import socket
import tempfile
from pathlib import Path

from expects import be_false, equal, expect
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from harness.diagnostics.app import App, AppServer  # noqa: E402
from harness.diagnostics.server_health import ServerHealth  # noqa: E402
from harness.hooks.hook_daemon import HookDaemon  # noqa: E402
from harness.installation.data_class import data_of  # noqa: E402
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

    # Each app registers itself; the report lists every one, read as it is now, so the status row shows each.
    with context("with an app registered and answering on the second of its ports"):
        with before.each:
            self.held = App.registered()
            self.listener = socket.socket()
            self.listener.bind(("127.0.0.1", 0))
            self.listener.listen()
            self.port = self.listener.getsockname()[1]
            (self.root / "package.json").write_text("{}", encoding="utf-8")
            (self.root / "node_modules").mkdir()
            App("Graph", self.root, AppServer(self.root, "serve.js", (closed_port(), self.port))).register()

        with after.each:
            self.listener.close()
            for app in self.held:
                app.register()

        with it("should list the app with its status and the port it answers on"):
            graph = next(app for app in data_of(ServerHealth(self.root).report())["apps"] if app["label"] == "Graph")
            expect((graph["status"], graph["port"])).to(equal(("running", self.port)))

    with context("with no hook server state in the project"):
        with it("should report the hook server is not running"):
            expect(data_of(ServerHealth(self.root).report())["is_hook_server_running"]).to(be_false)

    with context("with a hook server state file whose process has gone"):
        with it("should report the hook server is not running"):
            state = HookDaemon(self.root).address_file.path
            state.parent.mkdir()
            state.write_text(json.dumps({"port": closed_port()}), encoding="utf-8")
            expect(data_of(ServerHealth(self.root).report())["is_hook_server_running"]).to(be_false)

    with context("called through the MCP server for the project the call names"):
        with before.each:
            self.server = McpServer(project=self.root)
            self.server.start(("harness.diagnostics.server_health:ServerHealth",))

        with it("should answer the band's call with every part"):
            result = self.server.invoke_tool("server-health.report", {})
            answer = json.loads(json.dumps(result, default=data_of))
            expect(sorted(answer)).to(equal(["apps", "is_hook_server_running"]))

        with it("should leave the session log alone"):
            self.server.invoke_tool("server-health.report", {})
            logged = [log.read_text(encoding="utf-8") for log in self.root.glob(".sessions/**/session.log")]
            expect("server-health" in "".join(logged)).to(be_false)
