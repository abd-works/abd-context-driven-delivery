"""The mods a cdd home publishes for every chat, published by several real processes at the same moment, as installs
from the main checkout and a ticket's worktree do."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.mcp.cdd_home import BOARD_PLUGIN, CddHome

# One install's publishing in a process of its own, repeated so the processes overlap however they start.
_PUBLISH_IN_ITS_OWN_PROCESS = (
    "import sys; sys.path.insert(0, sys.argv[1]); "
    "from harness.mcp.cdd_home import CddHome; "
    "home = CddHome(sys.argv[2]); "
    "[home.write_mod_plugins() for _ in range(4)]"
)
_PUBLISHERS = 4
_PUBLISH_SECONDS = 120


def _start_publishing(home: CddHome) -> subprocess.Popen:
    command = [sys.executable, "-c", _PUBLISH_IN_ITS_OWN_PROCESS, str(_REPO_ROOT), str(home.folder)]
    return subprocess.Popen(command, cwd=_REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")


with description("a cdd home's Claude Code plugins") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-home-"))
        self.home = CddHome(self.root / ".cdd")
        self.home.folder.mkdir(parents=True)
        # The home serves this checkout pinned, so publishing reads the mods here and writes nothing back into it.
        runtime = {"source": str(_REPO_ROOT), "mode": CddHome.PINNED}
        (self.home.folder / "runtime.json").write_text(json.dumps(runtime), encoding="utf-8")

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    with context("with several installs publishing the mods at the same moment"):
        with before.each:
            publishers = [_start_publishing(self.home) for _ in range(_PUBLISHERS)]
            self.outcomes = [(publisher.communicate(timeout=_PUBLISH_SECONDS)[1], publisher.returncode) for publisher in publishers]

        with it("should finish every one"):
            failed = [errors[-500:] for errors, code in self.outcomes if code]
            expect(failed).to(equal([]))

        with it("should leave the board mod whole in the marketplace"):
            manifest = self.home.claude_plugins / BOARD_PLUGIN / ".claude-plugin" / "plugin.json"
            expect(json.loads(manifest.read_text(encoding="utf-8"))["name"]).to(equal(BOARD_PLUGIN))
