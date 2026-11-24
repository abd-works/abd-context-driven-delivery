"""What a checkout's git holds for a lookup: which branch is checked out, which commit, which refs and branches, whether
there is an origin, and which worktrees there are. *GitFolder* reads the answers from the checkout's ``.git`` files;
*AskedOfGit* asks the git command line, for a checkout whose refs only git reads. Both answer the one *GitFacts*
interface, so a caller never chooses between them at the place it asks."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path

from harness.git.git import Git, RepoConnectError

_SYMBOLIC = "ref: "
_HEADS = "refs/heads/"
_REMOTE_SECTION = re.compile(r'^\s*\[remote\s+"([^"]+)"\]\s*$')
_SECTION = re.compile(r"^\s*\[")
_URL = re.compile(r"^\s*url\s*=\s*(.+?)\s*$")
_REFTABLE = re.compile(r"^\s*refstorage\s*=\s*reftable\s*$", re.IGNORECASE)


class GitFacts(ABC):
    """The facts a checkout's git holds, each answered as git itself answers it."""

    @abstractmethod
    def head_branch(self) -> str:
        """The branch checked out, as ``git rev-parse --abbrev-ref HEAD`` names it: ``HEAD`` when none is."""

    @abstractmethod
    def is_on_branch(self) -> bool:
        """Whether HEAD names a branch, as ``git symbolic-ref -q HEAD`` says; false when HEAD is detached at a commit."""

    @abstractmethod
    def head_commit(self) -> str:
        """The commit checked out; empty in a repository with no commit yet."""

    @abstractmethod
    def has_ref(self, ref: str) -> bool:
        """Whether the full ref, such as ``refs/heads/main`` or ``refs/remotes/origin/main``, names a commit."""

    @abstractmethod
    def branch_names(self) -> list[str]:
        """Every local branch, sorted as ``git for-each-ref refs/heads`` lists them."""

    @abstractmethod
    def has_remote(self, name: str) -> bool:
        """Whether the repository names a URL for the remote called name, as ``git remote get-url`` would answer."""

    @abstractmethod
    def worktrees(self) -> list[tuple[Path, str]]:
        """Every checkout of the repository with the branch it has checked out (empty when detached), the main clone
        first, as ``git worktree list`` lists them."""

    @abstractmethod
    def common_folder(self) -> Path:
        """The git folder that keeps the refs, config and worktrees: the main clone's ``.git``."""

    @abstractmethod
    def is_merging(self) -> bool:
        """Whether a merge is going on in this checkout, as ``git rev-parse -q --verify MERGE_HEAD`` says: the next
        commit concludes it with everything staged."""


