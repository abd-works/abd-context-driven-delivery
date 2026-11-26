"""CheckoutWorktrees - the linked worktrees and branches of the repository a checkout's sessions work in, listed once and
read again after a moment."""

from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING

from space.session.session_checkout import names_ticket

if TYPE_CHECKING:
    from space.session.sessions import Sessions

# How long one listing of the worktrees and branches answers before it is read again.
_LISTING_SECONDS = 2.0


class CheckoutWorktrees:
    """The linked worktrees beside the main clone, each by the branch it has out, and the repository's branch names, as
    git lists them: listed once and read again after a moment, since every session placed on a board read asks, and the
    one owner of that rule. A path in another checkout of the repository is moved into a session's own."""

    def __init__(self, sessions: Sessions) -> None:
        self._sessions = sessions
        self._listing: tuple[float, dict[str, Path], list[str]] = (0.0, {}, [])

    def of_branch(self, name: str) -> Path | None:
        """The linked worktree of the branch called name, else of the one branch whose name holds name as a whole word,
        as git lists them now; none when no linked worktree has either."""
        listed = self._read()[0]
        if name in listed:
            return listed[name]
        matches = [folder for branch, folder in listed.items() if names_ticket(branch, name)]
        return matches[0] if len(matches) == 1 else None

    def branch_names(self) -> list[str]:
        """Every local branch of the repository, by name."""
        return self._read()[1]

    def forget(self) -> None:
        """List again at the next ask: a worktree or branch was just made or removed here."""
        self._listing = (0.0, {}, [])

    def in_checkout(self, checkout: Path, path: Path | str) -> Path:
        """path, resolved, moved into checkout when it lies in another checkout of this repository, its main clone or
        another worktree, at the same place from that checkout's top: ``<main>/harness/.context`` becomes
        ``<checkout>/harness/.context``. A path outside every checkout is kept as it is."""
        resolved = Path(path).resolve()
        if resolved.is_relative_to(checkout):
            return resolved
        others = [self._sessions.repo.main_clone.root.resolve(), self._sessions.root.resolve(), *self._read()[0].values()]
        holding = [other for other in others if other != checkout and resolved.is_relative_to(other)]
        if not holding:
            return resolved
        top = max(holding, key=lambda other: len(other.parts))
        return (checkout / resolved.relative_to(top)).resolve()

    def _read(self) -> tuple[dict[str, Path], list[str]]:
        read_at, worktrees, branches = self._listing
        if read_at and time.monotonic() - read_at < _LISTING_SECONDS:
            return worktrees, branches
        repo = self._sessions.repo.main_clone
        try:
            checkouts = repo.worktrees.by_branch
            branches = [branch.name for branch in repo.branches]
        except (RuntimeError, OSError):  # a folder in no repository has no worktrees and no branches
            checkouts, branches = {}, []
        worktrees = {branch.name: checkout.root for branch, checkout in checkouts.items() if not checkout.is_main_clone}
        self._listing = (time.monotonic(), worktrees, branches)
        return worktrees, branches
