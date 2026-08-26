"""Shim — canonical git model lives in utilities/git."""

from git import (
    DirtyBranchSwitchError,
    GhConnectError,
    GitConnectError,
    GitRepo,
    NullGitRepo,
    Repo,
    TicketNotFoundError,
)

_git = Repo.git

__all__ = [
    "DirtyBranchSwitchError",
    "GhConnectError",
    "GitConnectError",
    "GitRepo",
    "NullGitRepo",
    "Repo",
    "TicketNotFoundError",
    "_git",
]
