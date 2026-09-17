"""Workspace aggregate, WorkSession, GitRepo, SessionLog."""

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
    "SessionPaths",
    "SessionModel",
    "docs_dir",
    "session_dir",
    "inherit_annotations",
    "inherit_annotations_from_bases",
    "summarize_mapping",
]


def __getattr__(name: str):
    if name in (
        "WorkSession",
        "Workspace",
        "ContextToolHost",
        "Turn",
        "Mistake",
        "Correction",
        "SessionPaths",
        "SessionModel",
        "docs_dir",
        "session_dir",
    ):
        from workspace import workspace as _w

        return getattr(_w, name)
    if name in ("GitRepo", "NullGitRepo", "Repo"):
        from workspace.git_repo import GitRepo, NullGitRepo, Repo

        return {
            "GitRepo": GitRepo,
            "NullGitRepo": NullGitRepo,
            "Repo": Repo,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
