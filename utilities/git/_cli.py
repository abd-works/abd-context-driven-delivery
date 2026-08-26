"""Low-level git and gh CLI adapters — internal to utilities/git."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

_GIT_DO_NOT_PROCEED = (
    "Do not proceed unless the user tells you to continue without a git connection."
)
_GH_DO_NOT_PROCEED = (
    "Do not proceed unless the user tells you to continue without GitHub CLI access."
)

_EVAL_MISTAKES_NOTES = "refs/notes/eval-mistakes"


class _GitConnectError(RuntimeError):
    """Raised when the clone cannot be used for git."""


class _GhConnectError(RuntimeError):
    """Raised when gh cannot be used."""


class _DirtyBranchSwitchError(RuntimeError):
    """Raised when checkout would move a dirty tree onto another branch."""

    def __init__(self, current: str, wanted: str) -> None:
        self.current = current
        self.wanted = wanted
        super().__init__(
            f"Working tree has uncommitted changes on {current!r}; "
            f"not switching to {wanted!r}. Ask whether to bring this work onto "
            f"the session branch, or create a continuation branch "
            f"(e.g. {wanted}-2)."
        )


class _TicketNotFoundError(LookupError):
    """Raised when a GitHub issue reference does not resolve."""


def _git_executable() -> str:
    found = shutil.which("git")
    if found:
        return found
    for candidate in (
        Path(r"C:\Program Files\Git\cmd\git.exe"),
        Path(r"C:\Program Files\Git\bin\git.exe"),
    ):
        if candidate.is_file():
            return str(candidate)
    raise _GitConnectError(
        f"Cannot connect git: `git` is not available. {_GIT_DO_NOT_PROCEED}"
    )


def _gh_executable() -> str:
    found = shutil.which("gh")
    if found:
        return found
    raise _GhConnectError(f"Cannot connect gh: `gh` is not available. {_GH_DO_NOT_PROCEED}")


def _run_git(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            [_git_executable(), "-C", str(root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except _GitConnectError:
        raise
    except OSError as exc:
        raise _GitConnectError(
            f"Cannot connect git: {exc}. {_GIT_DO_NOT_PROCEED}"
        ) from exc
    if completed.returncode != 0:
        err = (completed.stderr or completed.stdout or "").strip()
        raise _GitConnectError(
            f"Cannot connect git: git {' '.join(args)} failed in {root}: "
            f"{err}. {_GIT_DO_NOT_PROCEED}"
        )
    return (completed.stdout or "").strip()


def _run_gh(*args: str) -> str:
    try:
        completed = subprocess.run(
            [_gh_executable(), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except _GhConnectError:
        raise
    except OSError as exc:
        raise _GhConnectError(
            f"Cannot connect gh: {exc}. {_GH_DO_NOT_PROCEED}"
        ) from exc
    if completed.returncode != 0:
        err = (completed.stderr or completed.stdout or "").strip()
        raise _GhConnectError(
            f"Cannot connect gh: gh {' '.join(args)} failed: {err}. {_GH_DO_NOT_PROCEED}"
        )
    return (completed.stdout or "").strip()


def _gh_owner_repo(root: Path) -> tuple[str, str]:
    raw = _run_gh("-C", str(root), "repo", "view", "--json", "nameWithOwner")
    payload = json.loads(raw or "{}")
    name = payload.get("nameWithOwner", "")
    if "/" not in name:
        raise _GhConnectError(
            f"Cannot resolve owner/repo for {root}. {_GH_DO_NOT_PROCEED}"
        )
    owner, repo = name.split("/", 1)
    return owner, repo


def _gh_set_project_status(
    issue_url: str,
    status: str,
    *,
    project_owner: str,
    project_number: int,
) -> None:
    item_raw = _run_gh(
        "project",
        "item-add",
        str(project_number),
        "--owner",
        project_owner,
        "--url",
        issue_url,
        "--format",
        "json",
    )
    item = json.loads(item_raw or "{}")
    item_id = item.get("id")
    if not item_id:
        raise _GhConnectError(
            f"Could not add issue to project. {_GH_DO_NOT_PROCEED}"
        )
    _run_gh(
        "project",
        "item-edit",
        "--id",
        str(item_id),
        "--project-id",
        str(project_number),
        "--owner",
        project_owner,
        "--field",
        "Status",
        "--value",
        status,
    )


def _eval_mistakes_notes_ref() -> str:
    return _EVAL_MISTAKES_NOTES
