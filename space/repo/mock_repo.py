"""A repository the domain specs work on without git: our Repo, Branch, and Worktrees, answered from memory."""
from __future__ import annotations

import hashlib
import re
import shutil
import threading
from pathlib import Path
from typing import Iterator

from space.repo.origin import Merges, Origin
from space.repo.repo import SERVED_CHECKOUTS, Branch, Publishing, Refs, Repo, WorkingTree
from space.repo.worktree import Worktree, Worktrees

_IGNORED_ALWAYS = (".git",)


class MockGitUsed(AssertionError):
    """Raised when code reaches for the git command line of a mocked repository: every git question the board asks has
    to go through Repo, Branch, or Worktrees, which the mock answers."""

    def __init__(self, args: tuple[str, ...]) -> None:
        super().__init__(f"a mocked repository was asked to run git {' '.join(args)}; answer it through Repo, Branch, or Worktrees")


class _NoGit:
    def run(self, *args: str, **_: object) -> str:
        raise MockGitUsed(args)

    def succeeds(self, *args: str) -> bool:
        raise MockGitUsed(args)


class HeldTrees:
    """Branches a *MockGit* keeps, each with the content of every file it committed and its commit messages: the
    branches themselves (*HeldBranches*) and their copies on origin (*HeldOrigin*)."""

    def __init__(self, held: MockGit) -> None:
        self._held = held
        # Each branch's committed files, path from the top to the hash of its content, and its commit messages, newest last.
        self.trees: dict[str, dict[str, str]] = {}
        self.logs: dict[str, list[str]] = {}

    def has(self, name: str) -> bool:
        return name in self.trees

    def _take(self, name: str, source: HeldTrees, source_name: str) -> None:
        """name holds, from now on, a copy of the files and commit messages source holds for source_name."""
        self.trees[name] = dict(source.trees.get(source_name, {}))
        self.logs[name] = list(source.logs.get(source_name, []))

    def _drop(self, name: str) -> bool:
        """Forget the branch called name; whether it was held."""
        self.logs.pop(name, None)
        return self.trees.pop(name, None) is not None


class HeldOrigin(HeldTrees):
    """The origin a *MockGit* keeps: each branch pushed to it, with its files and commit messages as they were pushed."""

    def __init__(self, held: MockGit) -> None:
        super().__init__(held)
        self.is_present = False

    def add(self) -> None:
        """An origin holding main as it is."""
        with self._held.lock:
            self.is_present = True
            self.push(self._held.default_branch)

    def push(self, branch: str) -> None:
        held = self._held
        with held.lock:
            self._take(branch, held.branches, branch)
            held.calls.append(("push", branch))

    def needs_push(self, branch: str) -> bool:
        return self.logs.get(branch) != self._held.branches.logs.get(branch, [])

    def delete_branch(self, name: str) -> None:
        with self._held.lock:
            if self._drop(name):
                self._held.calls.append(("delete_origin_branch", name))


class HeldBranches(HeldTrees):
    """The branches a *MockGit* keeps, and what each held when it was made; and the commands that change them, each
    recorded in the *MockGit*'s ``calls``."""

    def __init__(self, held: MockGit) -> None:
        super().__init__(held)
        # The files a branch held when it was made, which tell what it changed since.
        self.forks: dict[str, dict[str, str]] = {}

    def add(self, name: str, start_point: str = "") -> None:
        """A branch made from start_point, the main clone's checked-out branch when none is named."""
        held = self._held
        with held.lock:
            self._take(name, self, start_point or held.branch_of(held.root))
            self.forks[name] = dict(self.trees[name])

    def changed_since_fork(self, branch: str) -> list[str]:
        """The files branch committed since it was made from the default branch."""
        fork, tree = self.forks.get(branch, {}), self.trees.get(branch, {})
        return sorted(path for path in tree if fork.get(path) != tree[path])

    def record_commit(self, branch: str, changed: dict[str, str], message: str) -> None:
        """changed, each file's path from the top with the hash of its content, committed on branch with message."""
        with self._held.lock:
            self.trees.setdefault(branch, {}).update(changed)
            self.logs.setdefault(branch, []).append(message)
            self._held.calls.append(("commit", branch, message))

    def merge(self, into: str, branch: str, message: str) -> None:
        """Merge branch into into: its committed files land on into, with one more commit."""
        with self._held.lock:
            self.trees.setdefault(into, {}).update(self.trees.get(branch, {}))
            self.logs.setdefault(into, []).append(message or f"merge {branch} into {into}")
            self._held.calls.append(("merge", branch, into))

    def delete(self, name: str) -> None:
        with self._held.lock:
            self._drop(name)
            self._held.calls.append(("delete_branch", name))
            self._held.origin.delete_branch(name)


