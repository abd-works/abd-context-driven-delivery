"""Workspace ``.context/context-index.md`` - where each context tool puts durable work."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

_INDEX_NAME = "context-index.md"
_ENTRY_RE = re.compile(
    r"^\s*[-*]?\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(.+?)\s*$"
)


def context_index_path(workspace: str | Path) -> Path:
    return Path(workspace) / ".context" / _INDEX_NAME


def normalize_root_glob(root: str) -> str:
    """Normalize a tool root to workspace-relative ``./folder/*`` form."""
    text = (root or ".").strip().replace("\\", "/")
    if text.endswith("/*"):
        text = text[:-2]
    if text.endswith("/"):
        text = text[:-1]
    if text in ("", "."):
        return "./*"
    if not text.startswith("./"):
        text = "./" + text.lstrip("/")
    return text + "/*"


def root_glob_to_path(workspace: str | Path, root_glob: str) -> str:
    """Turn ``./tests/*`` into a filesystem path under workspace."""
    text = (root_glob or "./*").strip().replace("\\", "/")
    if text.endswith("/*"):
        text = text[:-2]
    if text.endswith("/"):
        text = text[:-1]
    if text in ("", ".", "./"):
        return str(Path(workspace))
    rel = text[2:] if text.startswith("./") else text.lstrip("/")
    return str(Path(workspace) / rel)


def path_to_root_glob(workspace: str | Path, working: str | Path) -> str:
    """Express working path as a workspace-relative root glob."""
    ws = Path(workspace).resolve()
    work = Path(working).resolve()
    try:
        rel = work.relative_to(ws)
    except ValueError:
        return normalize_root_glob(str(working))
    if str(rel) in (".", ""):
        return "./*"
    return normalize_root_glob(rel.as_posix())


def parse_current_entries(text: str) -> dict[str, str]:
    """Parse ``## Current`` (or whole file) tool = root lines."""
    section = text
    if "## Current" in text:
        after = text.split("## Current", 1)[1]
        if "## " in after:
            section = after.split("## ", 1)[0]
        else:
            section = after
    entries: dict[str, str] = {}
    for line in section.splitlines():
        match = _ENTRY_RE.match(line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        if key.lower() in {"tool", "root"}:
            continue
        entries[key] = normalize_root_glob(value)
    return entries


def read_entries(workspace: str | Path) -> dict[str, str]:
    path = context_index_path(workspace)
    if not path.is_file():
        return {}
    return parse_current_entries(path.read_text(encoding="utf-8"))


def lookup_root(workspace: str | Path, tool_key: str) -> str | None:
    if not tool_key:
        return None
    return read_entries(workspace).get(tool_key)


def render_index(entries: dict[str, str], log_lines: list[str]) -> str:
    lines = [
        "# Context index",
        "",
        "Workspace-relative roots for each context tool. "
        "Prefer these over defaults when generating. "
        "Handoffs must cite this file.",
        "",
        "## Current",
        "",
    ]
    if entries:
        for key in sorted(entries):
            lines.append(f"- {key} = {entries[key]}")
    else:
        lines.append("- *(none yet)*")
    lines.extend(["", "## Log", ""])
    if log_lines:
        lines.extend(f"- {line}" for line in log_lines)
    else:
        lines.append("- *(empty)*")
    lines.append("")
    return "\n".join(lines)


def _parse_log(text: str) -> list[str]:
    if "## Log" not in text:
        return []
    after = text.split("## Log", 1)[1]
    if "## " in after:
        after = after.split("## ", 1)[0]
    lines: list[str] = []
    for raw in after.splitlines():
        stripped = raw.strip()
        if stripped.startswith("- ") and stripped not in {"- *(empty)*"}:
            lines.append(stripped[2:].strip())
    return lines


def upsert_entry(
    workspace: str | Path,
    tool_key: str,
    root_glob: str,
    *,
    note: str = "",
    when: str | None = None,
) -> Path:
    """Create or update one tool root; append a log line when the value changes."""
    if not tool_key:
        raise ValueError("tool_key is required")
    ws = Path(workspace)
    path = context_index_path(ws)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_text = path.read_text(encoding="utf-8") if path.is_file() else ""
    entries = parse_current_entries(existing_text) if existing_text else {}
    log_lines = _parse_log(existing_text) if existing_text else []
    normalized = normalize_root_glob(root_glob)
    previous = entries.get(tool_key)
    entries[tool_key] = normalized
    day = when or date.today().isoformat()
    if previous != normalized:
        detail = f"{tool_key} = {normalized}"
        if previous:
            detail += f" (was {previous})"
        if note:
            detail += f" - {note}"
        log_lines.append(f"{day}: {detail}")
    path.write_text(render_index(entries, log_lines), encoding="utf-8")
    return path
