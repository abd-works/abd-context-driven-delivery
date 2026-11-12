"""What a checkout's .git holds, read from its files, answers what git itself answers."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from space.repo.git_folder import GitFolder


def _git(folder: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=folder, capture_output=True, text=True).stdout.strip()


def _succeeds(folder: Path, *args: str) -> bool:
    return subprocess.run(["git", *args], cwd=folder, capture_output=True).returncode == 0


def _clone_with_history() -> Path:
    """A clone on main with two commits, a second branch, an origin, and its refs packed, as git gc leaves them."""
    top = Path(tempfile.mkdtemp(prefix="cdd-git-folder-")).resolve()
    clone = top / "clone"
    _git(top, "init", "-q", "-b", "main", str(clone))
    _git(clone, "config", "user.email", "spec@example.invalid")
    _git(clone, "config", "user.name", "Spec")
    for message in ("one", "two"):
        (clone / f"{message}.txt").write_text(message, encoding="utf-8")
        _git(clone, "add", "-A")
        _git(clone, "commit", "-q", "-m", message)
    _git(clone, "branch", "feature/pets")
    _git(clone, "remote", "add", "origin", str(top / "origin.git"))
    _git(clone, "pack-refs", "--all")
    _git(clone, "branch", "loose-one")
    return clone


with description("a checkout's git folder, read from its files"):
    with before.each:
        self.clone = _clone_with_history()
        self.folder = GitFolder(self.clone)

    with after.each:
        shutil.rmtree(self.clone.parent, ignore_errors=True)

    with it("should be readable"):
        expect(self.folder.is_readable).to(equal(True))

    with it("should name the branch checked out as git does"):
        expect(self.folder.head_branch()).to(equal(_git(self.clone, "rev-parse", "--abbrev-ref", "HEAD")))

    with it("should name the commit checked out as git does"):
        expect(self.folder.head_commit()).to(equal(_git(self.clone, "rev-parse", "HEAD")))

    with it("should list the branches git lists, packed and loose"):
        expect(self.folder.branch_names()).to(equal(_git(self.clone, "for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()))

    with it("should find a packed ref and a loose one, and not one that is missing"):
        found = [self.folder.has_ref(ref) for ref in ("refs/heads/feature/pets", "refs/heads/loose-one", "refs/heads/missing")]
        expect(found).to(equal([True, True, False]))

    with it("should know the origin git knows, and no other remote"):
        expect([self.folder.has_remote("origin"), self.folder.has_remote("upstream")]).to(equal([True, False]))

    with it("should list the checkout itself as the only worktree"):
        expect(self.folder.worktrees()).to(equal([(self.clone, "main")]))

    with context("that has a linked worktree"):
        with before.each:
            self.linked = self.clone.parent / "pets"
            _git(self.clone, "worktree", "add", "-q", str(self.linked), "feature/pets")

        with it("should list each worktree with its branch, the main clone first, as git does"):
            listed = [line.split(" ", 1)[1] for line in _git(self.clone, "worktree", "list", "--porcelain").splitlines() if line.startswith(("worktree ", "branch "))]
            expected = [(Path(listed[0]).resolve(), listed[1].removeprefix("refs/heads/")), (Path(listed[2]).resolve(), listed[3].removeprefix("refs/heads/"))]
            expect([(path.resolve(), branch) for path, branch in self.folder.worktrees()]).to(equal(expected))

        with it("should read the linked worktree's own branch from there"):
            expect(GitFolder(self.linked).head_branch()).to(equal("feature/pets"))

        with it("should read the repository's branches from the linked worktree too"):
            expect(GitFolder(self.linked).branch_names()).to(equal(self.folder.branch_names()))

    with context("that has HEAD detached at a commit"):
        with before.each:
            _git(self.clone, "checkout", "-q", "--detach")

        with it("should name no branch, as git says HEAD"):
            expect(self.folder.head_branch()).to(equal("HEAD"))

        with it("should say HEAD names no branch, as git symbolic-ref does"):
            expect(self.folder.is_on_branch()).to(equal(_succeeds(self.clone, "symbolic-ref", "-q", "HEAD")))

        with it("should still name the commit checked out"):
            expect(self.folder.head_commit()).to(equal(_git(self.clone, "rev-parse", "HEAD")))
