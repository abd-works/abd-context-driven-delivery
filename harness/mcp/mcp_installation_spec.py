"""The MCP config cdd writes its entry into: the user's other servers in it survive the write."""
import json
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.mcp.mcp_server import McpConfigUnreadable, McpInstallation
from harness.installation.ide_layout import IdeLayout

UNREADABLE = '{"mcpServers": {"notes": {"command": "notes-server"},'


with description("an MCP config that cdd writes its entry into") as self:
    with before.each:
        self.project = Path(tempfile.mkdtemp(prefix="cdd-mcp-config-"))
        self.config = self.project / ".mcp.json"
        self.installation = McpInstallation(IdeLayout("Claude"), self.project / ".claude")
        self.installation.record_operation(SimpleNamespace(install_to_mcp=True))

    with after.each:
        shutil.rmtree(self.project, ignore_errors=True)

    with context("that names another server"):
        with before.each:
            self.config.write_text(json.dumps({"mcpServers": {"notes": {"command": "notes-server"}}}), encoding="utf-8")
            self.installation.write_mcp_manifest()
            self.servers = json.loads(self.config.read_text(encoding="utf-8"))["mcpServers"]

        with it("should add the cdd entry"):
            expect(list(self.servers)).to(contain("cdd"))

        with it("should keep the other server"):
            expect(self.servers["notes"]).to(equal({"command": "notes-server"}))

    with context("that is not readable JSON"):
        with before.each:
            self.config.write_text(UNREADABLE, encoding="utf-8")

        with it("should refuse to write it, naming the file"):
            expect(self.installation.write_mcp_manifest).to(raise_error(McpConfigUnreadable))

        with it("should leave what it holds as it was"):
            try:
                self.installation.write_mcp_manifest()
            except McpConfigUnreadable:
                pass
            expect(self.config.read_text(encoding="utf-8")).to(equal(UNREADABLE))
