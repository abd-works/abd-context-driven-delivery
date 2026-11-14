"""A repository the domain specs work on without git: our Repo, Branch, and Worktrees, answered from memory."""
from __future__ import annotations

import hashlib
import re
import shutil
import threading
from pathlib import Path
from typing import Iterator

from space.repo.repo import SERVED_CHECKOUTS, Branch, Repo
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
        self.has_origin = False
        # Each branch's committed files, path from the top to the hash of its content, and its commit messages, newest last.
        self.trees: dict[str, dict[str, str]] = {}
        self.logs: dict[str, list[str]] = {}
        # The files a branch held when it was made, which tell what it changed since.
        self.forks: dict[str, dict[str, str]] = {}
        self.origin_trees: dict[str, dict[str, str]] = {}
        self.origin_logs: dict[str, list[str]] = {}
        # The branch each checkout has checked out, by the checkout's folder.
        self.checked_out: dict[Path, str] = {}
        self.calls: list[tuple[str, ...]] = []
        self.lock = threading.RLock()

    # --- What a spec seeds -------------------------------------------------------------------------------------------

    def make_clone(self) -> None:
        """The project as a checkout on main with every file it holds committed."""
        with self.lock:
            self.is_clone = True
            (self.root / ".git").mkdir(exist_ok=True)
            self.trees[self.default_branch] = {}
            self.logs[self.default_branch] = []
            self.checked_out[self.root] = self.default_branch
            self.commit(self.root, [self.root], "Fixture", untracked=True)
        self.serve(self.root)

    def add_origin(self) -> None:
        """An origin holding main as it is."""
        with self.lock:
            self.has_origin = True
            self.push(self.default_branch)

    def add_branch(self, name: str, at: str = "") -> None:
        """A branch made from at, the checked-out branch when none is named."""
        with self.lock:
            start = at or self.checked_out.get(self.root, self.default_branch)
            self.trees[name] = dict(self.trees.get(start, {}))
            self.logs[name] = list(self.logs.get(start, []))
            self.forks[name] = dict(self.trees[name])

    def add_worktree(self, branch: str, folder: Path) -> None:
        """branch checked out in a worktree at folder, made with the branch when it is new."""
        with self.lock:
            if branch not in self.trees:
                self.add_branch(branch)
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

    def has_branch(self, name: str) -> bool:
        return name in self.trees

    def origin_has_branch(self, name: str) -> bool:
        return name in self.origin_trees

    def worktrees(self) -> list[tuple[Path, str]]:
        """The main clone first, then each linked worktree, with the branch each has checked out."""
        linked = [(folder, branch) for folder, branch in self.checked_out.items() if folder != self.root]
        return [(self.root, self.branch_of(self.root)), *sorted(linked)]

    def uncommitted(self, checkout: Path, under: Path | None = None) -> list[str]:
        """The files in checkout, or under a folder of it, whose content its branch has not committed, as paths from the
        checkout's top; the files .gitignore names are not counted."""
        committed = self.trees.get(self.branch_of(checkout), {})
        return sorted(path for path, digest in _files(checkout, under or checkout).items() if committed.get(path) != digest)

    def changed_since_fork(self, branch: str) -> list[str]:
        """The files branch committed since it was made from the default branch."""
        fork, tree = self.forks.get(branch, {}), self.trees.get(branch, {})
        return sorted(path for path in tree if fork.get(path) != tree[path])

    # --- What the board does -----------------------------------------------------------------------------------------

    def commit(self, checkout: Path, paths: list[Path], message: str, *, untracked: bool) -> bool:
        """Commit the changes under paths on the branch checkout has checked out; false when there was nothing to
        commit. Without untracked, only files the branch already holds are committed."""
        with self.lock:
            branch = self.branch_of(checkout)
            tree = self.trees.setdefault(branch, {})
            changed = {path: digest for folder in paths for path, digest in _files(checkout, folder).items() if tree.get(path) != digest and (untracked or path in tree)}
            if not changed:
                return False
            tree.update(changed)
            self.logs.setdefault(branch, []).append(message)
            self.calls.append(("commit", branch, message))
            return True

    def push(self, branch: str) -> None:
        with self.lock:
            self.origin_trees[branch] = dict(self.trees.get(branch, {}))
            self.origin_logs[branch] = list(self.logs.get(branch, []))
            self.calls.append(("push", branch))

    def needs_push(self, branch: str) -> bool:
        return self.origin_logs.get(branch) != self.logs.get(branch, [])

    def check_out(self, checkout: Path, branch: str) -> None:
        with self.lock:
            if branch not in self.trees:
                self.add_branch(branch)
            self.checked_out[checkout] = branch
            self.calls.append(("check_out", branch))

    def merge(self, into: str, branch: str, message: str) -> None:
        """Merge branch into into: its committed files land on into, with one more commit."""
        with self.lock:
            self.trees.setdefault(into, {}).update(self.trees.get(branch, {}))
            self.logs.setdefault(into, []).append(message or f"merge {branch} into {into}")
            self.calls.append(("merge", branch, into))

    def delete_branch(self, name: str) -> None:
        with self.lock:
            self.trees.pop(name, None)
            self.logs.pop(name, None)
            self.calls.append(("delete_branch", name))
            if self.origin_trees.pop(name, None) is not None:
                self.origin_logs.pop(name, None)
                self.calls.append(("delete_origin_branch", name))

    def remove_worktree(self, folder: Path) -> None:
        with self.lock:
            self.checked_out.pop(folder, None)
            shutil.rmtree(folder, ignore_errors=True)
            self.calls.append(("remove_worktree", str(folder)))


