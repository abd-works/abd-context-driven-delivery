"""Session-scoped logging for @log-marked tools and actions.

Utility package. Run requests may set ``session`` and ``log`` (full|verbose|off).
Events append under ``{session.path}/.context/sessions/{session.name}/logs/``.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from workspace.workspace_session import Session

F = TypeVar("F", bound=Callable[..., Any])


def log(func: F) -> F:
    """Mark a @tool or @action so SessionLog records its run/expansion."""
    func._is_logged = True  # type: ignore[attr-defined]
    return func


def is_logged(func: Callable[..., Any] | None) -> bool:
    if func is None:
        return False
    target = getattr(func, "__func__", func)
    return bool(getattr(target, "_is_logged", False))


# Marker attrs copied from a base method onto a subclass override when absent.
# Action wrappers / chain annotations resolve via MRO in primitives.actions - not here.
_INHERITED_MARKER_ATTRS = ("_is_logged",)


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
    """Append-only session event log bound to a ``Session``."""

    @classmethod
    @abstractmethod
    def instance(cls) -> ISessionLog: ...

    @abstractmethod
    def bind(self, session: Session) -> None: ...

    @abstractmethod
    def set_session(self, session: str | Session | None) -> None: ...

    @abstractmethod
    def apply_log_control(self, control: str | None) -> None: ...

    @abstractmethod
    def append(
        self,
        *,
        kind: str,
        toolset: str,
        name: str,
        summary: str,
        ok: bool,
        error: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None: ...

    @property
    @abstractmethod
    def log_dir(self) -> Path: ...

    @property
    @abstractmethod
    def session(self) -> Session: ...


class SessionLog(ISessionLog):
    """Append-only session log with optional full payload files."""

    _instance: SessionLog | None = None

    @staticmethod
    def _session_cls():
        from workspace.workspace_session import Session

        return Session

    def __init__(self, sessions_root: Path | None = None) -> None:
        # Test override only: when set, log_dir = sessions_root / session.name
        self._sessions_root = sessions_root
        self._session = SessionLog._session_cls()(path=".", name="default")
        self._verbose = False
        self._last_payload: _LastPayload | None = None
        self._event_count = 0

    @classmethod
    def instance(cls) -> SessionLog:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, log: SessionLog | None) -> None:
        cls._instance = log

    @property
    def session(self) -> Session:
        return self._session

    @property
    def session_name(self) -> str:
        return self._session.name or "default"

    @property
    def log_dir(self) -> Path:
        if self._sessions_root is not None:
            return self._sessions_root / self.session_name
        return self._session.log

    @property
    def verbose(self) -> bool:
        return self._verbose

    @property
    def last_payload(self) -> _LastPayload | None:
        return self._last_payload

    def bind(self, session: Session) -> None:
        """Bind a Context Session; events go under ``session.log``."""
        self._session = session

    def set_session(self, session: str | Session | None) -> None:
        """Bind a Session, or a name (legacy) as ``Session(path=".", name=...)``."""
        Session = SessionLog._session_cls()
        if isinstance(session, Session):
            self.bind(session)
            return
        name = (session or "").strip() or "default"
        self._session = Session(path=".", name=name)

    def apply_log_control(self, control: str | None) -> None:
        if control is None:
            return
        value = str(control).strip().lower()
        if value == "full":
            self._flush_last_payload()
            self._verbose = True
            return
        if value == "verbose":
            self._verbose = True
            return
        if value == "off":
            self._verbose = False
            return
        raise ValueError(f"unsupported log control {control!r}; use full, verbose, or off")

    def append(
        self,
        *,
        kind: str,
        toolset: str,
        name: str,
        summary: str,
        ok: bool,
        error: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self._event_count += 1
        index = self._event_count
        self.log_dir.mkdir(parents=True, exist_ok=True)
        payload_ref = self._maybe_write_payloads(index, payload)
        line = self._format_event_line(
            kind=kind,
            toolset=toolset,
            name=name,
            summary=summary,
            ok=ok,
            error=error,
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

    def _maybe_write_payloads(
        self, index: int, payload: dict[str, Any] | None
    ) -> str | None:
        if not self._verbose or payload is None:
            return None
        req_name, res_name = self._write_payload_files(index, payload)
        return f"{req_name},{res_name}"

    def _flush_last_payload(self) -> None:
        if self._last_payload is None:
            return
        self.log_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "request": self._last_payload.request,
            "response": self._last_payload.response,
        }
        req_name, res_name = self._write_payload_files(self._last_payload.event_index, payload)
        with (self.log_dir / "events.log").open("a", encoding="utf-8") as fh:
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            fh.write(
                f"{ts} kind=control name=log_full "
                f"payload={req_name},{res_name} summary=retroactive-full\n"
            )

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
        kind: str,
        toolset: str,
        name: str,
        summary: str,
        ok: bool,
        error: str | None,
        payload_ref: str | None,
    ) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        parts = [
            ts,
            f"kind={kind}",
            f"toolset={toolset}",
            f"name={name}",
            f"ok={'true' if ok else 'false'}",
            f"summary={summary}",
        ]
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


def member_is_logged(owner: type | Any, name: str) -> bool:
    """True when the named member - or a base-class definition - carries @log."""
    cls = owner if isinstance(owner, type) else type(owner)
    for base in cls.__mro__:
        member = base.__dict__.get(name)
        if member is None or not callable(member):
            continue
        if is_logged(member):
            return True
    return False

