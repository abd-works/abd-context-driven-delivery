"""Git utility — repo, branch, commit, project, ticket."""

from git.git import (
    Branch,
    CliAgentBinding,
    Commit,
    DirtyBranchSwitchError,
    GhConnectError,
    Git,
    GitConnectError,
    GitRepo,
    Project,
    Repo,
    Ticket,
    TicketNotFoundError,
    TicketState,
    Worktree,
    resolve_github_status_option,
)

NullGitRepo = Repo.memory

__all__ = [
    "Branch",
    "CliAgentBinding",
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
    "Worktree",
    "resolve_github_status_option",
]
