"""BDD spec — clearing the worktrees of a repository whose work is done, on a real repository with real worktrees."""
import os
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path

from expects import be_false, be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from space.repo.repo import Repo  # noqa: E402


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout.strip()


def _commit(root: Path, name: str) -> None:
    (root / name).write_text(name, encoding="utf-8")
    _git(root, "add", name)
    _git(root, "commit", "-q", "-m", name)


class _Workplace:
    """A main clone named ``clone`` with worktrees beside it, one for each way a worktree's work can stand, and the
    folders and records a hand clear-up leaves behind."""

    def __init__(self) -> None:
        self.top = Path(tempfile.mkdtemp(prefix="clear-worktrees-")).resolve()
        self.clone = self.top / "clone"
        self.clone.mkdir()
        _git(self.clone, "init", "-q", "-b", "main")
        _git(self.clone, "config", "user.email", "clear@test")
        _git(self.clone, "config", "user.name", "clear")
        (self.clone / ".gitignore").write_text(".sessions/\n", encoding="utf-8")
        _git(self.clone, "add", ".gitignore")
        _git(self.clone, "commit", "-q", "-m", "seed")

    def worktree(self, branch: str) -> Path:
        folder = self.top / f"clone-{branch}"
        _git(self.clone, "worktree", "add", "-q", "-b", branch, str(folder))
        return folder

    def merged(self, branch: str) -> Path:
        folder = self.worktree(branch)
        _commit(folder, f"{branch}.txt")
        _git(self.clone, "merge", "-q", "--no-ff", "-m", f"merge {branch}", branch)
        return folder

    def unmerged(self, branch: str) -> Path:
        folder = self.worktree(branch)
        _commit(folder, f"{branch}.txt")
        return folder

    def closed_session(self, name: str, branch: str) -> None:
        record = self.clone / ".sessions" / "_complete" / name
        record.mkdir(parents=True)
        (record / "session.json").write_text(f'{{"name": "{name}", "branch": "{branch}"}}', encoding="utf-8")

    def records(self) -> list[str]:
        held = self.clone / ".git" / "worktrees"
        return sorted(entry.name for entry in held.iterdir()) if held.is_dir() else []

    def remove(self) -> None:
        def writable(function, path, _info) -> None:
            os.chmod(path, stat.S_IWRITE)
            function(path)

        shutil.rmtree(self.top, onerror=writable)


def _reasons(listed) -> dict[str, str]:
    return {Path(cleared.folder).name: cleared.reason for cleared in listed}


with description("clearing the worktrees of a repository whose work is done") as self:
    with before.all:
        self.place = _Workplace()
        self.merged = self.place.merged("merged")
        self.closed = self.place.unmerged("closed")
        self.place.closed_session("closed-work", "closed")
        self.open = self.place.unmerged("open")
        self.dirty = self.place.merged("dirty")
        (self.dirty / "draft.txt").write_text("not committed", encoding="utf-8")
        self.current = self.place.merged("current")
        self.gone = self.place.worktree("gone")
        shutil.rmtree(self.gone)
        self.leftover = self.place.top / "clone-leftover"
        (self.leftover / "node_modules").mkdir(parents=True)
        (self.leftover / "node_modules" / "held.js").write_text("left behind", encoding="utf-8")
        os.chmod(self.leftover / "node_modules" / "held.js", stat.S_IREAD)
        self.own_clone = self.place.top / "clone-own"
        self.own_clone.mkdir()
        _git(self.own_clone, "init", "-q")
        self.cleared = Repo(self.current).clear_worktrees()
        self.removed = _reasons(self.cleared.removed)
        self.kept = _reasons(self.cleared.kept)

    with after.all:
        self.place.remove()

    with context("with a worktree whose branch is merged into main"):
        with it("should remove its folder"):
            expect(self.merged.exists()).to(be_false)

        with it("should say it was removed because its branch is merged into main"):
            expect(self.removed.get("clone-merged", "")).to(contain("merged into main"))

        with it("should keep its branch"):
            expect(_git(self.place.clone, "branch", "--list", "merged")).to(contain("merged"))

    with context("with a worktree whose branch has commits not on main"):
        with it("should keep its folder"):
            expect(self.open.is_dir()).to(be_true)

        with it("should say it was kept for its commits not on main"):
            expect(self.kept.get("clone-open", "")).to(contain("1 commit not on main"))

    with context("with a worktree whose session is closed but whose branch has commits not on main"):
        with it("should keep its folder"):
            expect(self.closed.is_dir()).to(be_true)

        with it("should say its session is closed and why it was kept"):
            expect(self.kept.get("clone-closed", "")).to(contain("session closed-work is closed"))

    with context("with a merged worktree holding work not committed"):
        with it("should keep its folder"):
            expect(self.dirty.is_dir()).to(be_true)

        with it("should say it holds work not committed"):
            expect(self.kept.get("clone-dirty", "")).to(contain("not committed"))

    with context("with the worktree the call is made from"):
        with it("should keep it, merged as it is"):
            expect(self.kept.get("clone-current", "")).to(contain("the worktree this call works in"))

    with context("with the main clone"):
        with it("should keep it"):
            expect(self.kept.get("clone", "")).to(contain("the main clone"))

    with context("with git's record of a worktree whose folder is gone"):
        with it("should delete the record"):
            expect(self.place.records()).to(equal(["clone-closed", "clone-current", "clone-dirty", "clone-open"]))

        with it("should say the record was removed because its folder is gone"):
            expect(self.removed.get("clone-gone", "")).to(contain("folder is gone"))

    with context("with a leftover folder beside the main clone that is no longer a worktree, holding a read-only file"):
        with it("should delete the folder"):
            expect(self.leftover.exists()).to(be_false)

        with it("should say it was no longer a worktree"):
            expect(self.removed.get("clone-leftover", "")).to(contain("no longer a worktree"))

    with context("with a clone of its own beside the main clone"):
        with it("should keep it"):
            expect(self.own_clone.is_dir()).to(be_true)

        with it("should say it is a repository of its own"):
            expect(self.kept.get("clone-own", "")).to(contain("a repository of its own"))

    with context("with what it did put in words"):
        with it("should name each folder it removed and each it kept, with why"):
            expect(self.cleared.report).to(contain("Removed", "Kept", "clone-merged", "clone-open"))
