"""WorkSession model, logging, and binding.

``WorkSession`` loads lazily so ``from workspace import log``
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
    "WorkSession",
    "SessionLog",
    "docs_dir",
    "inherit_annotations",
    "inherit_annotations_from_bases",
    "is_logged",
    "log",
    "member_is_logged",
    "summarize_mapping",
]


def __getattr__(name: str):
    if name == "WorkSession":
        from workspace.workspace_session import WorkSession

        return WorkSession
    if name in ("GitRepo", "NullGitRepo", "find_git_root"):
        from workspace.git_repo import GitRepo, NullGitRepo, find_git_root

        return {
            "GitRepo": GitRepo,
            "NullGitRepo": NullGitRepo,
            "find_git_root": find_git_root,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
