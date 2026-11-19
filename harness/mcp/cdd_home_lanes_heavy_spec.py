"""The mods every chat installs while a dev lane runs beside the stable lane: each example serves two checkouts and
publishes their mods as real files, which takes longer than a unit example may."""
import shutil
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.mcp.cdd_home import CddHome
from harness.mcp.cdd_home_checkout_examples import QUEUE_MOD, checkout_with_board_mod

with description("a cdd home's Claude Code plugins") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-home-"))
        self.home = CddHome(self.root / ".cdd")

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    # Every chat installs its mods from the stable lane's marketplace, so a feature's mods stay there while its dev lane
    # runs, whichever lane's server restarts.
    with context("with a dev lane beside it, serving a feature checkout whose prompt queue mod differs"):
        with before.each:
            self.home.write_claude_plugin({"type": "http"})
            self.home.serve_from(checkout_with_board_mod(self.root / "stable"))
            feature = checkout_with_board_mod(self.root / "feature")
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