class MockGit:
    """*MockGit* is what git would hold for one throwaway project, kept in memory: its branches, which one each checkout
    has checked out, the worktrees beside it, an origin, and, for each branch, the commit messages and the content of
    every file it committed. It records every command the board gives it (``calls``), so a spec can check the board
    gave the right one, and answers the questions the board asks the way git would for those commands.

    It is a clone only once a spec makes it one (``make_clone``); before that, as with a folder git does not know, the
    board finds no branches."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.default_branch = "main"
        self.is_clone = False
        # The branch each checkout has checked out, by the checkout's folder.
        self.checked_out: dict[Path, str] = {}
        self.calls: list[tuple[str, ...]] = []
        self.lock = threading.RLock()
        self.origin = HeldOrigin(self)
        self.branches = HeldBranches(self)

    # --- What a spec seeds -------------------------------------------------------------------------------------------

    def make_clone(self) -> None:
        """The project as a checkout on main with every file it holds committed."""
        with self.lock:
            self.is_clone = True
            (self.root / ".git").mkdir(exist_ok=True)
            self.branches.trees[self.default_branch] = {}
            self.branches.logs[self.default_branch] = []
            self.checked_out[self.root] = self.default_branch
            self.serve(self.root).working_tree.commit([str(self.root)], "Fixture", untracked=True)

    def add_worktree(self, branch: str, folder: Path) -> None:
        """branch checked out in a worktree at folder, made with the branch when it is new."""
        with self.lock:
            if not self.branches.has(branch):
                self.branches.add(branch)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / ".git").write_text(f"gitdir: {self.root / '.git' / 'worktrees' / folder.name}\n", encoding="utf-8")
            self.checked_out[folder.resolve()] = branch
        self.serve(folder.resolve())

    def serve(self, folder: Path) -> MockRepo:
        """The mocked repository of the checkout at folder, held where the board finds every checkout's repository."""
        return SERVED_CHECKOUTS.serve(MockRepo(folder, self))

    # --- What the board asks ----------------------------------------------------------------------------------------

    def branch_of(self, checkout: Path) -> str:
        return self.checked_out.get(checkout, self.default_branch)

    def worktrees(self) -> list[tuple[Path, str]]:
        """The main clone first, then each linked worktree, with the branch each has checked out."""
        linked = [(folder, branch) for folder, branch in self.checked_out.items() if folder != self.root]
        return [(self.root, self.branch_of(self.root)), *sorted(linked)]

    # --- What the board does -----------------------------------------------------------------------------------------

    def check_out(self, checkout: Path, branch: str) -> None:
        with self.lock:
            if not self.branches.has(branch):
                self.branches.add(branch)
            self.checked_out[checkout] = branch
            self.calls.append(("check_out", branch))

    def remove_worktree(self, folder: Path) -> None:
        with self.lock:
            self.checked_out.pop(folder, None)
            shutil.rmtree(folder, ignore_errors=True)
            self.calls.append(("remove_worktree", str(folder)))


