"""Server health as the tool the band calls (cdd MCP), through the MCP server. Its servers reached over real sockets, and
every report that checks the registered apps' ports, are in server_health_heavy_spec.py.

Each signature here has a test of the same name in `harness/chat-ui/pane/hooks/register.test.ts`."""
import shutil
import tempfile
from pathlib import Path

from expects import be_false, expect
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from harness.mcp.mcp_server import McpServer  # noqa: E402


with description("server health") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="server-health-"))

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("called through the MCP server for the project the call names"):
        with before.each:
            self.server = McpServer(project=self.root)
            self.server.start(("harness.diagnostics.server_health:ServerHealth",))

        with it("should leave the session log alone"):
            self.server.invoke_tool("server-health.report", {})
            logged = [log.read_text(encoding="utf-8") for log in self.root.glob(".sessions/**/session.log")]
            expect("server-health" in "".join(logged)).to(be_false)
