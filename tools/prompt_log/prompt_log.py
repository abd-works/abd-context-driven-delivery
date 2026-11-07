"""
Read-only prompt audit hook — logs what crosses the wire to the model.

Appends to ``.sessions/{name}/logs/prompt-log.txt`` in the project being worked on, for the session open there, on:
- beforeSubmitPrompt — user prompt + rule/file attachments
- beforeReadFile — file content Cursor sends to the model
- preToolUse — tool calls (Task prompts, Read paths, shell, etc.)
- subagentStart — subagent task descriptions
- afterAgentResponse — the agent's reply text
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from harness.agent_tools.agent_tools import agent_toolset
from harness.hooks.hooks import Hook, Hooks
_PREVIEW_LINES = 8
_PREVIEW_CHARS = 600
_LOG_NAME = "prompt-log.txt"


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


def format_after_agent_response(data: dict) -> str:
    lines = [_header("afterAgentResponse", data)]
    text = data.get("text")
    if text:
        lines.append(f"text: {_preview(str(text))}")
    return "\n".join(lines)


@Hooks(disabled=True)
@agent_toolset
class PromptLog:
    """Audit what Cursor sends the model — one ``@Hook`` per event, each writing that event's entry to the log.

    The log is the file the toolset was made with; made with none, ``PROMPT_LOG_PATH`` when set, else
    ``prompt-log.txt`` in the logs folder of the session open in the project being worked on, read for each event so
    the log follows a session switch."""

    def __init__(self, log: Path | None = None) -> None:
        self._log = log

    @property
    def log(self) -> Path:
        if self._log is not None:
            return self._log
        override = os.environ.get("PROMPT_LOG_PATH")
        if override:
            return Path(override)
        from space.repo.repo import Repo
        from space.work_state import project_checkout

        return Repo(project_checkout()).current_session.hook_log(_LOG_NAME)

    def _append(self, entry: str) -> None:
        path = self.log
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as log:
            log.write(entry if entry.endswith("\n") else f"{entry}\n")

    @Hook("beforeSubmitPrompt")
    def before_submit_prompt(self, payload: dict) -> dict:
        self._append(format_before_submit(payload))
        return {"continue": True}

    @Hook("beforeReadFile")
    def before_read_file(self, payload: dict) -> dict:
        self._append(format_before_read_file(payload))
        return {"permission": "allow"}

    @Hook("preToolUse")
    def pre_tool_use(self, payload: dict) -> dict:
        self._append(format_pre_tool_use(payload))
        return {"permission": "allow"}

    @Hook("subagentStart")
    def subagent_start(self, payload: dict) -> dict:
        self._append(format_subagent_start(payload))
        return {"permission": "allow"}

    @Hook("afterAgentResponse")
    def after_agent_response(self, payload: dict) -> dict:
        self._append(format_after_agent_response(payload))
        return {}
