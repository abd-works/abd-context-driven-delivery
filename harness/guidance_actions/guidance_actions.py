"""First-order guidance-action prelude — workspace, then the session's hanging turn and decisions."""

from __future__ import annotations

import json
import re
from typing import Any, Union

from agent_tools import AgentToolSet, agent_instructions, agent_tool, agent_toolset, instructions, tools
from installation.hooks.prompt_echo.prompt_echo import echo, show_ide_toast
from installation.hooks.hooks import Hook
from installation.mcp.mcp_server import mcp
from workspace.workspace import SessionModel, Turn, Workspace

# Runtime-safe alias: a Guidance list (or toolset refs) or a string to act on directly.
GuidanceArg = Union[str, list]


def listed(host) -> list:
    """Instantiate guidance hosts bound on ``host._tool_items`` for guidance-action recipe bodies."""
    if getattr(host, "_guidance_text", None) is not None:
        return []
    raw = getattr(host, "_tool_items", None) or []
    return AgentToolSet.instantiate_all(raw)


@agent_toolset
class GuidanceAction:
    """Open workspace if needed. Turn and decision records hang off the work session."""

    def __init__(self, path: str = ".", session: str = "") -> None:
        super().__init__()
        self.workspace = Workspace(str(path))
        self.workspace.load()
        self._session_name = session
        self._guidance_text: str | None = None
        self._tool_items: list = []
        if session:
            self._open_session(session, path=path)

    def _session(self):
        return self.workspace.current_work_session

    def _decisions(self):
        session = self._session()
        if session is not None:
            return session.decisions
        from record_decisions.record_decisions import RecordDecisions

        return RecordDecisions()

    def _turn(self):
        session = self._session()
        if session is not None:
            return session.turn
        return Turn(root=str(self.workspace.path))

    def _open_session(self, name: str = "", *, path: str = "") -> str:
        session_name = SessionModel.session_slug(name or self._session_name)
        session = self.workspace.open(
            name=session_name,
            path=path or self.workspace.path,
            isolate=session_name != SessionModel.DEFAULT_SESSION,
        )
        return session.branch_warning()

    def _bind_guidance(self, guidance: GuidanceArg | None = None) -> None:
        """String: run once. Not a string: iterate the guidance list."""
        if isinstance(guidance, str):
            self._guidance_text = guidance
            self._tool_items = []
            return
        self._guidance_text = None
        self._tool_items = list(guidance or [])

    def guidance_text(self) -> str | None:
        """The string to run this action on, when guidance was not a host list."""
        return self._guidance_text

    def listed(self) -> list:
        """Return the Guidance hosts bound on this run from the guidance argument."""
        return listed(self)

    def each(self, operation):
        """Run ``operation`` once on a guidance string, or once per Guidance host."""
        text = self._guidance_text
        if text is not None:
            return [operation(text)]
        return [operation(host) for host in self.listed()]

    def run(self, guidance: GuidanceArg, operation, *, action: str = "") -> list:
        """Begin the turn, run ``operation`` on the string or each host, then end."""
        self._bind_guidance(guidance)
        self.begin(guidance, action=action)
        results = self.each(operation)
        self.end()
        return results

    @mcp
    @agent_tool
    def open_workspace(self, name: str = "", path: str = "") -> str:
        """Open a work session on this workspace if one is not already open. Pass a name to open or switch to that session; returns the session name and any branch warning."""
        if self.workspace.current_work_session is not None and not name:
            return self.workspace.current_work_session.name
        warning = self._open_session(name or self._session_name, path=path)
        session_name = self.workspace.current_work_session.name
        if warning:
            return f"{warning}\n{session_name}"
        return session_name

    @echo
    @agent_instructions
    def begin(self, guidance: GuidanceArg | None = None, action: str = "") -> str:
        """Start a guidance action: open the workspace if needed, attach this action to the session turn, and load decision records. A session is optional — the action still runs without one."""
        self._bind_guidance(guidance)
        warning = ""
        if self.workspace.current_work_session is None:
            warning = self._open_session(self._session_name)
        session = self._session()
        if session is not None:
            try:
                session.turn
                if action:
                    session.turn.action = action
                instructions(self._decisions().record_decisions_session())
            except (AttributeError, TypeError):
                pass
            if not warning:
                warning = session.branch_warning()
        return warning

    @echo
    @Hook("postToolUse")
    def inject_rules(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Inject listed guidance hosts' rules markdown after this action returns."""
        if type(self).__name__ == "Document":
            return {}
        data = payload or {}
        if not self._payload_is_this_action(data):
            return {}
        self._bind_guidance_from_payload(data)
        parts = []
        for host in self.listed():
            text = (getattr(host, "rules_markdown", None) or "").strip()
            if text:
                parts.append(text)
        if not parts:
            return {}
        body = "\n\n".join(parts)
        label = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", type(self).__name__).lower()
        show_ide_toast(f"Rules \u2192 {label}")
        return {"additional_context": body}

    def _payload_is_this_action(self, payload: dict[str, Any]) -> bool:
        tool = str(payload.get("tool_name") or "").lower()
        if not tool:
            return False
        name = type(self).__name__
        snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()
        aliases = {name.lower(), snake, snake.replace("_", "-"), snake.replace("_", "")}
        return any(alias and alias in tool for alias in aliases)

    def _bind_guidance_from_payload(self, payload: dict[str, Any]) -> None:
        raw = payload.get("tool_input") or {}
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                raw = {}
        if not isinstance(raw, dict):
            return
        if "guidance" in raw:
            self._bind_guidance(raw.get("guidance"))

    @agent_instructions
    def end(self) -> str:
        """Close the guidance action by committing the session turn."""
        tools(self._turn().turn(utility="guidance_action"))
        return ""
