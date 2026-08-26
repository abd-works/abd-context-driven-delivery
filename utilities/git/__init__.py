"""Git utility — repo, branch, commit, project, ticket."""

from git._cli import (
    _DirtyBranchSwitchError as DirtyBranchSwitchError,
    _GhConnectError as GhConnectError,
    _GitConnectError as GitConnectError,
    _TicketNotFoundError as TicketNotFoundError,
    _find_git_root as find_git_root,
    _format_commit_message as format_commit_message,
    _format_github_issue_trailer as format_github_issue_trailer,
    _parse_issue_number as parse_issue_number,
)
from git.git import (
    Branch,
    Commit,
    Git,
    GitRepo,
    Project,
    Repo,
    Ticket,
    TicketState,
)

NullGitRepo = Repo.memory

__all__ = [
    "Branch",
    "Commit",
    "DirtyBranchSwitchError",
    "GhConnectError",
    "Git",
    "GitConnectError",
    "GitRepo",
    "NullGitRepo",
    "Project",
    "Repo",
    "Ticket",
    "TicketNotFoundError",
    "TicketState",
    "find_git_root",
    "format_commit_message",
    "format_github_issue_trailer",
    "parse_issue_number",
]
