"""The Claude Code plugins a cdd home publishes: the cdd plugin, and the board and prompt queue mods from the code the
server runs."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, end_with, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets
from harness.mcp.cdd_home import CddHome, RuntimeNotInstalled, RuntimeRecordUnreadable
from harness.mcp.claude_marketplace import ClaudeMarketplace
from harness.mcp.cdd_home_checkout_examples import BOARD_MOD, QUEUE_MOD, checkout_with_board_mod

def _plugin_names(home: CddHome) -> list[str]:
    marketplace = json.loads((home.marketplace.folder / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    return [plugin["name"] for plugin in marketplace["plugins"]]


def _board_version(home: CddHome) -> str:
    return json.loads((home.marketplace.folder / "cdd-board" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


with description("a cdd home's Claude Code plugins") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-home-"))
        self.home = CddHome(self.root / ".cdd")

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("that serves no code yet"):
        with before.each:
            self.home.marketplace.publish_cdd_plugin({"type": "http"})

        with it("should list only the cdd plugin"):
            expect(_plugin_names(self.home)).to(equal(["cdd"]))

        # The server names a Claude Code chat from its connection, so the plugin runs nothing before a chat connects;
        # the hook only starts a server that is not running.
        with it("should start the server when a chat starts"):
            hooks = json.loads((self.home.marketplace.folder / "cdd" / "hooks" / "hooks.json").read_text(encoding="utf-8"))
            command = hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
            expect(command).to(end_with(f'"{self.home.connect_script}" --start'))

    # A chat runs the board mod its marketplace names; one named in a worktree runs that branch's mod, whatever the server runs.
    with context("that serves a checkout"):
        with before.each:
            self.checkout = checkout_with_board_mod(self.root)
            self.home.marketplace.publish_cdd_plugin({"type": "http"})
            self.home.serve_from(self.checkout)
            self.board = self.home.marketplace.folder / "cdd-board"

        with it("should list the board and prompt queue mods beside the cdd plugin"):
            expect(_plugin_names(self.home)).to(equal(["cdd", "cdd-board", "prompt-queue"]))

        # The prompt queue is a mod beside the chat bar, so every chat gets it from the code the server runs.
        with it("should publish that checkout's prompt queue mod"):
            queue = self.home.marketplace.folder / "prompt-queue"
            expect((queue / "hooks" / "register.tsx").read_text(encoding="utf-8")).to(equal("export default { queue: true }\n"))

        with it("should keep the prompt queue's own version as the start of the published one"):
            manifest = json.loads((self.home.marketplace.folder / "prompt-queue" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
            expect(manifest["version"].startswith("0.1.0-")).to(equal(True))

        with it("should publish that checkout's board mod"):
            expect((self.board / "hooks" / "register.ts").read_text(encoding="utf-8")).to(equal("export default {}\n"))

        # The chat bar opens diagrams in the viewer, so a chat outside a CDD checkout needs the viewer in the mod.
        with it("should publish the draw.io viewer inside the board mod"):
            expect((self.board / "drawio-viewer" / "drawio_viewer.py").read_text(encoding="utf-8")).to(equal("# the viewer"))

        with it("should leave the mod's tests out"):
            expect((self.board / "hooks" / "register.test.ts").exists()).to(equal(False))

        with it("should keep the mod's own version as the start of the published one"):
            expect(_board_version(self.home).startswith("0.6.3-")).to(equal(True))

        # Run install works when the server is what is broken, so the mod reads the command from its own folder.
        with context("whose mod runs an install for a chat"):
            with before.each:
                self.command = json.loads((self.board / ClaudeMarketplace.INSTALL_COMMAND).read_text(encoding="utf-8"))["command"]

            with it("should run it on the Python the server runs on"):
                expect(self.command[0]).to(equal(str(self.home.interpreter.executable)))

            with it("should run the served checkout's install script"):
                expect(self.command[1]).to(equal(str(self.checkout.resolve() / "scripts" / "install.py")))

            with it("should end on the flag that takes the chat's folder"):
                expect(self.command[-1]).to(equal("--from-chat"))

        # Claude Code keeps a plugin it has seen at the same version, so a changed mod needs a new one.
        with context("whose board mod has since changed"):
            with before.each:
                self.first_version = _board_version(self.home)
                (self.checkout / BOARD_MOD / "hooks" / "register.ts").write_text("export default { folder: true }\n", encoding="utf-8")
                self.home.serve_from(self.checkout)

            with it("should publish the changed mod"):
                expect((self.board / "hooks" / "register.ts").read_text(encoding="utf-8")).to(equal("export default { folder: true }\n"))

            with it("should give it a new version"):
                expect(_board_version(self.home)).not_to(equal(self.first_version))

        # A person working on CDD itself chose to serve the checkout, so an update from the board keeps serving it.
        with context("that is brought up to date"):
            with before.each:
                self.home.serve_current(self.checkout)

            with it("should still serve the checkout as it is on disk"):
                expect((self.home.mode, self.home.source)).to(equal((CddHome.CHECKOUT, self.checkout.resolve())))

with description("a cdd home's runtime record") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-home-"))
        self.home = CddHome(self.root / ".cdd")

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("that is not readable JSON"):
        with before.each:
            self.home.folder.mkdir(parents=True)
            self.home.runtime_record.write_text('{"source": ', encoding="utf-8")

        with it("should refuse to say whether cdd is installed, naming the file"):
            expect(lambda: self.home.is_installed).to(raise_error(RuntimeRecordUnreadable))

        with it("should leave the record as it was"):
            try:
                self.home.install(self.root, Path(__file__).resolve().parent / "scripts" / "connect.py")
            except RuntimeRecordUnreadable:
                pass
            expect(self.home.runtime_record.read_text(encoding="utf-8")).to(equal('{"source": '))

    with context("that is not there, since cdd was never installed in the home"):
        with it("should refuse to name the checkout the server runs, naming the home"):
            expect(lambda: self.home.source).to(raise_error(RuntimeNotInstalled, contain(str(self.home.folder))))


with description("a cdd home's server environment") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-home-"))
        self.home = CddHome(self.root / ".cdd")
        self.checkout = checkout_with_board_mod(self.root)
        self.home.serve_from(self.checkout)

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with it("should keep the server's bytecode where the checkout's toolsets keep theirs, as the hook daemon does"):
        expect(self.home.server_environment["PYTHONPYCACHEPREFIX"]).to(equal(RepositoryToolsets(self.checkout).pycache_prefix()))


def _pinned_from(home: CddHome, worktree: Path) -> None:
    """A runtime record as a pin from worktree leaves it, on the branch feature-x."""
    home.folder.mkdir(parents=True, exist_ok=True)
    record = {"source": str(home.pinned_checkout), "mode": CddHome.PINNED, "worktree": str(worktree), "branch": "feature-x", "commit": "1b684af68"}
    home.runtime_record.write_text(json.dumps(record), encoding="utf-8")


with description("a lane's served feature") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-home-"))
        self.stable = CddHome(self.root / ".cdd")
        self.dev = self.stable.dev_lane
        self.worktree = self.root / "checkout-feature"
        self.worktree.mkdir()

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("pinned on the dev lane from a worktree that is gone"):
        with before.each:
            _pinned_from(self.dev, self.worktree)
            self.worktree.rmdir()
            self.said = self.dev.return_to_main_when_feature_gone()

        with it("should say the dev lane runs main again, naming the branch and the worktree that is gone"):
            expect(self.said).to(contain("feature-x", str(self.worktree), "main"))

        with it("should serve no feature on the dev lane, so its chats run on main"):
            expect(self.dev.is_installed).to(equal(False))

    with context("pinned on the dev lane from a worktree still there"):
        with before.each:
            _pinned_from(self.dev, self.worktree)
            self.said = self.dev.return_to_main_when_feature_gone()

        with it("should say nothing"):
            expect(self.said).to(equal(""))

        with it("should keep serving the feature"):
            expect(self.dev.served_branch).to(equal("feature-x"))

    with context("pinned on the stable lane from a checkout that is gone"):
        with before.each:
            _pinned_from(self.stable, self.worktree)
            self.worktree.rmdir()

        with it("should be left as it is, since the stable lane runs main"):
            self.stable.return_to_main_when_feature_gone()
            expect(self.stable.is_installed).to(equal(True))
