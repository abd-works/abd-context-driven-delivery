"""BDD spec — a worktree opened for a branch, and whether it is up to date with origin."""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from expects import be, be_false, be_none, be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from space.repo.repo import Repo  # noqa: E402


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def _clone_with_origin(root: Path) -> tuple[Path, Path]:
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
    return origin, clone


with description("a worktree opened for a branch") as self:
    with before.each:
        self.tmp = Path(tempfile.mkdtemp(prefix="worktree-spec-"))
        self.origin, self.clone = _clone_with_origin(self.tmp)

    with after.each:
        shutil.rmtree(self.tmp, ignore_errors=True)

    with context("with origin reachable"):
        with before.each:
            self.opened = Repo(self.clone).branch_named("feature/a").open_in_worktree()

        with it("should be up to date with origin"):
            expect(self.opened.sync_failure).to(equal(""))

    with context("with origin no longer reachable"):
        with before.each:
            _git(self.clone, "remote", "set-url", "origin", str(self.tmp / "moved-away.git"))

        with context("that has been opened"):
            with before.each:
                self.opened = Repo(self.clone).branch_named("feature/a").open_in_worktree()

            with it("should check the branch out"):
                expect(_git(self.opened.path, "branch", "--show-current")).to(equal("feature/a"))

            with it("should say why it is not up to date with origin"):
                expect(self.opened.sync_failure).to(contain("fetch"))

            with it("should still open the worktree folder"):
                expect(self.opened.path.is_dir()).to(be_true)

    with context("whose folder holds files past Windows' 260-character path limit"):
        with before.each:
            self.opened = Repo(self.clone).branch_named("feature/a").open_in_worktree()
            self.worktrees = Repo(self.clone).worktrees
            deep = self.opened.path.resolve().joinpath(".retired", *("fixture-folder-" * 4 for _ in range(5)))
            long_deep = f"\\\\?\\{deep}" if os.name == "nt" else str(deep)
            os.makedirs(long_deep, exist_ok=True)
            Path(long_deep, "fixture.md").write_text("retired", encoding="utf-8")

        with it("should remove the folder"):
            self.worktrees.remove(self.opened)
            expect(self.opened.path.exists()).to(be_false)

    with context("whose folder a running program holds open"):
        with before.each:
            self.opened = Repo(self.clone).branch_named("feature/a").open_in_worktree()
            self.worktrees = Repo(self.clone).worktrees
            # Stands in for a checkout a running program holds open: every way of deleting the folder leaves it there.
            self.worktrees._rmtree_logged = lambda folder: None
            self.worktrees._force_remove_directory_windows = lambda folder: False

        with it("should leave git no longer listing the worktree"):
            self.worktrees.remove(self.opened)
            expect(Repo(self.clone).branch_named("feature/a").worktree).to(be_none)


with description("a branch on a clone") as self:
    with before.each:
        self.tmp = Path(tempfile.mkdtemp(prefix="branch-spec-"))
        self.origin, self.clone = _clone_with_origin(self.tmp)

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
            expect(Repo(self.clone).needs_push()).to(be_true)


with description("a Repo and its checkouts") as self:
    with before.each:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo-parts-spec-"))
        self.origin, self.clone = _clone_with_origin(self.tmp)
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
            self.tree = self.opened.path
            self.linked = Repo(self.tree)

        with it("should list the worktree where git has it"):
            expect(self.repo.worktrees.at(self.tree).path).to(equal(self.tree.resolve()))

        with it("should answer the worktree's branch from its own checkout"):
            expect(self.repo.worktrees.at(self.tree).branch.repo.root).to(equal(self.tree.resolve()))

        with it("should find the main clone from the linked worktree"):
            expect(self.linked.main_clone.root).to(equal(self.clone.resolve()))

        with it("should list the main clone with the repository that lists it"):
            listed = self.repo.worktrees.at(self.clone)
            expect(listed.repository).to(be(self.repo))

        with it("should remove the worktree through the checkouts that listed it"):
            self.repo.worktrees.at(self.tree).close("close the worktree")
            expect(self.tree.exists()).to(be_false)
