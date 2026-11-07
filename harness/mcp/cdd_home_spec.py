"""The Claude Code plugins a cdd home publishes: the cdd plugin, and the board mod from the code the server runs."""

import json
import shutil
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.mcp.cdd_home import CddHome, RuntimeRecordUnreadable

BOARD_MOD = Path("harness") / "chat-ui" / "pane"


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

    # A chat runs the board mod its marketplace names; one named in a worktree runs that branch's mod, whatever the server runs.
    with context("that serves a checkout"):
        with before.each:
            self.checkout = _checkout_with_board_mod(self.root)
            self.home.write_claude_plugin({"type": "http"})
            self.home.serve_from(self.checkout)
            self.board = self.home.claude_plugins / "cdd-board"

        with it("should list the board mod beside the cdd plugin"):
            expect(_plugin_names(self.home)).to(equal(["cdd", "cdd-board"]))

        with it("should publish that checkout's board mod"):
            expect((self.board / "hooks" / "register.ts").read_text(encoding="utf-8")).to(equal("export default {}\n"))

        with it("should leave the mod's tests out"):
            expect((self.board / "hooks" / "register.test.ts").exists()).to(equal(False))

        with it("should keep the mod's own version as the start of the published one"):
            expect(_board_version(self.home).startswith("0.6.3-")).to(equal(True))

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
