"""BDD spec — a worktree opened for a branch, and whether it is up to date with origin."""
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

from expects import be, be_false, be_none, be_true, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from space.repo.built_once import BuiltOnce  # noqa: E402
from space.repo.repo import Repo  # noqa: E402
from space.repo.worktree import WorktreeFolderTakenError, WorktreeNotRemovedError  # noqa: E402
from space.session.spec_support.throwaway_project import SPEC_RUN_HOME


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def _clone_with_origin(root: Path) -> None:
    origin = root / "origin.git"
    clone = root / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True, capture_output=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True, capture_output=True)
    _git(clone, "config", "user.email", "worktree@test")
    _git(clone, "config", "user.name", "worktree")
    _git(clone, "checkout", "-q", "-b", "main")
    (clone / ".gitignore").write_text(".sessions/\n", encoding="utf-8")
    _git(clone, "add", ".gitignore")
    _git(clone, "commit", "-q", "-m", "seed")
    _git(clone, "push", "-q", "origin", "main")


_REPOSITORIES = BuiltOnce("worktree-spec-", _clone_with_origin)


with description("a worktree opened for a branch") as self:
    with before.each:
        self.tmp = _REPOSITORIES.copy()
        self.origin, self.clone = self.tmp / "origin.git", self.tmp / "clone"

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with context("with origin no longer reachable"):
        with before.each:
            _git(self.clone, "remote", "set-url", "origin", str(self.tmp / "moved-away.git"))

        with context("that has been opened"):
            with before.each:
                self.opened = Repo(self.clone).branch_named("feature/a").open_in_worktree()

            with it("should check the branch out"):
                expect(_git(self.opened.root, "branch", "--show-current")).to(equal("feature/a"))

            with it("should still open the worktree folder"):
                expect(self.opened.root.is_dir()).to(be_true)

    with context("whose folder holds files past Windows' 260-character path limit"):
        with before.each:
            self.opened = Repo(self.clone).branch_named("feature/a").open_in_worktree()
            self.worktrees = Repo(self.clone).worktrees
            deep = self.opened.root.resolve().joinpath(".retired", *("fixture-folder-" * 4 for _ in range(5)))
            long_deep = f"\\\\?\\{deep}" if os.name == "nt" else str(deep)
            os.makedirs(long_deep, exist_ok=True)
            Path(long_deep, "fixture.md").write_text("retired", encoding="utf-8")

        with it("should remove the folder"):
            self.worktrees.remove(self.opened)
            expect(self.opened.root.exists()).to(be_false)

    # Only Windows refuses to delete a folder a running program works in.
    if os.name == "nt":
        with context("whose folder a running program holds open"):
            with before.each:
                self.repo = Repo(self.clone)
                self.opened = self.repo.branch_named("feature/a").open_in_worktree()
                (self.opened.root / "src").mkdir()
                self.holder = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], cwd=self.opened.root / "src")

            with after.each:
                self.holder.kill()
                self.holder.wait()

            with it("should refuse to call it removed, naming the folder left behind"):
                expect(lambda: self.repo.worktrees.remove(self.opened)).to(raise_error(WorktreeNotRemovedError, contain(self.opened.root.name)))

            with context("that has ended since its removal was refused"):
                with before.each:
                    expect(lambda: self.repo.worktrees.remove(self.opened)).to(raise_error(WorktreeNotRemovedError))
                    self.holder.kill()
                    self.holder.wait()
                    self.again = self.repo.branch_named("feature/a").open_in_worktree()

                with it("should open the branch again in a worktree"):
                    expect(_git(self.again.root, "branch", "--show-current")).to(equal("feature/a"))

    with context("whose folder was deleted outside CDD"):
        with before.each:
            self.repo = Repo(self.clone)
            self.opened = self.repo.branch_named("feature/a").open_in_worktree()
            shutil.rmtree(self.opened.root)

        with it("should no longer be the branch's worktree"):
            expect(self.repo.branch_named("feature/a").checkout).to(be_none)

        with it("should be made again when the branch is opened"):
            again = self.repo.branch_named("feature/a").open_in_worktree()
            expect(_git(again.root, "branch", "--show-current")).to(equal("feature/a"))

    with context("whose branch was deleted outside CDD, its folder left on no branch"):
        with before.each:
            self.repo = Repo(self.clone)
            self.opened = self.repo.branch_named("feature/a").open_in_worktree()
            _git(self.opened.root, "checkout", "-q", "--detach")
            _git(self.clone, "branch", "-q", "-D", "feature/a")

        with it("should refuse to open the branch onto that folder, naming the branch and the folder"):
            opening = lambda: self.repo.branch_named("feature/a").open_in_worktree()
            expect(opening).to(raise_error(WorktreeFolderTakenError, contain("feature/a", self.opened.root.name)))

    with context("with a folder that is no checkout where the branch's worktree goes"):
        with before.each:
            self.repo = Repo(self.clone)
            self.in_the_way = self.repo.worktrees.sibling_folder(self.repo.branch_named("feature/a"))
            self.in_the_way.mkdir()
            (self.in_the_way / "notes.txt").write_text("a person's own file\n", encoding="utf-8")

        with it("should refuse to open the branch onto it, naming the folder"):
            opening = lambda: self.repo.branch_named("feature/a").open_in_worktree()
            expect(opening).to(raise_error(WorktreeFolderTakenError, contain(self.in_the_way.name)))

        with it("should leave the folder's files as they were"):
            expect(lambda: self.repo.branch_named("feature/a").open_in_worktree()).to(raise_error(WorktreeFolderTakenError))
            expect((self.in_the_way / "notes.txt").is_file()).to(be_true)

    with context("with another branch whose name starts with the same 24 characters open in its worktree"):
        with before.each:
            self.repo = Repo(self.clone)
            self.monthly = self.repo.branch_named("customer-order-history-export-monthly").open_in_worktree()
            self.weekly = self.repo.branch_named("customer-order-history-export-weekly").open_in_worktree()

        with it("should open in a folder of its own"):
            expect(self.weekly.root).not_to(equal(self.monthly.root))

        with it("should have its own branch checked out there"):
            expect(_git(self.weekly.root, "branch", "--show-current")).to(equal("customer-order-history-export-weekly"))

    with context("that two callers open for one branch at the same moment"):
        with before.each:
            self.repo = Repo(self.clone)
            self.outcomes = []

            def open_it() -> None:
                try:
                    self.outcomes.append(self.repo.branch_named("feature/a").open_in_worktree().root)
                except Exception as failure:  # noqa: BLE001 - the example shows whatever either caller was answered
                    self.outcomes.append(failure)

            callers = [threading.Thread(target=open_it) for _ in range(3)]
            for caller in callers:
                caller.start()
            for caller in callers:
                caller.join()

        with it("should answer every caller the one worktree"):
            expect(self.outcomes).to(equal([self.repo.branch_named("feature/a").checkout.root] * 3))


