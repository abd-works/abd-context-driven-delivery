"""
Read-only prompt audit hook — logs what crosses the wire to the model.

Appends to .context/prompt-log.txt on:
- beforeSubmitPrompt — user prompt + rule/file attachments
- beforeReadFile — file content Cursor sends to the model
- preToolUse — tool calls (Task prompts, Read paths, shell, etc.)
- subagentStart — subagent task descriptions
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_LOG = _REPO_ROOT / ".context" / "prompt-log.txt"
_PREVIEW_LINES = 8
_PREVIEW_CHARS = 600


def log_path() -> Path:
    """You will honor PROMPT_LOG_PATH when set. Otherwise the default stands."""
    override = os.environ.get("PROMPT_LOG_PATH")
    if override:
        return Path(override)
    return _DEFAULT_LOG


def parse_hook_payload(raw: bytes) -> dict:
    """Strip BOM(s) the way Cursor sends them, then parse JSON."""
    text = raw.decode("utf-8-sig")
    while text.startswith("\ufeff"):
        text = text[1:]
    return json.loads(text)


def _norm_path(path: str) -> str:
    return str(Path(path)).replace("\\", "/").lower()


def classify_path(path: str) -> str:
    """Classify a filesystem path for the audit log."""
    if not path:
        return "unknown"
    norm = _norm_path(path)
    name = Path(path).name.lower()

    if name == "agents.md":
        return "agents-md"
    if "/.cursor/agents/" in norm and norm.endswith(".md"):
        return "agent"
    if "/.cursor/rules/" in norm:
        return "rule"
    if name == "skill.md":
        return "skill"
    if "/references/" in norm:
        return "reference"
    if "/.cursor/skills/" in norm or "/.agents/skills/" in norm:
        return "skill"
    return "file"


def classify_attachment(att: dict) -> tuple[str, str]:
    att_type = att.get("type", "file")
    file_path = att.get("file_path", "")
    if att_type == "rule":
        return "rule", file_path
    return classify_path(file_path), file_path


def _preview(text: str | None) -> str:
    if text is None:
        return ""
    if not isinstance(text, str):
        text = json.dumps(text, indent=2)
    lines = text.splitlines()
    if len(lines) <= _PREVIEW_LINES and len(text) <= _PREVIEW_CHARS:
        return text
    head = "\n".join(lines[:_PREVIEW_LINES])
    if len(head) > _PREVIEW_CHARS:
        head = head[:_PREVIEW_CHARS]
    return f"{head}\n... [{len(lines)} lines, {len(text)} chars total]"


def _header(event: str, data: dict) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    gen = (data.get("generation_id") or "")[:8]
    conv = (data.get("conversation_id") or "")[:8]
    model = data.get("model", "")
    return (
        f"\n{'=' * 78}\n"
        f"{ts}  {event}  conv={conv}  gen={gen}  model={model}\n"
        f"{'-' * 78}\n"
    )


def append_log(block: str, target: Path | None = None) -> None:
    path = target or log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)
        if not block.endswith("\n"):
            f.write("\n")


def format_before_submit(data: dict) -> str:
    lines = [_header("beforeSubmitPrompt", data)]
    lines.append("USER PROMPT:")
    lines.append(_preview(data.get("prompt", "")))
    attachments = data.get("attachments") or []
    if attachments:
        lines.append("\nATTACHMENTS:")
        for att in attachments:
            kind, path = classify_attachment(att)
            lines.append(f"  [{kind}] {path}")
    return "\n".join(lines)


def format_before_read_file(data: dict) -> str:
    path = data.get("file_path", "")
    kind = classify_path(path)
    content = data.get("content", "")
    lines = [_header("beforeReadFile", data)]
    lines.append(f"READ [{kind}]: {path}")
    lines.append(f"size: {len(content)} chars")
    if content:
        lines.append("preview:")
        lines.append(_preview(content))
    attachments = data.get("attachments") or []
    if attachments:
        lines.append("\nPROMPT ATTACHMENTS (bundled with read):")
        for att in attachments:
            ak, ap = classify_attachment(att)
            lines.append(f"  [{ak}] {ap}")
    return "\n".join(lines)


def format_pre_tool_use(data: dict) -> str:
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    lines = [_header(f"preToolUse:{tool_name}", data)]

    if tool_name == "Task":
        for key in ("description", "prompt", "subagent_type", "model"):
            val = tool_input.get(key)
            if val:
                lines.append(f"{key}: {_preview(str(val))}")
    elif tool_name in ("Read", "TabRead"):
        path = tool_input.get("path") or tool_input.get("file_path") or ""
        lines.append(f"read [{classify_path(path)}]: {path}")
    else:
        for key, val in tool_input.items():
            if key in ("command", "pattern", "query", "url", "description", "prompt"):
                lines.append(f"{key}: {_preview(str(val))}")
        path = tool_input.get("path") or tool_input.get("file_path") or ""
        if path:
            lines.append(f"path [{classify_path(path)}]: {path}")

    return "\n".join(lines)


def format_subagent_start(data: dict) -> str:
    lines = [_header("subagentStart", data)]
    for key in ("subagent_type", "subagent_model", "task", "git_branch"):
        val = data.get(key)
        if val:
            lines.append(f"{key}: {_preview(str(val))}")
    return "\n".join(lines)


def handle(data: dict, *, target: Path | None = None) -> dict:
    event = data.get("hook_event_name", "preToolUse")

    if event == "beforeSubmitPrompt":
        append_log(format_before_submit(data), target)
        return {"continue": True}
    if event == "beforeReadFile":
        append_log(format_before_read_file(data), target)
        return {"permission": "allow"}
    if event == "subagentStart":
        append_log(format_subagent_start(data), target)
        return {"permission": "allow"}
    if event == "preToolUse":
        append_log(format_pre_tool_use(data), target)
        return {"permission": "allow"}

    return {"permission": "allow"}


def main():
    raw = sys.stdin.buffer.read()
    if not raw.strip():
        print(json.dumps({"permission": "allow"}))
        return
    try:
        data = parse_hook_payload(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        print(json.dumps({"permission": "allow"}))
        return
    out = handle(data)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