class MockRepo(Repo):
    """Our Repo for one checkout of a *MockGit*: every question and command answered from memory, none by git."""

    def __init__(self, root: Path, held: MockGit) -> None:
        self._held = held
        self.root = Path(root).resolve()
        self.git = _NoGit()
        self.worktrees = MockWorktrees(self, SERVED_CHECKOUTS)
        self.refs = MockRefs(self)
        self.working_tree = MockWorkingTree(self)
        self.origin = MockOrigin(self)
        self.merges = MockMerges(self)
        self.publishing = Publishing(self)
        self._from_top: dict[Path, str] = {}
        self.writing_index = held.lock

    @property
    def held(self) -> MockGit:
        """What git would hold for this checkout's repository, kept in memory."""
        return self._held

    @property
    def default_branch(self) -> str:
        return self._held.default_branch

    @property
    def is_clone(self) -> bool:
        return self._held.is_clone

    @property
    def is_linked_worktree(self) -> bool:
        return self.root != self._held.root

    @property
    def main_clone(self) -> Repo:
        return self if self.root == self._held.root else SERVED_CHECKOUTS.at(self._held.root)

    def branch_named(self, name: str) -> Branch:
        return MockBranch(self, name)

    @property
    def branches(self) -> list[Branch]:
        return [self.branch_named(name) for name in sorted(self._held.branches.trees)] if self.is_clone else []

    @property
    def current_branch(self) -> Branch:
        return self.branch_named(self._held.branch_of(self.root))

    @property
    def is_on_branch(self) -> bool:
        return True

    @property
    def current_commit(self) -> str:
        log = self._held.branches.logs.get(self._held.branch_of(self.root), [])
        return hashlib.sha1(f"{self.root}{len(log)}".encode()).hexdigest()

    @property
    def default_start_point(self) -> str:
        return self.default_branch

    @property
    def has_origin(self) -> bool:
        return self._held.origin.is_present

    @property
    def head_message(self) -> str:
        log = self._held.branches.logs.get(self._held.branch_of(self.root), [])
        return log[-1] if log else ""


class MockRefs(Refs):
    """Our Refs on a *MockRepo*: a branch's ref is there when the *MockGit* or its origin holds the branch."""

    _repo: MockRepo

    def has(self, ref: str) -> bool:
        held = self._repo.held
        if ref.startswith("refs/heads/"):
            return held.branches.has(ref.removeprefix("refs/heads/"))
        if ref.startswith("refs/remotes/origin/"):
            return held.origin.has(ref.removeprefix("refs/remotes/origin/"))
        return False


class MockWorkingTree(WorkingTree):
    """Our WorkingTree on a *MockRepo*: the files in the checkout compared with what its branch committed in the
    *MockGit*."""

    _repo: MockRepo

    def is_dirty(self, path: str | Path | None = None, *, untracked: bool = True) -> bool:
        return bool(self.uncommitted(Path(path) if path is not None else None))

    @property
    def is_merging(self) -> bool:
        return False

    def commit(self, paths: list[str], message: str, *, untracked: bool = False) -> str:
        """Commit the changes under paths on the branch this checkout has checked out. Without untracked, only files the
        branch already holds are committed."""
        held = self._repo.held
        with held.lock:
            tree = held.branches.trees.get(held.branch_of(self._repo.root), {})
            changed = {path: digest for folder in paths for path, digest in self._files(Path(folder)).items() if tree.get(path) != digest and (untracked or path in tree)}
            if changed:
                held.branches.record_commit(held.branch_of(self._repo.root), changed, message)
        return self._repo.current_commit

    def uncommitted(self, under: Path | None = None) -> list[str]:
        """The files in this checkout, or under a folder of it, whose content its branch has not committed, as paths
        from the checkout's top; the files .gitignore names are not counted."""
        held = self._repo.held
        committed = held.branches.trees.get(held.branch_of(self._repo.root), {})
        return sorted(path for path, digest in self._files(under or self._repo.root).items() if committed.get(path) != digest)

    def _files(self, under: Path) -> dict[str, str]:
        """Every file under the folder under in this checkout, by its path from the checkout's top, with the hash of its
        content; what the checkout's .gitignore names, and the .git marker, are left out, as git leaves them out."""
        ignored = self._ignore_patterns()
        found = {}
        for path in self._files_at(under.resolve()):
            if not path.is_relative_to(self._repo.root):
                continue
            relative = path.relative_to(self._repo.root).as_posix()
            if relative.split("/", 1)[0] in _IGNORED_ALWAYS or any(pattern.search(relative) for pattern in ignored):
                continue
            found[relative] = hashlib.sha1(path.read_bytes()).hexdigest()
        return found

    def _ignore_patterns(self) -> list[re.Pattern[str]]:
        gitignore = self._repo.root / ".gitignore"
        if not gitignore.is_file():
            return []
        patterns = []
        for line in gitignore.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith(("#", "!")):
                continue
            body = re.escape(line.strip("/")).replace(r"\*\*/", "(?:.*/)?").replace(r"\*", "[^/]*")
            anchored = "^" if "/" in line.strip("/") else "(?:^|/)"
            patterns.append(re.compile(f"{anchored}{body}(?:/|$)"))
        return patterns

    def _files_at(self, start: Path) -> list[Path]:
        """The file start names, or every file under the folder it names; none when nothing is there."""
        if start.is_file():
            return [start]
        if start.is_dir():
            return [path for path in start.rglob("*") if path.is_file()]
        return []


