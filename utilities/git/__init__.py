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
    InMemoryRepo,
    Project,
    Repo,
    Ticket,
    TicketNotFoundError,
    TicketState,
    Worktree,
    issue_theme_label,
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
    "InMemoryRepo",
    "NullGitRepo",
    "Project",
    "Repo",
    "Ticket",
    "TicketNotFoundError",
    "TicketState",
    "Worktree",
    "issue_theme_label",
    "resolve_github_status_option",
]
