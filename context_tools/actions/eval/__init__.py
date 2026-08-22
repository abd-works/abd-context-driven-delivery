"""eval package — EvalSession domain for turns / mistakes / repairs / YAML trail."""

from eval.session import (
    CDDRepo,
    Correction,
    EvalGitConnectError,
    EvalSession,
    Mistake,
    NullCDDRepo,
    NullGitRepo,
    Repair,
    ToolCall,
    Turn,
    TurnCommit,
    GitRepo,
    find_git_root,
    find_cdd_root,
    repos_for_workspace,
)

__all__ = [
    "CDDRepo",
    "Correction",
    "EvalGitConnectError",
    "EvalSession",
    "Mistake",
    "NullCDDRepo",
    "NullGitRepo",
    "Repair",
    "ToolCall",
    "Turn",
    "TurnCommit",
    "GitRepo",
    "find_git_root",
    "find_cdd_root",
    "repos_for_workspace",
]
