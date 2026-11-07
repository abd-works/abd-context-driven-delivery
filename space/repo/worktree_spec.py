"""BDD spec — a worktree opened for a branch, and whether it is up to date with origin."""
import shutil
import subprocess
import tempfile
from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from space.repo.repo import Repo  # noqa: E402
from space.work_state import WorkState  # noqa: E402


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

        with context("that has been opened through the repo toolset"):
            with before.each:
                self.reply = Repo(self.clone).switch_worktree("feature/a")

            with it("should say in its reply that it was not updated from origin"):
                expect(self.reply).to(contain("not updated from origin"))

            with it("should still open the worktree folder"):
                expect(WorkState(self.clone).worktree.path.is_dir()).to(be_true)
