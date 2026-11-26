"""A spec's cdd server keeps everything it writes under its own throwaway home, so a spec never changes the person's own
chats. Each context installs one server, with no server started, before its examples, which read what it named."""
import os
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_true, equal, expect
from mamba import after, before, context, description, it

from harness.mcp.spec_support import CHATS_FOLDER_ENV, SpecServer


def _install(spec) -> None:
    spec.server = SpecServer()
    spec.server.install()
    spec.named = os.environ.get(CHATS_FOLDER_ENV)


with description("a spec's cdd server") as self:
    with before.all:
        self.prior = os.environ.pop(CHATS_FOLDER_ENV, None)

    with after.all:
        if self.prior is not None:
            os.environ[CHATS_FOLDER_ENV] = self.prior

    with context("installed for a spec that names no chats folder"):
        with before.all:
            _install(self)
            self.server.stop()

        with it("should name a chats folder under its own home, never the person's"):
            expect(Path(self.named).is_relative_to(self.server.home.folder)).to(be_true)

        with it("should name none once stopped, as before it was installed"):
            expect(os.environ.get(CHATS_FOLDER_ENV)).to(equal(None))

    # A spec that names its own chats folder reads the chats the server writes there.
    with context("installed for a spec that names its own chats folder"):
        with before.all:
            self.own = tempfile.mkdtemp(prefix="spec-chats-")
            os.environ[CHATS_FOLDER_ENV] = self.own
            _install(self)
            self.server.stop()

        with after.all:
            os.environ.pop(CHATS_FOLDER_ENV, None)

        with it("should keep the spec's folder"):
            expect(self.named).to(equal(self.own))

        with it("should leave the spec's folder named once stopped"):
            expect(os.environ.get(CHATS_FOLDER_ENV)).to(equal(self.own))
