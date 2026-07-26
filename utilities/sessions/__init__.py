"""Session model (named sprints), logging, and BaseContextTool workspace binding.

Public exports include ``workspace_session`` (decorator) and ``WorkspaceSession`` (kit).
``WorkspaceSession`` / ``workspace_session`` load lazily so ``from sessions import log``
does not re-enter ``primitives.actions.action`` while that module is still importing.
"""

from sessions.session import ISession, Session, docs_dir
from sessions.session_log import (
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
    "ISession",
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
    "workspace_session",
]


def __getattr__(name: str):
    if name == "WorkspaceSession":
        from sessions.workspace_session import WorkspaceSession

        return WorkspaceSession
    if name == "workspace_session":
        from sessions._decorator import workspace_session

        return workspace_session
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