class MockRepo(Repo):
    """Our Repo for one checkout of a *MockGit*: every question and command answered from memory, none by git."""

    def __init__(self, root: Path, held: MockGit) -> None:
        self.root = Path(root).resolve()
        self.default_branch = held.default_branch
        self.git = _NoGit()
        self.worktrees = MockWorktrees(self, held)
        self._from_top: dict[Path, str] = {}
        self._held = held

    @property
    def is_clone(self) -> bool:
        return self._held.is_clone

    def is_linked_worktree(self) -> bool:
        return self.root != self._held.root

    def primary_root(self) -> Path:
        return self._held.root

    @property
    def main_clone(self) -> Repo:
        return self if self.root == self._held.root else SERVED_CHECKOUTS.at(self._held.root)

    def checkout_at(self, folder: Path | str) -> Repo:
        return SERVED_CHECKOUTS.at(Path(folder).resolve())

    def branch_named(self, name: str) -> Branch:
        return MockBranch(self, name, self._held)

    @property
    def branches(self) -> list[Branch]:
        return [self.branch_named(name) for name in sorted(self._held.trees)] if self.is_clone else []

    @property
    def current_branch(self) -> Branch:
        return self.branch_named(self._held.branch_of(self.root))

    @property
    def is_on_branch(self) -> bool:
        return True

    @property
    def current_commit(self) -> str:
        log = self._held.logs.get(self._held.branch_of(self.root), [])
        return hashlib.sha1(f"{self.root}{len(log)}".encode()).hexdigest()

    @property
    def default_start_point(self) -> str:
        return self.default_branch

    def has_ref(self, ref: str) -> bool:
        if ref.startswith("refs/heads/"):
            return self._held.has_branch(ref.removeprefix("refs/heads/"))
        if ref.startswith("refs/remotes/origin/"):
            return self._held.origin_has_branch(ref.removeprefix("refs/remotes/origin/"))
        return False

    def worktree_listing(self) -> list[tuple[Path, str]]:
        return self._held.worktrees()

    def is_dirty(self, path: str | Path | None = None, *, untracked: bool = True) -> bool:
        return bool(self._held.uncommitted(self.root, Path(path) if path is not None else None))

    @property
    def is_merging(self) -> bool:
        return False

    def commit(self, paths: list[str], message: str, *, untracked: bool = False) -> str:
        self._held.commit(self.root, [Path(path) for path in paths], message, untracked=untracked)
        return self.current_commit

    @property
    def has_origin(self) -> bool:
        return self._held.has_origin

    def push_upstream(self) -> None:
        self._held.push(self._held.branch_of(self.root))

    def merge_origin_copy(self) -> None:
        return None

    def needs_push(self) -> bool:
        return self._held.needs_push(self._held.branch_of(self.root))

    def fetch(self) -> None:
        return None

    def merge_from(self, other: Branch, message: str = "") -> str:
        current = self._held.branch_of(self.root)
        if other.name != current:
            self._held.merge(current, other.name, message)
        return self.current_commit

    def prepare_merges(self) -> None:
        return None


class MockBranch(Branch):
    """Our Branch on a *MockRepo*: what git would hold for it, read and changed in the *MockGit*."""

    __slots__ = ("_held",)

    def __init__(self, repo: MockRepo, name: str, held: MockGit) -> None:
        super().__init__(repo, name)
        self._held = held

    @property
    def start_point(self) -> str:
        return self._repo.default_branch

    def changed_files(self) -> list[str]:
        if not self.exists:
            return []
        committed = self._held.changed_since_fork(self.name)
        if self._repo.current_branch != self:
            return committed
        return sorted({*committed, *self._held.uncommitted(self._repo.root)})

    def check_out(self) -> Branch:
        self._held.check_out(self._repo.root, self.name)
        return self

    def land_on_default(self) -> None:
        held = self._held
        default = held.default_branch
        held.check_out(held.root, default)
        held.merge(default, self.name, f"merge {self.name} into {default}")
        held.push(default)

    def delete(self, unmerged: bool = False) -> None:
        self._held.delete_branch(self.name)


class MockWorktrees(Worktrees):
    """Our Worktrees on a *MockRepo*: each worktree a real folder beside the main clone, so a chat can work in it, and
    the branch it has checked out kept in the *MockGit*."""

    def __init__(self, repo: MockRepo, held: MockGit) -> None:
        super().__init__(repo)
        self._held = held

    def __iter__(self) -> Iterator[Worktree]:
        for path, branch in self._held.worktrees():
            yield self._listed(path, branch)

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


def _files(checkout: Path, under: Path) -> dict[str, str]:
    """Every file under the folder under in checkout, by its path from checkout's top, with the hash of its content;
    what checkout's .gitignore names, and the .git marker, are left out, as git leaves them out."""
    ignored = _ignore_patterns(checkout)
    top = checkout.resolve()
    start = under.resolve()
    if start.is_file():
        candidates = [start]
    elif start.is_dir():
        candidates = [path for path in start.rglob("*") if path.is_file()]
    else:
        return {}
    found = {}
    for path in candidates:
        if not path.is_relative_to(top):
            continue
        relative = path.relative_to(top).as_posix()
        if relative.split("/", 1)[0] in _IGNORED_ALWAYS or any(pattern.search(relative) for pattern in ignored):
            continue
        found[relative] = hashlib.sha1(path.read_bytes()).hexdigest()
    return found


def _ignore_patterns(checkout: Path) -> list[re.Pattern[str]]:
    gitignore = checkout / ".gitignore"
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
