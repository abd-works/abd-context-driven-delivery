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

from expects import end_with, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets
from harness.mcp.cdd_home import CddHome, RuntimeRecordUnreadable

BOARD_MOD = Path("harness") / "chat-ui" / "pane"
QUEUE_MOD = Path("tools") / "prompt_queue"


def _checkout_with_board_mod(root: Path) -> Path:
    mod = root / "checkout" / BOARD_MOD
    (mod / ".claude-plugin").mkdir(parents=True)
    (mod / "hooks").mkdir()
    (mod / "types").mkdir()
    (mod / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "cdd-board", "version": "0.6.3"}), encoding="utf-8")
    (mod / "hooks" / "hooks.json").write_text("{}", encoding="utf-8")
    (mod / "hooks" / "register.ts").write_text("export default {}\n", encoding="utf-8")
    (mod / "hooks" / "register.test.ts").write_text("test('x', () => {})\n", encoding="utf-8")
    (mod / "types" / "index.d.ts").write_text("export {}\n", encoding="utf-8")
    viewer = root / "checkout" / "tools" / "drawio_viewer"
    viewer.mkdir(parents=True)
    (viewer / "drawio_viewer.py").write_text("# the viewer", encoding="utf-8")
    queue = root / "checkout" / QUEUE_MOD
    (queue / ".claude-plugin").mkdir(parents=True)
    (queue / "hooks").mkdir()
    (queue / ".claude-plugin" / "plugin.json").write_text(json.dumps({"name": "prompt-queue", "version": "0.1.0", "description": "A prompt queue"}), encoding="utf-8")
    (queue / "hooks" / "register.tsx").write_text("export default { queue: true }\n", encoding="utf-8")
    return root / "checkout"


def _plugin_names(home: CddHome) -> list[str]:
    marketplace = json.loads((home.claude_plugins / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    return [plugin["name"] for plugin in marketplace["plugins"]]


def _board_version(home: CddHome) -> str:
    return json.loads((home.claude_plugins / "cdd-board" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


with description("a cdd home's Claude Code plugins") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-home-"))
        self.home = CddHome(self.root / ".cdd")

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("that serves no code yet"):
        with before.each:
            self.home.write_claude_plugin({"type": "http"})

        with it("should list only the cdd plugin"):
            expect(_plugin_names(self.home)).to(equal(["cdd"]))

        # The server names a Claude Code chat from its connection, so the plugin runs nothing before a chat connects;
        # the hook only starts a server that is not running.
        with it("should start the server when a chat starts"):
            hooks = json.loads((self.home.claude_plugins / "cdd" / "hooks" / "hooks.json").read_text(encoding="utf-8"))
            command = hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
            expect(command).to(end_with(f'"{self.home.connect_script}" --start'))

    # A chat runs the board mod its marketplace names; one named in a worktree runs that branch's mod, whatever the server runs.
    with context("that serves a checkout"):
        with before.each:
            self.checkout = _checkout_with_board_mod(self.root)
            self.home.write_claude_plugin({"type": "http"})
            self.home.serve_from(self.checkout)
            self.board = self.home.claude_plugins / "cdd-board"

        with it("should list the board and prompt queue mods beside the cdd plugin"):
            expect(_plugin_names(self.home)).to(equal(["cdd", "cdd-board", "prompt-queue"]))

        # The prompt queue is a mod beside the chat bar, so every chat gets it from the code the server runs.
        with it("should publish that checkout's prompt queue mod"):
            queue = self.home.claude_plugins / "prompt-queue"
            expect((queue / "hooks" / "register.tsx").read_text(encoding="utf-8")).to(equal("export default { queue: true }\n"))

        with it("should keep the prompt queue's own version as the start of the published one"):
            manifest = json.loads((self.home.claude_plugins / "prompt-queue" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
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
                self.command = json.loads((self.board / CddHome.INSTALL_COMMAND).read_text(encoding="utf-8"))["command"]

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

    # Every chat installs its mods from the stable lane's marketplace, so a feature's mods stay there while its dev lane
    # runs, whichever lane's server restarts.
    with context("with a dev lane beside it, serving a feature checkout whose prompt queue mod differs"):
        with before.each:
            self.home.write_claude_plugin({"type": "http"})
            self.home.serve_from(_checkout_with_board_mod(self.root / "stable"))
            feature = _checkout_with_board_mod(self.root / "feature")
            (feature / QUEUE_MOD / "hooks" / "register.tsx").write_text("export default { feature: true }\n", encoding="utf-8")
            self.dev = CddHome(self.home.folder / "dev")
            self.dev.write_claude_plugin({"type": "http"})
            self.dev.serve_from(feature)
            self.published_queue = lambda: (self.home.claude_plugins / "prompt-queue" / "hooks" / "register.tsx").read_text(encoding="utf-8")

        with context("that the dev lane's server restarts"):
            with it("should publish the feature's mods where every chat installs them"):
                self.dev.publish_mods_for_chats(is_dev_lane_running=True)
                expect(self.published_queue()).to(equal("export default { feature: true }\n"))

        with context("that the stable server restarts while the dev lane's server runs"):
            with it("should keep the feature's mods where every chat installs them"):
                self.home.publish_mods_for_chats(is_dev_lane_running=True)
                expect(self.published_queue()).to(equal("export default { feature: true }\n"))

        with context("that the stable server restarts with the dev lane's server stopped"):
            with it("should publish the stable lane's own mods"):
                self.home.publish_mods_for_chats(is_dev_lane_running=False)
                expect(self.published_queue()).to(equal("export default { queue: true }\n"))


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


with description("a cdd home's server environment") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-home-"))
        self.home = CddHome(self.root / ".cdd")
        self.checkout = _checkout_with_board_mod(self.root)
        self.home.serve_from(self.checkout)

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with it("should keep the server's bytecode where the checkout's toolsets keep theirs, as the hook daemon does"):
        expect(self.home.server_environment["PYTHONPYCACHEPREFIX"]).to(equal(RepositoryToolsets(self.checkout).pycache_prefix()))
