"""
Read-only prompt audit hook — logs what crosses the wire to the model.

Appends to ``.sessions/{name}/logs/prompt-log.txt`` in the project being worked on, for the session open there, on:
- beforeSubmitPrompt — user prompt + rule/file attachments
- beforeReadFile — file content Cursor sends to the model
- preToolUse — tool calls (Task prompts, Read paths, shell, etc.)
- subagentStart — subagent task descriptions
- afterAgentResponse — the agent's reply text
"""

from __future__ import annotations

import json
from pathlib import Path

from harness.agent_tools.agent_tools import agent_toolset
from harness.hooks.hook_server import HookPayload
from harness.hooks.hooks import Hook, Hooks, hook
from harness.installation.destination import noCatalog
from space.session.session_log import LogTimestamp

# A long prompt or file is shown by its first lines, cut at a length a person can still scan in the log.
_PREVIEW_LINES = 8
_PREVIEW_CHARS = 600
_LOG_NAME = "prompt-log.txt"
# The width of the rules that frame each entry's header.
_RULE_WIDTH = 78
# A chat or generation id is shown by its first characters, enough to tell the entries of two chats apart.
_SHOWN_ID_LENGTH = 8
# The arguments of a tool call that say what it does, shown under its entry.
_TOOL_INPUT_SHOWN = ("command", "pattern", "query", "url", "description", "prompt")
_TASK_INPUT_SHOWN = ("description", "prompt", "subagent_type", "model")
_SUBAGENT_FIELDS_SHOWN = ("subagent_type", "subagent_model", "task", "git_branch")


class LoggedFile:
    """A file an event names, such as one Cursor reads into the prompt or attaches to it, and what kind of guidance it
    is: an AGENTS.md, an agent, a rule, a skill, a reference, or any other file."""

    def __init__(self, path: str) -> None:
        self.path = path or ""

    @property
    def kind(self) -> str:
        if not self.path:
            return "unknown"
        posix = str(Path(self.path)).replace("\\", "/").lower()
        name = Path(self.path).name.lower()
        if name == "agents.md":
            return "agents-md"
        if "/.cursor/agents/" in posix and posix.endswith(".md"):
            return "agent"
        if "/.cursor/rules/" in posix:
            return "rule"
        if name == "skill.md":
            return "skill"
        if "/references/" in posix:
            return "reference"
        if "/.cursor/skills/" in posix or "/.agents/skills/" in posix:
            return "skill"
        return "file"


