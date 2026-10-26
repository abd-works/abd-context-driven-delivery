"""Phase-1 feedback loop: /branch-create skill MCP names vs live host + mcp.json.

Exit 0 = green (skills that name branch-create / new_branch point at enrolled tools;
project mcp.json has cdd; no stale branch.create / repo.branch_create).
Exit 1 = red (the thrash failure mode: skill names a missing MCP tool).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_USE_MCP = re.compile(r"Use MCP tool:\s*`([A-Za-z0-9_.-]+)")
_CALL_MCP = re.compile(r"Call MCP ``([A-Za-z0-9_.-]+)``")
_STALE = frozenset({"branch.create", "repo.branch_create", "branch.branch_create"})
_BRANCH_CREATE_NAMES = frozenset({"branch-create", "new-branch"})


def _rel(path: Path, root: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _collect_refs(cursor: Path) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for folder, pattern in (("skills", "SKILL.md"), ("commands", "*.md")):
        base = cursor / folder
        if not base.is_dir():
            continue
        for path in base.rglob(pattern if folder == "skills" else "*.md"):
            if folder == "skills" and path.name != "SKILL.md":
                continue
            text = path.read_text(encoding="utf-8")
            rel = _rel(path, cursor)
            for match in _USE_MCP.finditer(text):
                refs.append((rel, match.group(1)))
            for match in _CALL_MCP.finditer(text):
                refs.append((rel, match.group(1)))
    return refs


def _published(repo: Path) -> set[str]:
    from harness.installation.installer import Installer
    from harness.mcp.mcp_server import McpHost

    installer = Installer(repo=repo)
    host = McpHost.from_refs(
        tuple(installer.collect_toolsets()),
        repo=str(repo),
        project=str(repo),
    )
    return set(host._runtime.tools) | set(host._runtime.prompts) | {"cdd.ping"}


def _mcp_has_cdd(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return "cdd" in (data.get("mcpServers") or {})


def main() -> int:
    repo = _REPO
    cursor = repo / ".cursor"
    refs = _collect_refs(cursor)
    published = _published(repo)

    stale = [(path, name) for path, name in refs if name in _STALE]
    branch_paths = [
        (path, name)
        for path, name in refs
        if any(token in path for token in _BRANCH_CREATE_NAMES)
        or name in _STALE
        or name == "repo.new_branch"
    ]
    missing_on_create = [
        (path, name)
        for path, name in branch_paths
        if name not in published
    ]

    project_cdd = _mcp_has_cdd(cursor / "mcp.json")
    user_cdd = _mcp_has_cdd(Path.home() / ".cursor" / "mcp.json")
    host_new_branch = "repo.new_branch" in published

    report = {
        "ok": not stale and not missing_on_create and project_cdd and host_new_branch,
        "symptom": (
            "skill names missing MCP tool → agent thrash"
            if stale or missing_on_create
            else "aligned"
        ),
        "project_mcp_has_cdd": project_cdd,
        "user_mcp_has_cdd": user_cdd,
        "host_has_repo_new_branch": host_new_branch,
        "stale_skill_mcp_names": [{"path": p, "mcp": n} for p, n in stale],
        "branch_create_refs": [{"path": p, "mcp": n} for p, n in branch_paths],
        "missing_on_host": [{"path": p, "mcp": n} for p, n in missing_on_create],
    }
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
