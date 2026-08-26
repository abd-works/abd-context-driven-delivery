"""Git utility — repo, branch, commit, project, ticket."""

from git.git import (
    Branch,
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
]
