"""Shim — canonical git model lives in tools/git."""

from git import (
    Commit,
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
    "Commit",
    "DirtyBranchSwitchError",
    "GhConnectError",
    "GitConnectError",
    "GitRepo",
    "NullGitRepo",
    "Repo",
    "TicketNotFoundError",
    "_git",
]
