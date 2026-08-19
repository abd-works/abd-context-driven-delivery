"""eval package — EvalSession domain for turns / mistakes / repairs / YAML trail."""

from eval.session import (
    CDDRepo,
    Correction,
    EvalSession,
    Mistake,
    NullCDDRepo,
    NullWorkspaceRepo,
    Repair,
    Session,
    ToolCall,
    Turn,
    TurnCommit,
    WorkspaceRepo,
    find_git_root,
    find_cdd_root,
    repos_for_workspace,
)

__all__ = [
    "CDDRepo",
    "Correction",
    "EvalSession",
    "Mistake",
    "NullCDDRepo",
    "NullWorkspaceRepo",
    "Repair",
    "Session",
    "ToolCall",
    "Turn",
    "TurnCommit",
    "WorkspaceRepo",
    "find_git_root",
    "find_cdd_root",
    "repos_for_workspace",
]
