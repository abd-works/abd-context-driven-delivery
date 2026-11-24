"""The mods each lane publishes while a dev lane runs beside the stable lane: each example serves two checkouts and
publishes their mods as real files, which takes longer than a unit example may."""
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.installation.ide_layout import IdeLayout
from harness.mcp.cdd_home import CddHome
from harness.mcp.cdd_home_checkout_examples import QUEUE_MOD, checkout_with_board_mod
from harness.mcp.mcp_address import McpAddress
from harness.mcp.mcp_server import McpChannelServer, McpHost
from harness.mcp.server_lanes import ServerLanes

STABLE_QUEUE = "export default { queue: true }\n"
FEATURE_QUEUE = "export default { feature: true }\n"


def restartable_toolsets(project: Path) -> SimpleNamespace:
    """A checkout's toolsets whose restart answers themselves, so a host restarts without loading any toolset."""
    toolsets = SimpleNamespace(project=project, tools={}, prompts={}, skipped=SimpleNamespace(as_data=[]))
    toolsets.restarted = lambda: toolsets
    return toolsets


with description("a cdd home's Claude Code plugins") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-home-"))
        self.home = CddHome(self.root / ".cdd")

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    # The stable lane's marketplace is the one every chat's plugins come from, and the stable server runs main, so a
    # feature's mods stay in the dev lane's own marketplace: a stable chat never gets a button its server cannot serve.
    with context("with a dev lane beside it, serving a feature checkout whose prompt queue mod differs"):
        with before.each:
            self.home.marketplace.publish_cdd_plugin({"type": "http"})
            self.home.serve_from(checkout_with_board_mod(self.root / "stable"))
            self.feature = checkout_with_board_mod(self.root / "feature")
            (self.feature / QUEUE_MOD / "hooks" / "register.tsx").write_text(FEATURE_QUEUE, encoding="utf-8")
            self.lanes = ServerLanes(self.home, McpAddress(47900))
            self.dev = self.lanes.dev.home
            self.dev.marketplace.publish_cdd_plugin({"type": "http"})
            self.dev.serve_from(self.feature)
            self.queue_of = lambda home: (home.marketplace.folder / "prompt-queue" / "hooks" / "register.tsx").read_text(encoding="utf-8")

        with context("that a dev-lane install installs its mods"):
            with before.each:
                plugins = SimpleNamespace(install=lambda plugin: "installed")
                server = McpChannelServer(self.lanes.dev.served_checkout(self.feature), self.lanes, plugins, IdeLayout("Claude"))
                server.install_mods()

            with it("should leave the stable lane's mods as the stable lane's code has them"):
                expect(self.queue_of(self.home)).to(equal(STABLE_QUEUE))

            with it("should keep the feature's mods in the dev lane's own marketplace"):
                expect(self.queue_of(self.dev)).to(equal(FEATURE_QUEUE))

        with context("that the dev lane's server restarts"):
            with before.each:
                McpHost(restartable_toolsets(self.feature), self.lanes, self.dev).restart()

            with it("should leave the stable lane's mods as the stable lane's code has them"):
                expect(self.queue_of(self.home)).to(equal(STABLE_QUEUE))

            with it("should publish the feature's mods in the dev lane's own marketplace"):
                expect(self.queue_of(self.dev)).to(equal(FEATURE_QUEUE))

        with context("that the stable server restarts"):
            with before.each:
                (self.home.marketplace.folder / "prompt-queue" / "hooks" / "register.tsx").write_text(FEATURE_QUEUE, encoding="utf-8")
                McpHost(restartable_toolsets(self.home.source), self.lanes, self.home).restart()

            with it("should publish the stable lane's own mods"):
                expect(self.queue_of(self.home)).to(equal(STABLE_QUEUE))
