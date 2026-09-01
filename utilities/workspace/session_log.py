"""Session-scoped logging — explicit ``SessionLog.append`` (no ``@log`` decorator).

Utility package. Run requests may set ``session``. Events append under
``{AgentSession.folder}/logs/`` (``eval_log_dir``). Expand is logged by the
framework; run is logged by author calls to ``append``.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from agent.agent import AgentSession

F = TypeVar("F", bound=Callable[..., Any])


# Marker attrs copied from a base method onto a subclass override when absent.
# Action wrappers / chain annotations resolve via MRO in primitives.actions - not here.
_INHERITED_MARKER_ATTRS = (
    "_is_agent_instructions",
    "_is_agent_tool",
)


def inherit_annotations(
    child: Callable[..., Any] | None,
    parent: Callable[..., Any] | None,
) -> None:
    """Copy missing decorator markers from parent onto child (do not overwrite)."""
    if child is None or parent is None:
        return
    child_f = getattr(child, "__func__", child)
    parent_f = getattr(parent, "__func__", parent)
    if not callable(child_f) or not callable(parent_f):
        return
    for attr in _INHERITED_MARKER_ATTRS:
        if hasattr(child_f, attr):
            continue
        if hasattr(parent_f, attr):
            setattr(child_f, attr, getattr(parent_f, attr))


def inherit_annotations_from_bases(cls: type) -> None:
    """For each override on ``cls``, inherit markers from base definitions of the same name."""
    for name, child in list(cls.__dict__.items()):
        if name.startswith("__") or not callable(child):
            continue
        child_f = getattr(child, "__func__", child)
        for base in cls.__mro__[1:]:
            parent = base.__dict__.get(name)
            if parent is None or not callable(parent):
                continue
            parent_f = getattr(parent, "__func__", parent)
            if parent_f is child_f:
                continue
            inherit_annotations(child, parent)


@dataclass
class _LastPayload:
    event_index: int
    request: Any
    response: Any


class ISessionLog(ABC):
    """Append-only session event log bound to an ``AgentSession``."""

    @classmethod
    @abstractmethod
    def instance(cls) -> ISessionLog: ...

    @abstractmethod
    def bind(self, session: AgentSession) -> None: ...

    @abstractmethod
    def set_session(self, session: str | AgentSession | None) -> None: ...

    @abstractmethod
    def append(
        self,
        *,
        toolset: str,
        name: str,
        summary: str,
        ok: bool,
        error: str | None = None,
        role: str = "",
        kind: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None: ...

    @property
    @abstractmethod
    def log_dir(self) -> Path: ...

    @property
    @abstractmethod
    def session(self) -> AgentSession: ...


class SessionLog(ISessionLog):
    """Append-only session log with optional full payload files."""

    _instance: SessionLog | None = None

    @staticmethod
    def _agent_session_cls():
        from agent.agent import AgentSession

        return AgentSession

    def __init__(self, sessions_root: Path | None = None) -> None:
        # Test override only: when set, log_dir = sessions_root / session.name
        self._sessions_root = sessions_root
        self._session = self._resolve_agent_session("default")
        self._last_payload: _LastPayload | None = None
        self._event_count = 0
        self._explicit_binding = False

    @classmethod
    def instance(cls) -> SessionLog:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, log: SessionLog | None) -> None:
        cls._instance = log

    @property
    def session(self) -> AgentSession:
        return self._session

    @property
    def session_name(self) -> str:
        return self._session.name or "default"

    @property
    def log_dir(self) -> Path:
        if self._sessions_root is not None:
            return self._sessions_root / self.session_name
        return self._session.eval_log_dir

    @property
    def last_payload(self) -> _LastPayload | None:
        return self._last_payload

    def bind(self, session: AgentSession) -> None:
        """Bind an AgentSession; events go under ``session.eval_log_dir``."""
        self._session = session
        self._explicit_binding = True

    def set_session(self, session: str | AgentSession | None) -> None:
        """Bind an AgentSession, or resolve one from ``name`` under ``.agent_sessions/``."""
        agent_session_cls = SessionLog._agent_session_cls()
        if isinstance(session, agent_session_cls):
            self.bind(session)
            return
        name = (session or "").strip() or "default"
        self._session = self._resolve_agent_session(name)
        self._explicit_binding = True

    def _resolve_agent_session(self, name: str) -> AgentSession:
        agent_session_cls = SessionLog._agent_session_cls()
        effective = (name or "").strip() or "default"
        root = self._sessions_root if self._sessions_root is not None else Path.cwd().resolve()
        folder = root / ".agent_sessions" / effective
        context = root / ".context" if (root / ".context").is_dir() else root
        return agent_session_cls(name=effective, folder=folder, context_root=context)

    def append(
        self,
        *,
        toolset: str,
        name: str,
        summary: str,
        ok: bool,
        error: str | None = None,
        role: str = "",
        kind: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self._event_count += 1
        index = self._event_count
        self.log_dir.mkdir(parents=True, exist_ok=True)
        payload_ref = self._maybe_write_payloads(index, payload)
        effective_role = role or (kind if kind in ("expansion", "run") else "")
        line = self._format_event_line(
            toolset=toolset,
            name=name,
            summary=summary,
            ok=ok,
            error=error,
            role=effective_role,
            kind=kind,
            payload_ref=payload_ref,
        )
        with (self.log_dir / "events.log").open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        if payload is not None:
            self._last_payload = _LastPayload(
                event_index=index,
                request=payload.get("request"),
                response=payload.get("response"),
            )
        self._mirror_to_open_turn(
            toolset=toolset,
            name=name,
            summary=summary,
            ok=ok,
            error=error,
            role=effective_role,
        )

    def _mirror_to_open_turn(
        self,
        *,
        toolset: str,
        name: str,
        summary: str,
        ok: bool,
        error: str | None,
        role: str,
    ) -> None:
        open_turn = getattr(self._session, "open_turn", None)
        if open_turn is None:
            return
        from agent.agent import ToolCall

        open_turn.tool_calls.append(
            ToolCall(
                toolset=toolset,
                name=name,
                summary=summary,
                ok=ok,
                error=error or "",
                role=role,
            )
        )

    def _maybe_write_payloads(
        self, index: int, payload: dict[str, Any] | None
    ) -> str | None:
        # Verbose payload files are author-opt-in via payload only when writing
        # companion files is requested by passing payload and keeping last_payload.
        if payload is None:
            return None
        return None

    def _write_payload_files(self, index: int, payload: dict[str, Any]) -> tuple[str, str]:
        req_name = f"event-{index:03d}-request.yaml"
        res_name = f"event-{index:03d}-response.yaml"
        (self.log_dir / req_name).write_text(
            self._dump_yamlish(payload.get("request")),
            encoding="utf-8",
        )
        (self.log_dir / res_name).write_text(
            self._dump_yamlish(payload.get("response")),
            encoding="utf-8",
        )
        return req_name, res_name

    @staticmethod
    def _format_event_line(
        *,
        toolset: str,
        name: str,
        summary: str,
        ok: bool,
        error: str | None,
        role: str,
        kind: str | None,
        payload_ref: str | None,
    ) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        parts = [
            ts,
            f"toolset={toolset}",
            f"name={name}",
            f"ok={'true' if ok else 'false'}",
            f"summary={summary}",
        ]
        if kind:
            parts.insert(1, f"kind={kind}")
        if role:
            parts.append(f"role={role}")
        if error:
            parts.append(f"error={error}")
        if payload_ref:
            parts.append(f"payload={payload_ref}")
        return " ".join(parts)

    @staticmethod
    def _dump_yamlish(value: Any) -> str:
        try:
            import yaml

            return yaml.safe_dump(value, sort_keys=False)
        except (ImportError, TypeError, ValueError):
            return json.dumps(value, indent=2, default=str)


def summarize_mapping(data: dict[str, Any] | None, *, limit: int = 120) -> str:
    if not data:
        return ""
    parts = [f"{key}={_short(value)}" for key, value in data.items()]
    text = ",".join(parts)
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def _short(value: Any, *, max_len: int = 40) -> str:
    text = str(value).replace("\n", " ")
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "..."
