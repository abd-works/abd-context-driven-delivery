"""Checkout - one folder git checks a branch out in: the main clone, or a linked worktree beside it."""
from __future__ import annotations

from pathlib import Path

from harness.git.git import Git
from harness.git.git_facts import AskedOfGit, GitFacts, GitFolder, NoGitFacts


class Checkout:
    """*Checkout* is one checkout of a repository, known by its top folder: whether it is the main clone or a linked
    worktree, the branch it has out, and the facts its git holds (*GitFacts*). Every part of the framework and of
    space/repo that asks which checkout holds a folder, or what a checkout's git holds, asks one of these, so the answer
    is read one way on both sides of the boundary."""

    def __init__(self, folder: Path | str) -> None:
        self.folder = Path(folder).resolve()
        self._read: GitFolder | None = None

    @classmethod
    def holding(cls, folder: Path | str) -> Checkout:
        """The checkout holding folder: the nearest folder at or above it that git marks as a checkout's top, else the
        folder itself, which is then no clone."""
        resolved = Path(folder).resolve()
        current = resolved.parent if resolved.is_file() else resolved
        top = next((candidate for candidate in (current, *current.parents) if (candidate / ".git").exists()), current)
        return cls(top)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Checkout):
            return NotImplemented
        return self.folder == other.folder

    def __hash__(self) -> int:
        return hash(self.folder)

    def __repr__(self) -> str:
        return f"Checkout({self.folder!s})"

    @property
    def is_clone(self) -> bool:
        """Whether git works here: a .git folder holding a HEAD, or the .git file of a linked worktree. A .git folder with
        nothing in it only marks a project's root."""
        marker = self.folder / ".git"
        return marker.is_file() or (marker / "HEAD").is_file()

    @property
    def is_main(self) -> bool:
        """Whether this is a repository's main clone, whose .git is a directory."""
        return (self.folder / ".git").is_dir()

    @property
    def is_linked_worktree(self) -> bool:
        """Whether this is a linked worktree beside the main clone, whose .git is a file naming its git folder."""
        return (self.folder / ".git").is_file()

    @property
    def main_folder(self) -> Path:
        """The repository's main checkout: this one unless it is a linked worktree, whose git folder leads back to it."""
        return GitFolder(self.folder).main_checkout()

    @property
    def branch(self) -> str:
        """The branch checked out here; empty for a checkout on no branch or a folder that is no clone."""
        if not self.is_clone or not self.facts.is_on_branch():
            return ""
        return self.facts.head_branch()

    @property
    def facts(self) -> GitFacts:
        """What this checkout's git holds: read from its .git files where they can be, else asked of git, and nothing
        for a folder that is no clone. Chosen again until the files can be read, so a plain folder made a repository is
        read from its files from then on."""
        if self._read is not None:
            return self._read
        folder = GitFolder(self.folder)
        if folder.is_readable:
            self._read = folder
            return folder
        return AskedOfGit(Git(self.folder)) if self.is_clone else NoGitFacts(self.folder)
