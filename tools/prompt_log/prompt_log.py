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
from harness.hooks.hook_server import HookPayload
from harness.hooks.hooks import Hook, Hooks
from harness.installation.destination import noCatalog
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


def _header(event: str, payload: HookPayload) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    gen = payload.generation_id[:8]
    conv = payload.conversation_id[:8]
    model = payload.get("model", "")
    return (
        f"\n{'=' * 78}\n"
        f"{ts}  {event}  conv={conv}  gen={gen}  model={model}\n"
        f"{'-' * 78}\n"
    )


def format_before_submit(payload: HookPayload) -> str:
    lines = [_header("beforeSubmitPrompt", payload)]
    lines.append("USER PROMPT:")
    lines.append(_preview(payload.get("prompt", "")))
    attachments = payload.get("attachments") or []
    if attachments:
        lines.append("\nATTACHMENTS:")
        for att in attachments:
            kind, path = classify_attachment(att)
            lines.append(f"  [{kind}] {path}")
    return "\n".join(lines)


def format_before_read_file(payload: HookPayload) -> str:
    path = payload.get("file_path", "")
    kind = classify_path(path)
    content = payload.get("content", "")
    lines = [_header("beforeReadFile", payload)]
    lines.append(f"READ [{kind}]: {path}")
    lines.append(f"size: {len(content)} chars")
    if content:
        lines.append("preview:")
        lines.append(_preview(content))
    attachments = payload.get("attachments") or []
    if attachments:
        lines.append("\nPROMPT ATTACHMENTS (bundled with read):")
        for att in attachments:
            ak, ap = classify_attachment(att)
            lines.append(f"  [{ak}] {ap}")
    return "\n".join(lines)


def format_pre_tool_use(payload: HookPayload) -> str:
    tool_name = payload.tool_name
    tool_input = payload.tool_input
    lines = [_header(f"preToolUse:{tool_name}", payload)]

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


def format_subagent_start(payload: HookPayload) -> str:
    lines = [_header("subagentStart", payload)]
    for key in ("subagent_type", "subagent_model", "task", "git_branch"):
        val = payload.get(key)
        if val:
            lines.append(f"{key}: {_preview(str(val))}")
    return "\n".join(lines)


def format_after_agent_response(payload: HookPayload) -> str:
    lines = [_header("afterAgentResponse", payload)]
    text = payload.get("text")
    if text:
        lines.append(f"text: {_preview(str(text))}")
    return "\n".join(lines)


@noCatalog
@Hooks(disabled=True)
@agent_toolset
class PromptLog:
    """Audit what Cursor sends the model — one ``@Hook`` per event, each writing that event's entry to the log.

    The log is the file the toolset was made with; made with none, ``PROMPT_LOG_PATH`` when set, else
    ``prompt-log.txt`` in the logs folder of the session open in the project the event happened in, read for each
    event so the log follows a session switch."""

    def __init__(self, log: Path | None = None) -> None:
        self._log = log

    def log_for(self, payload: HookPayload) -> Path:
        """The file payload's entry is written to."""
        if self._log is not None:
            return self._log
        override = os.environ.get("PROMPT_LOG_PATH")
        if override:
            return Path(override)
        from space.session.sessions import Sessions

        return Sessions(payload.project).saved.hook_log(_LOG_NAME)

    def _append(self, payload: HookPayload, entry: str) -> None:
        path = self.log_for(payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as log:
            log.write(entry if entry.endswith("\n") else f"{entry}\n")

    @Hook("beforeSubmitPrompt")
    def before_submit_prompt(self, payload: HookPayload) -> dict:
        self._append(payload, format_before_submit(payload))
        return {"continue": True}

    @Hook("beforeReadFile")
    def before_read_file(self, payload: HookPayload) -> dict:
        self._append(payload, format_before_read_file(payload))
        return {"permission": "allow"}

    @Hook("preToolUse")
    def pre_tool_use(self, payload: HookPayload) -> dict:
        self._append(payload, format_pre_tool_use(payload))
        return {"permission": "allow"}

    @Hook("subagentStart")
    def subagent_start(self, payload: HookPayload) -> dict:
        self._append(payload, format_subagent_start(payload))
        return {"permission": "allow"}

    @Hook("afterAgentResponse")
    def after_agent_response(self, payload: HookPayload) -> dict:
        self._append(payload, format_after_agent_response(payload))
        return {}