class PromptLogEntry:
    """One event's entry in the prompt log: a header naming the event, the chat, and the model, then what the event
    sent the model, added a part at a time."""

    def __init__(self, event: str, payload: HookPayload) -> None:
        self._payload = payload
        self._lines = [self._header(event)]

    @property
    def text(self) -> str:
        return "\n".join(self._lines)

    def with_prompt(self) -> PromptLogEntry:
        self._lines += ["USER PROMPT:", self._preview(self._payload.get("prompt", ""))]
        return self

    def with_attachments(self, title: str) -> PromptLogEntry:
        """The files and rules attached to the prompt, under title; nothing when none are."""
        attachments = self._payload.get("attachments") or []
        if attachments:
            self._lines += [f"\n{title}:", *(self._attachment_line(attachment) for attachment in attachments)]
        return self

    def with_read_file(self) -> PromptLogEntry:
        file = LoggedFile(self._payload.get("file_path", ""))
        content = self._payload.get("content", "")
        self._lines += [f"READ [{file.kind}]: {file.path}", f"size: {len(content)} chars"]
        if content:
            self._lines += ["preview:", self._preview(content)]
        return self

    def with_tool_call(self) -> PromptLogEntry:
        """What the tool call does: a Task's prompt, the file a read names, or another tool's command and path."""
        tool_input = self._payload.tool_input
        if self._payload.tool_name == "Task":
            return self.with_fields(tool_input, _TASK_INPUT_SHOWN)
        file = LoggedFile(tool_input.get("path") or tool_input.get("file_path") or "")
        if self._payload.tool_name in ("Read", "TabRead"):
            self._lines.append(f"read [{file.kind}]: {file.path}")
            return self
        self.with_fields(tool_input, _TOOL_INPUT_SHOWN)
        if file.path:
            self._lines.append(f"path [{file.kind}]: {file.path}")
        return self

    def with_fields(self, fields, names: tuple[str, ...]) -> PromptLogEntry:
        """Each of names that fields gives a value, with a preview of that value."""
        self._lines += [f"{name}: {self._preview(str(fields.get(name)))}" for name in names if fields.get(name)]
        return self

    def _header(self, event: str) -> str:
        stamp = LogTimestamp.now()
        chat = self._payload.conversation_id[:_SHOWN_ID_LENGTH]
        generation = self._payload.generation_id[:_SHOWN_ID_LENGTH]
        model = self._payload.get("model", "")
        return f"\n{'=' * _RULE_WIDTH}\n{stamp}  {event}  conv={chat}  gen={generation}  model={model}\n{'-' * _RULE_WIDTH}\n"

    def _attachment_line(self, attachment: dict) -> str:
        file = LoggedFile(attachment.get("file_path", ""))
        kind = "rule" if attachment.get("type", "file") == "rule" else file.kind
        return f"  [{kind}] {file.path}"

    def _preview(self, text) -> str:
        if text is None:
            return ""
        if not isinstance(text, str):
            text = json.dumps(text, indent=2)
        lines = text.splitlines()
        if len(lines) <= _PREVIEW_LINES and len(text) <= _PREVIEW_CHARS:
            return text
        head = "\n".join(lines[:_PREVIEW_LINES])[:_PREVIEW_CHARS]
        return f"{head}\n... [{len(lines)} lines, {len(text)} chars total]"


@noCatalog
@Hooks(disabled=True)
@agent_toolset
class PromptLog:
    """Audit what Cursor sends the model — one ``@Hook`` per event, each writing that event's entry to the log.

    The log is the file the toolset was made with; made with none, ``prompt-log.txt`` in the logs folder of the session
    the event works in, which each event reads, so the log follows a session switch."""

    def __init__(self, log: Path | None = None) -> None:
        self._log = log

    def log_for(self, payload: HookPayload) -> Path:
        """The file payload's entry is written to: the toolset's own, else the one in the session the event works in."""
        if self._log is not None:
            return self._log
        return payload.session.hook_log(_LOG_NAME)

    def _append(self, payload: HookPayload, entry: PromptLogEntry) -> None:
        path = self.log_for(payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        text = entry.text
        with open(path, "a", encoding="utf-8") as log:
            log.write(text if text.endswith("\n") else f"{text}\n")

    @hook("beforeSubmitPrompt")
    def before_submit_prompt(self, payload: HookPayload) -> dict:
        self._append(payload, PromptLogEntry("beforeSubmitPrompt", payload).with_prompt().with_attachments("ATTACHMENTS"))
        return {"continue": True}

    @hook("beforeReadFile")
    def before_read_file(self, payload: HookPayload) -> dict:
        entry = PromptLogEntry("beforeReadFile", payload).with_read_file().with_attachments("PROMPT ATTACHMENTS (bundled with read)")
        self._append(payload, entry)
        return {"permission": "allow"}

    @hook("preToolUse")
    def pre_tool_use(self, payload: HookPayload) -> dict:
        self._append(payload, PromptLogEntry(f"preToolUse:{payload.tool_name}", payload).with_tool_call())
        return {"permission": "allow"}

    @hook("subagentStart")
    def subagent_start(self, payload: HookPayload) -> dict:
        self._append(payload, PromptLogEntry("subagentStart", payload).with_fields(payload, _SUBAGENT_FIELDS_SHOWN))
        return {"permission": "allow"}

    @hook("afterAgentResponse")
    def after_agent_response(self, payload: HookPayload) -> dict:
        self._append(payload, PromptLogEntry("afterAgentResponse", payload).with_fields(payload, ("text",)))
        return {}
