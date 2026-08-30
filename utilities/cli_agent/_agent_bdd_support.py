"""Shared helpers for #44 one-at-a-time agent BDD specs. Not production."""
from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from git.git import GitRepo, Repo

CLI = "cli_agent.cli_agent:CliAgent"
WS = "workspace.workspace:WorkSession"
ECHO = "echo.echo:Echo"
SPAWN_LINE = re.compile(r"^--- spawn\b", re.MULTILINE)
HOP_S = 120
BACKLOG_S = 600
STALL_S = 120.0


def init_git_repo(prefix: str) -> Path:
    primary = Path(tempfile.mkdtemp(prefix=prefix))
    Repo.git(primary, "init")
    Repo.git(primary, "config", "user.email", "e2e@abd.works")
    Repo.git(primary, "config", "user.name", "e2e")
    Repo.git(primary, "commit", "--allow-empty", "-m", "init")
    Repo.git(primary, "branch", "-M", "main")
    return primary


def worktree(primary: Path, session: str) -> Path | None:
    found = GitRepo(primary).worktree_for(f"session/{session}")
    return Path(found.path) if found is not None else None


def session_dir(workspace: Path, session: str) -> Path:
    return workspace / ".context" / "sessions" / session


def records(workspace: Path, session: str) -> list[dict]:
    path = session_dir(workspace, session) / "cli-agent-session.jsonl"
    if not path.is_file():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def kinds(workspace: Path, session: str) -> list[str]:
    return [str(r.get("kind") or "") for r in records(workspace, session)]


def spawn_count(workspace: Path, session: str, *, role: str = "doer") -> int:
    log = session_dir(workspace, session) / f"cli-agent-{role}.log"
    if not log.is_file():
        return 0
    return len(SPAWN_LINE.findall(log.read_text(encoding="utf-8", errors="replace")))


def ctx(workspace: Path, session: str) -> dict:
    return {
        "workspace": str(workspace).replace("\\", "/"),
        "session": session,
    }


def echo_job(prompt: str, *, with_action: bool = True) -> dict:
    job: dict = {
        "prompt": prompt,
        "tools": [ECHO],
        "judge": True,
        "judge_criteria": (
            "PASS when the doer used Echo (fence and/or echo_session) and finished "
            "the Turn. FAIL only if the doer contacted the judge or edited the queue."
        ),
    }
    if with_action:
        job["actions"] = [ECHO]
    return job


def commit_all(tree: Path, message: str) -> None:
    if not tree.is_dir():
        return
    Repo.git(tree, "add", "-A")
    if Repo.git(tree, "status", "--porcelain").strip():
        Repo.git(tree, "commit", "-m", message)
