"""SessionRoots - where each session of a checkout works: its own worktree, a folder chosen for it, or the checkout."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import TYPE_CHECKING

from space.session.session import MAIN_SESSION_NAME, Session

if TYPE_CHECKING:
    from space.session.sessions import Sessions

# How long one ``git worktree list`` answers where each branch's worktree is before it is read again.
_WORKTREE_LISTING_SECONDS = 2.0


class SessionRoots:
    """Where the sessions of one checkout work, derived when asked and never saved on a switch: a ticket's own worktree
    as git lists it, a workpath a person chose by hand, else the checkout. A session's root is always in its own
    checkout."""

    def __init__(self, sessions: Sessions) -> None:
        self._sessions = sessions
        # One ``git worktree list``, read again after a moment, from which each session's root is derived.
        self._worktree_listing: tuple[float, dict[str, Path]] = (0.0, {})

    def root_of(self, session: Session) -> Path:
        """Where session writes, derived when asked and never saved on a switch: a workpath a person chose by hand in
        its session.json, else its own worktree as git lists it, else this checkout. A session's root is always in its
        own checkout, so a chosen workpath that lies in another checkout of the repository names the same folder in it."""
        stored = str(session.record.fields.get("workpath", "") or "").strip()
        checkout = self.checkout_of(session)
        chosen = self.in_checkout(checkout, checkout / stored) if stored else None
        # WHY: older switches saved the checkout itself, or a worktree since removed, as the workpath; neither was chosen.
        if chosen is not None and chosen.is_dir() and chosen not in (self._sessions.root, self._sessions.repo.main_clone.root, checkout):
            return chosen
        return checkout

    def checkout_of(self, session: Session) -> Path:
        """The checkout session works in: its own worktree, the one its ticket opened or the one git lists for its
        branch, else this checkout."""
        if not session.name or session.name == MAIN_SESSION_NAME:
            return self._sessions.root
        kept = str(session.record.fields.get("worktree", "") or "").strip()
        if kept and Path(kept).is_dir():
            return Path(kept).resolve()
        worktree = self.worktree_of(session.name)
        return worktree if worktree is not None else self._sessions.root

    def in_checkout(self, checkout: Path, path: Path | str) -> Path:
        """path, resolved, moved into checkout when it lies in another checkout of this repository, its main clone or
        another worktree, at the same place from that checkout's top: ``<main>/harness/.context`` becomes
        ``<checkout>/harness/.context``. A path outside every checkout is kept as it is."""
        resolved = Path(path).resolve()
        if resolved.is_relative_to(checkout):
            return resolved
        others = [self._sessions.repo.main_clone.root.resolve(), self._sessions.root.resolve(), *self._worktrees_by_branch().values()]
        holding = [other for other in others if other != checkout and resolved.is_relative_to(other)]
        if not holding:
            return resolved
        top = max(holding, key=lambda other: len(other.parts))
        return (checkout / resolved.relative_to(top)).resolve()

    def worktree_of(self, name: str) -> Path | None:
        """The linked worktree of the branch called name, else of the one branch whose name holds name as a whole word,
        as git lists them now."""
        listed = self._worktrees_by_branch()
        if name in listed:
            return listed[name]
        word = re.compile(rf"(^|[/_-]){re.escape(name)}($|[/_-])")
        matches = [folder for branch, folder in listed.items() if word.search(branch)]
        return matches[0] if len(matches) == 1 else None

    def _worktrees_by_branch(self) -> dict[str, Path]:
        read_at, listed = self._worktree_listing
        if read_at and time.monotonic() - read_at < _WORKTREE_LISTING_SECONDS:
            return listed
        main = self._sessions.repo.main_clone.root
        try:
            listing = self._sessions.repo.main_clone.worktrees.listing()
        except (RuntimeError, OSError):  # a folder in no repository has no worktrees
            listing = []
        listed = {}
        for path, branch in listing:
            folder = path.resolve()
            if branch and folder != main and folder.is_dir():
                listed[branch] = folder
        self._worktree_listing = (time.monotonic(), listed)
        return listed
