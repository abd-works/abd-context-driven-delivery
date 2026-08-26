"""Low-level git and gh CLI adapters — internal to utilities/git."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

_GIT_DO_NOT_PROCEED = (
    "Do not proceed unless the user tells you to continue without a git connection."
)
_GH_DO_NOT_PROCEED = (
    "Do not proceed unless the user tells you to continue without GitHub CLI access."
)

_ISSUE_NUMBER = re.compile(r"^\d+$")
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


def _find_git_root(start: str | Path) -> Path | None:
    current = Path(start).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def _parse_issue_number(ticket: str) -> int:
    """Normalize #87, owner/repo#87, or issue URLs to an issue number."""
    cleaned = ticket.strip()
    if not cleaned:
        raise ValueError(f"not a GitHub issue reference: {ticket!r}")
    if cleaned.startswith("#"):
        return int(cleaned[1:])
    if "#" in cleaned:
        suffix = cleaned.rsplit("#", 1)[-1]
        if _ISSUE_NUMBER.match(suffix):
            return int(suffix)
    if "/issues/" in cleaned:
        suffix = cleaned.rstrip("/").split("/")[-1]
        if _ISSUE_NUMBER.match(suffix):
            return int(suffix)
    if _ISSUE_NUMBER.match(cleaned):
        return int(cleaned)
    raise ValueError(f"not a GitHub issue reference: {ticket!r}")


def _format_github_issue_trailer(owner: str, repo: str, number: int) -> str:
    return f"{owner}/{repo}#{number}"


def _format_commit_message(subject: str, trailers: dict[str, str]) -> str:
    lines = [subject.strip()]
    for key, value in trailers.items():
        text = (value or "").strip()
        if text:
            lines.append(f"{key}: {text}")
    return "\n".join(lines)


def _parse_commit_trailers(message: str) -> dict[str, str]:
    lines = (message or "").splitlines()
    if not lines:
        return {}
    data: dict[str, str] = {}
    for line in lines[1:]:
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        data[key.strip()] = value.strip()
    return data


def _payload_to_note(fields: dict[str, str]) -> str:
    return "\n".join(f"{key}: {value}" for key, value in fields.items())


def _note_to_payload(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (text or "").splitlines():
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        out[key.strip()] = value
    return out


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


def _gh_view_issue(root: Path, ticket: str) -> dict[str, str | int] | None:
    number = _parse_issue_number(ticket)
    try:
        raw = _run_gh(
            "-C",
            str(root),
            "issue",
            "view",
            str(number),
            "--json",
            "number,title,body,url,state",
        )
    except _GhConnectError as exc:
        message = str(exc).lower()
        if "could not resolve" in message or "not found" in message:
            return None
        raise
    payload = json.loads(raw or "{}")
    if not payload:
        return None
    return {
        "number": int(payload["number"]),
        "title": str(payload.get("title") or ""),
        "body": str(payload.get("body") or ""),
        "url": str(payload.get("url") or ""),
        "state": str(payload.get("state") or ""),
    }


def _gh_create_issue(root: Path, title: str, body: str) -> dict[str, str | int]:
    raw = _run_gh(
        "-C",
        str(root),
        "issue",
        "create",
        "--title",
        title,
        "--body",
        body,
        "--json",
        "number,title,body,url",
    )
    payload = json.loads(raw or "{}")
    return {
        "number": int(payload["number"]),
        "title": str(payload.get("title") or title),
        "body": str(payload.get("body") or body),
        "url": str(payload.get("url") or ""),
    }


def _gh_close_issue(root: Path, ticket: str) -> None:
    number = _parse_issue_number(ticket)
    _run_gh("-C", str(root), "issue", "close", str(number))


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
