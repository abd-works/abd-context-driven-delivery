"""What a checkout's .git holds for a lookup, read from its files rather than by starting git."""
from __future__ import annotations

import re
from pathlib import Path

_SYMBOLIC = "ref: "
_HEADS = "refs/heads/"
_REMOTE_SECTION = re.compile(r'^\s*\[remote\s+"([^"]+)"\]\s*$')
_SECTION = re.compile(r"^\s*\[")
_URL = re.compile(r"^\s*url\s*=\s*(.+?)\s*$")
_REFTABLE = re.compile(r"^\s*refstorage\s*=\s*reftable\s*$", re.IGNORECASE)


class GitFolder:
    """*GitFolder* answers the questions the board and the sessions ask of a checkout many times in one read: which
    branch is checked out, which commit it is on, whether a ref or a branch exists, whether there is an origin, and which
    worktrees there are. Starting git costs about 40 ms on Windows however small the question, and these answers are
    small files in the checkout's ``.git``: ``HEAD``, a ref's file or its line in ``packed-refs``, the ``[remote]``
    section of ``config``, and each linked worktree's folder under ``worktrees``.

    A linked worktree's ``.git`` is a file naming its own git folder, which holds its ``HEAD``; its refs, config and
    worktree list are in the git folder the main clone keeps (``commondir``). ``is_readable`` is false for a checkout
    whose refs git keeps in a reftable, which only git reads; its repository then asks git."""

    def __init__(self, checkout: Path) -> None:
        self._checkout = checkout

    @property
    def is_readable(self) -> bool:
        """Whether the checkout's refs are files this reads: a git folder with a HEAD, refs not kept in a reftable."""
        own = self._own_folder()
        if own is None or not (own / "HEAD").is_file():
            return False
        config = self._common_folder() / "config"
        return not (config.is_file() and any(_REFTABLE.match(line) for line in config.read_text(encoding="utf-8").splitlines()))

    def head_branch(self) -> str:
        """The branch checked out, as ``git rev-parse --abbrev-ref HEAD`` names it: ``HEAD`` when none is."""
        head = self._head()
        return head.removeprefix(_SYMBOLIC).removeprefix(_HEADS) if head.startswith(_SYMBOLIC + _HEADS) else "HEAD"

    def is_on_branch(self) -> bool:
        """Whether HEAD names a branch, as ``git symbolic-ref -q HEAD`` says; false when HEAD is detached at a commit."""
        return self._head().startswith(_SYMBOLIC)

    def head_commit(self) -> str:
        """The commit checked out; empty in a repository with no commit yet."""
        head = self._head()
        return self.commit_of(head.removeprefix(_SYMBOLIC)) if head.startswith(_SYMBOLIC) else head

    def has_ref(self, ref: str) -> bool:
        """Whether the full ref, such as ``refs/heads/main`` or ``refs/remotes/origin/main``, names a commit."""
        return bool(self.commit_of(ref))

    def commit_of(self, ref: str) -> str:
        """The commit the full ref names: its file under the common git folder, else its line in ``packed-refs``."""
        common = self._common_folder()
        loose = common / ref
        if loose.is_file():
            return loose.read_text(encoding="utf-8").strip()
        return self._packed().get(ref, "")

    def branch_names(self) -> list[str]:
        """Every local branch, sorted as ``git for-each-ref refs/heads`` lists them."""
        heads = self._common_folder() / "refs" / "heads"
        loose = {path.relative_to(heads).as_posix() for path in heads.rglob("*") if path.is_file()} if heads.is_dir() else set()
        packed = {ref.removeprefix(_HEADS) for ref in self._packed() if ref.startswith(_HEADS)}
        return sorted(loose | packed)

    def has_remote(self, name: str) -> bool:
        """Whether the config names a URL for the remote called name, as ``git remote get-url`` would answer."""
        config = self._common_folder() / "config"
        if not config.is_file():
            return False
        section = ""
        for line in config.read_text(encoding="utf-8").splitlines():
            remote = _REMOTE_SECTION.match(line)
            if remote:
                section = remote.group(1)
            elif _SECTION.match(line):
                section = ""
            elif section == name and _URL.match(line):
                return True
        return False

    def worktrees(self) -> list[tuple[Path, str]]:
        """Every checkout of the repository with the branch it has checked out (empty when detached), the main clone
        first, as ``git worktree list`` lists them."""
        common = self._common_folder()
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

    def _head(self) -> str:
        own = self._own_folder()
        return (own / "HEAD").read_text(encoding="utf-8").strip() if own is not None else ""

    def _own_folder(self) -> Path | None:
        """The checkout's own git folder: its .git folder, or the folder a linked worktree's .git file names."""
        marker = self._checkout / ".git"
        if marker.is_dir():
            return marker
        if marker.is_file():
            named = marker.read_text(encoding="utf-8").split("gitdir:", 1)[-1].strip()
            return (self._checkout / named).resolve()
        return None

    def _common_folder(self) -> Path:
        """The git folder that keeps the refs, config and worktrees: the main clone's, named by a worktree's commondir."""
        own = self._own_folder()
        if own is None:
            return self._checkout / ".git"
        common = own / "commondir"
        return (own / common.read_text(encoding="utf-8").strip()).resolve() if common.is_file() else own

    def _packed(self) -> dict[str, str]:
        packed = self._common_folder() / "packed-refs"
        if not packed.is_file():
            return {}
        found: dict[str, str] = {}
        for line in packed.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith(("#", "^")):
                continue
            commit, _, ref = line.partition(" ")
            found[ref.strip()] = commit
        return found