class MockOrigin(Origin):
    """Our Origin on a *MockRepo*: the origin the *MockGit* keeps, which takes every push."""

    def push_upstream(self) -> None:
        self._repo.held.origin.push(self._repo.held.branch_of(self._repo.root))

    def merge_copy(self) -> None:
        return None

    def needs_push(self) -> bool:
        return self._repo.held.origin.needs_push(self._repo.held.branch_of(self._repo.root))

    def fetch(self) -> None:
        return None


class MockMerges(Merges):
    """Our Merges on a *MockRepo*: a branch's commits merged in the *MockGit*."""

    def merge_from(self, other: Branch, message: str = "") -> str:
        current = self._repo.held.branch_of(self._repo.root)
        if other.name != current:
            self._repo.held.branches.merge(current, other.name, message)
        return self._repo.current_commit

    def prepare(self) -> None:
        return None


class MockBranch(Branch):
    """Our Branch on a *MockRepo*: what git would hold for it, read and changed in the *MockGit*."""

    __slots__ = ()

    _repo: MockRepo

    @property
    def start_point(self) -> str:
        return self._repo.default_branch

    def changed_files(self) -> list[str]:
        if not self.exists:
            return []
        committed = self._repo.held.branches.changed_since_fork(self.name)
        if self._repo.current_branch != self:
            return committed
        return sorted({*committed, *self._repo.working_tree.uncommitted()})

    def check_out(self) -> Branch:
        self._repo.held.check_out(self._repo.root, self.name)
        return self

    def delete(self, unmerged: bool = False) -> None:
        self._repo.held.branches.delete(self.name)


class MockWorktrees(Worktrees):
    """Our Worktrees on a *MockRepo*: each worktree a real folder beside the main clone, so a chat can work in it, and
    the branch it has checked out kept in the *MockGit*."""

    _repo: MockRepo

    @property
    def _held(self) -> MockGit:
        return self._repo.held

    def __iter__(self) -> Iterator[Worktree]:
        for path, branch in self._held.worktrees():
            yield self._listed(path, branch)

    def listing(self) -> list[tuple[Path, str]]:
        return self._held.worktrees()

    def primary_root(self) -> Path:
        return self._held.root

    def add(self, path: str | Path, branch: Branch) -> Worktree:
        existing = self.of(branch)
        if existing is not None:
            return existing
        dest = Path(path).resolve()
        self._held.add_worktree(branch.name, dest)
        self._held.calls.append(("add_worktree", branch.name, str(dest)))
        return self._listed(dest, branch.name)

    def remove(self, worktree: Worktree) -> None:
        self._held.remove_worktree(worktree.path)
