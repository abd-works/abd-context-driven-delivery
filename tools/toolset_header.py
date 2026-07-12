"""Read @toolset-manifest headers from toolset class files."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

TOOLSET_MANIFEST_MARKER = "@toolset-manifest"

_AGENT_READING_RE = re.compile(
    r"^\s*#\s*Agent reading this file:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)
_INVOKE_NEW_RE = re.compile(r"^\s*#\s*invoke-new:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_INVOKE_EDIT_RE = re.compile(r"^\s*#\s*invoke-edit:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_INVOKE_CHECK_RE = re.compile(r"^\s*#\s*invoke-check:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_REQUEST_GENERATE_MARKER = re.compile(r"^\s*#\s*request-generate:\s*$", re.IGNORECASE)


@dataclass(frozen=True)
class ToolsetHeader:
    source_path: Path
    manifest_command: str
    agent_instruction: str | None
    invoke_new: str | None
    invoke_edit: str | None
    invoke_check: str | None
    request_generate: str | None


def read_toolset_header(source_path: Path) -> ToolsetHeader:
    """Load agent-facing metadata from comment headers at the top of a toolset file."""
    text = source_path.read_text(encoding="utf-8")
    command = _find_marker_command(text)
    if command is None:
        raise ValueError(f"{source_path}: missing {TOOLSET_MANIFEST_MARKER} comment")
    agent = _AGENT_READING_RE.search(text)
    invoke_new = _INVOKE_NEW_RE.search(text)
    invoke_edit = _INVOKE_EDIT_RE.search(text)
    invoke_check = _INVOKE_CHECK_RE.search(text)
    return ToolsetHeader(
        source_path=source_path.resolve(),
        manifest_command=command.strip(),
        agent_instruction=agent.group(1).strip() if agent else None,
        invoke_new=invoke_new.group(1).strip() if invoke_new else None,
        invoke_edit=invoke_edit.group(1).strip() if invoke_edit else None,
        invoke_check=invoke_check.group(1).strip() if invoke_check else None,
        request_generate=_read_request_generate_block(text),
    )


def _find_marker_command(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            if stripped and not stripped.startswith('"""') and not stripped.startswith("'''"):
                break
            continue
        body = stripped.lstrip("#").strip()
        if TOOLSET_MANIFEST_MARKER not in body:
            continue
        remainder = body.split(TOOLSET_MANIFEST_MARKER, 1)[1].strip()
        if remainder.startswith(":"):
            remainder = remainder[1:].strip()
        if remainder:
            return remainder
    return None


def _read_request_generate_block(text: str) -> str | None:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if _REQUEST_GENERATE_MARKER.match(line):
            start = index + 1
            break
    if start is None:
        return None
    yaml_lines: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if not stripped.startswith("#"):
            break
        body = stripped.lstrip("#")
        if body.startswith(" "):
            yaml_lines.append(body[1:])
        elif body == "":
            break
        else:
            break
    if not yaml_lines:
        return None
    return "\n".join(yaml_lines).rstrip() + "\n"
