"""Git utility — repo, branch, commit, project, ticket."""

from git._cli import (
    _DirtyBranchSwitchError as DirtyBranchSwitchError,
    _GhConnectError as GhConnectError,
    _GitConnectError as GitConnectError,
    _TicketNotFoundError as TicketNotFoundError,
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
]
