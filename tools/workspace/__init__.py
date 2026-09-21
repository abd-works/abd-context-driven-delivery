"""Workspace aggregate, WorkSession, GitRepo."""

__all__ = [
    "WorkSession",
    "WorkSessionGuidance",
    "WorkSessionRulesCollection",
    "WorkSessionRule",
    "Example",
    "Examples",
    "Turn",
    "TurnCommit",
    "GitRepo",
    "NullGitRepo",
]


def __getattr__(name: str):
    if name in (
        "WorkSession",
        "WorkSessionGuidance",
        "WorkSessionRulesCollection",
        "WorkSessionRule",
        "Example",
        "Examples",
        "Turn",
        "TurnCommit",
    ):
        from workspace import workspace as _w

        return getattr(_w, name)
    if name in ("GitRepo", "NullGitRepo", "Repo"):
        from git import GitRepo, NullGitRepo, Repo

        return {
            "GitRepo": GitRepo,
            "NullGitRepo": NullGitRepo,
            "Repo": Repo,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
