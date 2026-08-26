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
    find_git_root,
    format_commit_message,
    format_github_issue_trailer,
    parse_issue_number,
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
    "find_git_root",
    "format_commit_message",
    "format_github_issue_trailer",
    "parse_issue_number",
]