class GitFolder(GitFacts):
    """*GitFolder* answers a checkout's facts from the files of its ``.git``, because the board and the sessions ask them
    many times in one read and starting git costs about 40 ms on Windows however small the question: ``HEAD``, a ref's
    file or its line in ``packed-refs``, the ``[remote]`` section of ``config``, and each linked worktree's folder under
    ``worktrees``.

    A linked worktree's ``.git`` is a file naming its own git folder, which holds its ``HEAD``; its refs, config and
    worktree list are in the git folder the main clone keeps (``commondir``). ``is_readable`` is false for a checkout
    whose refs git keeps in a reftable, which only git reads; its *Checkout* then asks git."""

    def __init__(self, checkout: Path) -> None:
        self._checkout = checkout

    @property
    def checkout(self) -> Path:
        """The top folder of the checkout this git folder belongs to."""
        return self._checkout

    def main_checkout(self) -> Path:
        """The repository's main checkout. A linked worktree's ``.git`` is a file naming its git folder, whose
        ``commondir`` leads back to the main checkout's ``.git``; any other checkout is its own main checkout."""
        own = self._own_folder()
        if own is None or not self._checkout.joinpath(".git").is_file() or not (own / "commondir").is_file():
            return self._checkout
        return self.common_folder().parent

    @property
    def is_readable(self) -> bool:
        """Whether the checkout's refs are files this reads: a git folder with a HEAD, refs not kept in a reftable."""
        own = self._own_folder()
        if own is None or not (own / "HEAD").is_file():
            return False
        config = self.common_folder() / "config"
        return not (config.is_file() and any(_REFTABLE.match(line) for line in config.read_text(encoding="utf-8").splitlines()))

    def head_branch(self) -> str:
        head = self._head()
        return head.removeprefix(_SYMBOLIC).removeprefix(_HEADS) if head.startswith(_SYMBOLIC + _HEADS) else "HEAD"

    def is_on_branch(self) -> bool:
        return self._head().startswith(_SYMBOLIC)

    def head_commit(self) -> str:
        head = self._head()
        return self.commit_of(head.removeprefix(_SYMBOLIC)) if head.startswith(_SYMBOLIC) else head

    def has_ref(self, ref: str) -> bool:
        return bool(self.commit_of(ref))

    def commit_of(self, ref: str) -> str:
        """The commit the full ref names: its file under the common git folder, else its line in ``packed-refs``."""
        common = self.common_folder()
        loose = common / ref
        if loose.is_file():
            return loose.read_text(encoding="utf-8").strip()
        return self._packed().get(ref, "")

    def branch_names(self) -> list[str]:
        heads = self.common_folder() / "refs" / "heads"
        loose = {path.relative_to(heads).as_posix() for path in heads.rglob("*") if path.is_file()} if heads.is_dir() else set()
        packed = {ref.removeprefix(_HEADS) for ref in self._packed() if ref.startswith(_HEADS)}
        return sorted(loose | packed)

    def has_remote(self, name: str) -> bool:
        config = self.common_folder() / "config"
        if not config.is_file():
            return False
        section = ""
        for line in config.read_text(encoding="utf-8").splitlines():
            section = self._remote_section_after(line, section)
            if section == name and _URL.match(line):
                return True
        return False

    def _remote_section_after(self, line: str, section: str) -> str:
        """The remote whose config section line is in: the one a remote header names, none after any other header,
        else the section it was already in."""
        remote = _REMOTE_SECTION.match(line)
        if remote:
            return remote.group(1)
        return "" if _SECTION.match(line) else section

    def worktrees(self) -> list[tuple[Path, str]]:
        common = self.common_folder()
        listed = [(common.parent, GitFolder(common.parent).head_branch())]
        linked = common / "worktrees"
        for folder in sorted(linked.iterdir()) if linked.is_dir() else []:
            gitdir = folder / "gitdir"
            if not gitdir.is_file():
                continue
            checkout = Path(gitdir.read_text(encoding="utf-8").strip()).parent
            listed.append((checkout, self._branch_in(folder)))
        return [(path, "" if branch == "HEAD" else branch) for path, branch in listed]

    def _branch_in(self, git_folder: Path) -> str:
        head = (git_folder / "HEAD").read_text(encoding="utf-8").strip() if (git_folder / "HEAD").is_file() else ""
        return head.removeprefix(_SYMBOLIC).removeprefix(_HEADS) if head.startswith(_SYMBOLIC + _HEADS) else ""

    def is_merging(self) -> bool:
        own = self._own_folder()
        return own is not None and (own / "MERGE_HEAD").is_file()

    def _head(self) -> str:
        own = self._own_folder()
        return (own / "HEAD").read_text(encoding="utf-8").strip() if own is not None and (own / "HEAD").is_file() else ""

    def _own_folder(self) -> Path | None:
        """The checkout's own git folder: its .git folder, or the folder a linked worktree's .git file names."""
        marker = self._checkout / ".git"
        if marker.is_dir():
            return marker
        if marker.is_file():
            named = marker.read_text(encoding="utf-8").split("gitdir:", 1)[-1].strip()
            return (self._checkout / named).resolve()
        return None

    def common_folder(self) -> Path:
        own = self._own_folder()
        if own is None:
            return self._checkout / ".git"
        common = own / "commondir"
        return (own / common.read_text(encoding="utf-8").strip()).resolve() if common.is_file() else own

    def _packed(self) -> dict[str, str]:
        packed = self.common_folder() / "packed-refs"
        if not packed.is_file():
            return {}
        found: dict[str, str] = {}
        for line in packed.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith(("#", "^")):
                continue
            commit, _, ref = line.partition(" ")
            found[ref.strip()] = commit
        return found


class AskedOfGit(GitFacts):
    """*AskedOfGit* answers a checkout's facts by running git, for a checkout whose refs git keeps where only git reads
    them, such as a reftable, or a folder that is no clone, where each question fails or answers nothing as git does."""

    def __init__(self, git: Git) -> None:
        self._git = git

    def head_branch(self) -> str:
        return self._git.run("rev-parse", "--abbrev-ref", "HEAD")

    def is_on_branch(self) -> bool:
        return self._git.succeeds("symbolic-ref", "-q", "HEAD")

    def head_commit(self) -> str:
        return self._git.run("rev-parse", "HEAD")

    def has_ref(self, ref: str) -> bool:
        return self._git.succeeds("show-ref", "--verify", "--quiet", ref)

    def branch_names(self) -> list[str]:
        listed = self._git.run("for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
        return [name for name in listed if name.strip()]

    def has_remote(self, name: str) -> bool:
        return self._git.succeeds("remote", "get-url", name)

    def worktrees(self) -> list[tuple[Path, str]]:
        listed = []
        for block in self._git.run("worktree", "list", "--porcelain").split("\n\n"):
            fields = dict(line.split(" ", 1) for line in block.splitlines() if " " in line)
            if "worktree" in fields:
                listed.append((Path(fields["worktree"]), fields.get("branch", "").removeprefix(_HEADS)))
        return listed

    def common_folder(self) -> Path:
        named = Path(self._git.run("rev-parse", "--git-common-dir"))
        return (named if named.is_absolute() else self._git.folder / named).resolve()

    def is_merging(self) -> bool:
        return self._git.succeeds("rev-parse", "-q", "--verify", "MERGE_HEAD")


class NoGitFacts(GitFacts):
    """The facts of a folder that is no clone: no branch, no commit, no ref, no origin, and no worktree. Asking git there
    would only fail."""

    def __init__(self, folder: Path) -> None:
        self._folder = folder

    def head_branch(self) -> str:
        raise RepoConnectError(f"Cannot connect git: {self._folder} is not a git checkout.")

    def is_on_branch(self) -> bool:
        return False

    def head_commit(self) -> str:
        raise RepoConnectError(f"Cannot connect git: {self._folder} is not a git checkout.")

    def has_ref(self, ref: str) -> bool:
        return False

    def branch_names(self) -> list[str]:
        return []

    def has_remote(self, name: str) -> bool:
        return False

    def worktrees(self) -> list[tuple[Path, str]]:
        return []

    def common_folder(self) -> Path:
        return self._folder / ".git"

    def is_merging(self) -> bool:
        return False