with description("a branch on a clone") as self:
    with before.each:
        self.tmp = _REPOSITORIES.copy()
        self.origin, self.clone = self.tmp / "origin.git", self.tmp / "clone"

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with context("that origin has a copy of, with no upstream set, and a commit origin lacks"):
        with before.each:
            _git(self.clone, "checkout", "-q", "-b", "feature/a")
            _git(self.clone, "push", "-q", "origin", "feature/a")
            (self.clone / "work.txt").write_text("work\n", encoding="utf-8")
            _git(self.clone, "add", "work.txt")
            _git(self.clone, "commit", "-q", "-m", "work")

        with it("should need a push"):
            expect(Repo(self.clone).origin.needs_push()).to(be_true)


with description("a Repo and its checkouts") as self:
    with before.each:
        SPEC_RUN_HOME.ensure()
        self.tmp = _REPOSITORIES.copy()
        self.origin, self.clone = self.tmp / "origin.git", self.tmp / "clone"
        self.repo = Repo(self.clone)

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with it("should keep one git command line"):
        expect(self.repo.git).to(be(self.repo.git))

    with it("should keep one list of its worktrees"):
        expect(self.repo.worktrees).to(be(self.repo.worktrees))

    with it("should answer the branch it has checked out as a branch"):
        expect(self.repo.current_branch).to(equal(self.repo.branch_named("main")))

    with it("should be its own main clone"):
        expect(self.repo.main_clone).to(be(self.repo))

    with context("with a branch opened in a linked worktree"):
        with before.each:
            self.opened = self.repo.branch_named("feature/a").open_in_worktree()
            self.tree = self.opened.root
            self.linked = Repo(self.tree)

        with it("should list the worktree where git has it"):
            expect(self.repo.worktrees.at(self.tree).root).to(equal(self.tree.resolve()))

        with it("should answer the worktree's branch from its own checkout"):
            expect(self.repo.worktrees.at(self.tree).current_branch.repo.root).to(equal(self.tree.resolve()))

        with it("should find the main clone from the linked worktree"):
            expect(self.linked.main_clone.root).to(equal(self.clone.resolve()))

        with it("should list the main clone as the repository that lists it"):
            expect(self.repo.worktrees.at(self.clone)).to(be(self.repo))

        with it("should remove the worktree through the checkouts that listed it"):
            self.repo.worktrees.at(self.tree).close("close the worktree")
            expect(self.tree.exists()).to(be_false)
