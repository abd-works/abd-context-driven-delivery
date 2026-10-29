"""The work state a repo shares between its sessions, hosts, and commands."""

import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from space.work_state import WorkState


with description("a repo's work state"):
    with before.each:
        self.root = Path(tempfile.mkdtemp())
        WorkState(self.root).session = "self-care"

    with after.each:
        os.chmod(WorkState(self.root).path, stat.S_IWRITE | stat.S_IREAD)
        shutil.rmtree(self.root, ignore_errors=True)

    with context("with a session already saved"):
        with context("that another host holds open read-only while this one starts"):
            with before.each:
                os.chmod(WorkState(self.root).path, stat.S_IREAD)

            with it("should accept the same session without writing the file"):
                WorkState(self.root).session = "self-care"
                expect(WorkState(self.root).session).to(equal("self-care"))

        with context("that is set to another session"):
            with before.each:
                WorkState(self.root).session = "legacy-compare"

            with it("should read back the new session"):
                expect(WorkState(self.root).session).to(equal("legacy-compare"))

            with it("should leave only the state file in the folder"):
                expect(sorted(item.name for item in WorkState(self.root).path.parent.iterdir())).to(
                    equal(["session.json"])
                )

        with context("whose session names the release being worked on"):
            with it("should keep that release's files in its own session folder"):
                expect(WorkState(self.root).release_folder()).to(equal(self.root.resolve() / ".sessions" / "self-care"))

            with it("should find another release's folder by its name"):
                expect(WorkState(self.root).release_folder("main-release")).to(
                    equal(self.root.resolve() / ".sessions" / "main-release")
                )
