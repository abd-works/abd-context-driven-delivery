"""Workspace aggregate, WorkSession, GitRepo, SessionLog."""

from workspace.session import SessionPaths

docs_dir = SessionPaths.docs_dir
from workspace.session_log import (
    ISessionLog,
    SessionLog,
    inherit_annotations,
    inherit_annotations_from_bases,
    summarize_mapping,
)

__all__ = [
    "ISessionLog",
    "Workspace",
    "WorkSession",
    "ContextToolHost",
    "GitRepo",
    "NullGitRepo",
    "SessionLog",
    "docs_dir",
    "inherit_annotations",
    "inherit_annotations_from_bases",
    "summarize_mapping",
]


def __getattr__(name: str):
    if name in ("WorkSession", "Workspace", "ContextToolHost", "Turn", "Mistake", "Correction"):
        from workspace import workspace as _w

        return getattr(_w, name)
    if name in ("GitRepo", "NullGitRepo", "find_git_root"):
        from workspace.git_repo import GitRepo, NullGitRepo, find_git_root

        return {
            "GitRepo": GitRepo,
            "NullGitRepo": NullGitRepo,
            "find_git_root": find_git_root,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
