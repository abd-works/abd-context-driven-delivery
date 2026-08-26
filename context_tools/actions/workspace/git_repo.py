"""Shim — canonical git model lives in utilities/git."""

from git._cli import _run_git as _git
from git import (
    DirtyBranchSwitchError,
    GhConnectError,
    GitConnectError,
    GitRepo,
    NullGitRepo,
    Repo,
    TicketNotFoundError,
)

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
