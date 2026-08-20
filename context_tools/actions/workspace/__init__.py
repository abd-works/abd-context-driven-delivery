"""Session model (named sprints + workspace kit), logging, and binding.

``Session`` / ``WorkspaceSession`` load lazily so ``from workspace import log``
does not re-enter ``primitives.actions.action`` while that module is still importing.
"""

from workspace.session import SessionPaths
docs_dir = SessionPaths.docs_dir
from workspace.session_log import (
    ISessionLog,
    SessionLog,
    inherit_annotations,
    inherit_annotations_from_bases,
    is_logged,
    log,
    member_is_logged,
    summarize_mapping,
)

__all__ = [
    "ISessionLog",
    "Session",
    "SessionLog",
    "WorkspaceSession",
    "docs_dir",
    "inherit_annotations",
    "inherit_annotations_from_bases",
    "is_logged",
    "log",
    "member_is_logged",
    "summarize_mapping",
]


def __getattr__(name: str):
    if name in ("Session", "WorkspaceSession"):
        from workspace.workspace_session import Session, WorkspaceSession

        return Session if name == "Session" else WorkspaceSession
    if name in ("WorkspaceRepo", "NullWorkspaceRepo", "find_git_root"):
        from workspace.workspace_repo import (
            NullWorkspaceRepo,
            WorkspaceRepo,
            find_git_root,
        )

        return {
            "WorkspaceRepo": WorkspaceRepo,
            "NullWorkspaceRepo": NullWorkspaceRepo,
            "find_git_root": find_git_root,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
