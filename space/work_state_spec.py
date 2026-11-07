"""The work state a repo shares between its sessions, hosts, and commands."""

import os
import shutil
import stat
import sys
import tempfile
import threading
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from space.work_state import WorkState, project_checkout, working_on


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


with description("the project being worked on"):
    with before.each:
        self.first = Path(tempfile.mkdtemp())
        self.second = Path(tempfile.mkdtemp())
        for project in (self.first, self.second):
            (project / ".git").mkdir()
            (project / "docs").mkdir()

    with after.each:
        shutil.rmtree(self.first, ignore_errors=True)
        shutil.rmtree(self.second, ignore_errors=True)

    with context("that a call names a folder inside a project"):
        with it("should be the checkout holding that folder"):
            with working_on(self.first / "docs"):
                expect(project_checkout()).to(equal(self.first.resolve()))

    with context("that a call names a folder in a linked worktree of a project"):
        with before.each:
            self.worktree = Path(tempfile.mkdtemp())
            worktree_git = self.first / ".git" / "worktrees" / "pet-visits"
            worktree_git.mkdir(parents=True)
            (worktree_git / "commondir").write_text("../..\n", encoding="utf-8")
            (self.worktree / ".git").write_text(f"gitdir: {worktree_git}\n", encoding="utf-8")
            (self.worktree / "docs").mkdir()

        with after.each:
            shutil.rmtree(self.worktree, ignore_errors=True)

        with it("should be the worktree holding that folder"):
            with working_on(self.worktree / "docs"):
                expect(project_checkout()).to(equal(self.worktree.resolve()))

    with context("that the call has finished"):
        with it("should no longer be the project that call named"):
            with working_on(self.first):
                pass
            expect(project_checkout()).not_to(equal(self.first.resolve()))

    with context("that two calls work on different projects at the same time"):
        with it("should give each call its own project"):
            seen: dict[str, Path] = {}
            both_inside = threading.Barrier(2)

            def look(name: str, project: Path) -> None:
                with working_on(project):
                    both_inside.wait(timeout=5)
                    seen[name] = project_checkout()

            calls = [threading.Thread(target=look, args=item) for item in (("first", self.first), ("second", self.second))]
            for call in calls:
                call.start()
            for call in calls:
                call.join()
            expect(seen).to(equal({"first": self.first.resolve(), "second": self.second.resolve()}))
