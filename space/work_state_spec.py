"""The open session, branch, and worktree a chat keeps under the cdd home, never in the checkout."""

import shutil
import sys
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from space.work_state import WorkState


with description("a chat's work state"):
    with before.each:
        self.root = Path(tempfile.mkdtemp())
        self.home = Path(tempfile.mkdtemp())
        self.state = lambda chat="": WorkState(self.root, chat, home=self.home)

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)
        shutil.rmtree(self.home, ignore_errors=True)

    with context("with a session opened by one chat"):
        with before.each:
            self.state("chat-a").session = "self-care"

        with it("should read back that chat's session"):
            expect(self.state("chat-a").session).to(equal("self-care"))

        with it("should leave another chat on no session"):
            expect(self.state("chat-b").session).to(equal(""))

        with it("should leave a call naming no chat on no session"):
            expect(self.state().session).to(equal(""))

        with it("should write nothing in the checkout"):
            expect(list(self.root.iterdir())).to(equal([]))

        with it("should keep the state in the cdd home"):
            expect(self.state("chat-a").path.parent).to(equal(self.home.resolve()))

    with context("with a session opened by a call naming no chat"):
        with before.each:
            self.state().session = "legacy-compare"

        with it("should read back the checkout folder's session"):
            expect(self.state().session).to(equal("legacy-compare"))

        with it("should treat an unknown chat as no chat"):
            expect(self.state("unknown").session).to(equal("legacy-compare"))
