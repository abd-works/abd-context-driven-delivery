"""The MCP config cdd writes its entry into: the user's other servers in it survive the write, and a dev lane's
worktree gets an entry naming the dev lane's server."""
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

from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_address import PROJECT_HEADER, McpAddress
from harness.mcp.mcp_server import McpConfigUnreadable, McpInstallation
from harness.mcp.server_lanes import ServerLanes
from harness.installation.ide_layout import IdeLayout

UNREADABLE = '{"mcpServers": {"notes": {"command": "notes-server"},'


with description("an MCP config that cdd writes its entry into") as self:
    with before.each:
        self.project = Path(tempfile.mkdtemp(prefix="cdd-mcp-config-"))
        self.config = self.project / ".mcp.json"
        self.installation = McpInstallation.create(IdeLayout("Claude"), self.project / ".claude")
        self.installation.write(SimpleNamespace(install_to_mcp=True))

    with after.each:
        shutil.rmtree(self.project, ignore_errors=True)

    with context("that names another server"):
        with before.each:
            self.config.write_text(json.dumps({"mcpServers": {"notes": {"command": "notes-server"}}}), encoding="utf-8")
            self.installation.cdd_entry.write()
            self.servers = json.loads(self.config.read_text(encoding="utf-8"))["mcpServers"]

        with it("should add the cdd entry"):
            expect(list(self.servers)).to(contain("cdd"))

        with it("should keep the other server"):
            expect(self.servers["notes"]).to(equal({"command": "notes-server"}))

    with context("that is not readable JSON"):
        with before.each:
            self.config.write_text(UNREADABLE, encoding="utf-8")

        with it("should refuse to write it, naming the file"):
            expect(self.installation.cdd_entry.write).to(raise_error(McpConfigUnreadable))

        with it("should leave what it holds as it was"):
            try:
                self.installation.cdd_entry.write()
            except McpConfigUnreadable:
                pass
            expect(self.config.read_text(encoding="utf-8")).to(equal(UNREADABLE))


with description("a VS Code install tree's MCP config") as self:
    with before.each:
        self.tree = Path(tempfile.mkdtemp(prefix="cdd-vscode-tree-")) / ".vscode"
        self.installation = McpInstallation.create(IdeLayout("VS Code"), self.tree)
        self.installation.write(SimpleNamespace(install_to_mcp=True))
        self.installation.cdd_entry.write()
        self.config = json.loads(self.installation.cdd_entry.path.read_text(encoding="utf-8"))

    with after.each:
        shutil.rmtree(self.tree.parent, ignore_errors=True)

    with it("should list cdd under the key VS Code reads its servers from"):
        expect(self.config).to(equal({"servers": self.config["servers"]}))


with description("the cdd entry a checkout's chats reach its lane's server through") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-lane-entry-"))
        self.project = self.root / "checkout"
        self.project.mkdir()
        self.config = self.project / ".mcp.json"
        self.lanes = ServerLanes(CddHome(self.root / "home"), McpAddress(47900))

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("of a ticket's worktree, served on the dev lane"):
        with before.each:
            self.config.write_text(json.dumps({"mcpServers": {"notes": {"command": "notes-server"}}}), encoding="utf-8")
            installation = McpInstallation(IdeLayout("Claude"), self.project / ".claude", self.lanes.dev.served_checkout(self.project))
            installation.cdd_entry.point_chats_at_served_lane()
            self.servers = json.loads(self.config.read_text(encoding="utf-8"))["mcpServers"]

        with it("should name the dev lane's server"):
            expect(self.servers["cdd"]["url"]).to(equal(self.lanes.dev.daemon.url))

        with it("should name the worktree as the chats' project"):
            expect(self.servers["cdd"]["headers"]).to(equal({PROJECT_HEADER: str(self.project.resolve())}))

        with it("should keep the other server"):
            expect(self.servers["notes"]).to(equal({"command": "notes-server"}))

    with context("of a main checkout, served on the stable lane"):
        with before.each:
            servers = {"cdd": {"type": "http", "url": self.lanes.dev.daemon.url}, "notes": {"command": "notes-server"}}
            self.config.write_text(json.dumps({"mcpServers": servers}), encoding="utf-8")
            installation = McpInstallation(IdeLayout("Claude"), self.project / ".claude", self.lanes.stable.served_checkout(self.project))
            installation.cdd_entry.point_chats_at_served_lane()
            self.servers = json.loads(self.config.read_text(encoding="utf-8"))["mcpServers"]

        with it("should drop the cdd entry, so the cdd plugin's server answers"):
            expect(list(self.servers)).to(equal(["notes"]))
