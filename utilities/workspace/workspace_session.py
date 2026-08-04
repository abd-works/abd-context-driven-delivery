"""Session — named sprint + workspace kit (working area, session area, context index)."""

from __future__ import annotations

import inspect
from datetime import date
from pathlib import Path

from primitives.actions.action import action
from primitives.instructions import Instruction
from primitives.instructions import instruction
from workspace.context_index import ContextIndex
from workspace.session import SessionPaths
from tools.tool import resource, tool

# Re-export for ``from workspace.workspace_session import SessionPaths.docs_dir``
__all__ = ["Session", "WorkspaceSession", "SessionPaths.docs_dir"]


class Session:
    """Sprint + workspace kit: working area, session area, and context index.

    - **path** — durable tool root (e.g. ``…/sandbox``)
    - **folder** — ``{path}/.context/sessions/{name}/``
    - **context_index** — text of ``{workspace_root}/.context/context-index.md`` when present
    """

    default_workspace_folder: str = "."
    context_index_key: str = ""

    def __init__(
        self,
        path: str | None = None,
        name: str | None = None,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        started: str | None = None,
        ended: str = "",
        outcome: str = "",
        handoff: str = "",
        *,
        format: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
        context_index_key: str | None = None,
        default_workspace_folder: str | None = None,
    ) -> None:
        self.format = format
        if context_index_key is not None:
            self.context_index_key = context_index_key
        if default_workspace_folder is not None:
            self.default_workspace_folder = default_workspace_folder
        self.workspace_root = workspace if workspace is not None else "."
        self._context_index: str | None = None

        load_name = session if session is not None else name
        if path is not None and session is None and name is not None:
            # Direct construction (SessionLog, load): path + name as fields — do not bind log
            self.path = path
            self.name = name
            self.goal = goal
            self.fidelities = fidelities
            self.contexts = contexts
            self.started = started if started is not None else date.today().isoformat()
            self.ended = ended
            self.outcome = outcome
            self.handoff = handoff
            return

        working = self._resolve_working_area(path)
        if load_name:
            loaded = type(self).load(working, load_name)
            self._take_from(loaded)
            self._bind_session_log()
            return

        self.path = working
        self.name = name
        self.goal = goal
        self.fidelities = fidelities
        self.contexts = contexts
        self.started = started if started is not None else date.today().isoformat()
        self.ended = ended
        self.outcome = outcome
        self.handoff = handoff
        self._bind_session_log()

    def _take_from(self, other: Session) -> None:
        self.path = other.path
        self.name = other.name
        self.goal = other.goal
        self.fidelities = other.fidelities
        self.contexts = other.contexts
        self.started = other.started
        self.ended = other.ended
        self.outcome = other.outcome
        self.handoff = other.handoff

    def _bind_session_log(self) -> None:
        if self.name:
            from workspace.session_log import SessionLog

            SessionLog.instance().bind(self)

    def _resolve_working_area(self, working_area: str | None) -> str:
        if working_area is not None:
            return working_area
        key = self.context_index_key or ""
        indexed = ContextIndex.lookup_root(self.workspace_root, key) if key else None
        if indexed:
            return ContextIndex.root_glob_to_path(self.workspace_root, indexed)
        folder = self.default_workspace_folder or "."
        if folder in (".", ""):
            return self.workspace_root
        return str(Path(self.workspace_root) / folder)

    @property
    def module_dir(self) -> Path:
        return Path(inspect.getfile(type(self))).resolve().parent

    @property
    def domain_slug(self) -> str:
        return "workspace_session"

    # -- Paths ---------------------------------------------------------------

    @property
    def folder(self) -> Path:
        if not self.name:
            raise ValueError(
                "session name is not set - confirm working path and session slug with the "
                "user, then call create_session before grill/sketch/handoff"
            )
        return Path(self.path) / ".context" / "sessions" / self.name

    @property
    def log(self) -> Path:
        """Directory for append-only session event logs."""
        return self.folder / "logs"

    @property
    def session_md(self) -> Path:
        return self.folder / "session.md"

    @property
    def context_index(self) -> str:
        """Cached index text, or empty string if none / not loaded yet."""
        return self._context_index or ""

    @instruction
    def session_guidance(self) -> Instruction: ...

    @property
    @resource
    def active(self) -> Session:
        """active"""
        return self

    def to_dict(self) -> dict[str, str | None]:
        folder: str | None
        try:
            folder = str(self.folder)
        except ValueError:
            folder = None
        return {
            "path": self.path,
            "name": self.name,
            "folder": folder,
            "goal": self.goal or None,
            "fidelities": self.fidelities or None,
            "contexts": self.contexts or None,
            "started": self.started or None,
            "ended": self.ended or None,
            "outcome": self.outcome or None,
            "handoff": self.handoff or None,
        }

    def __repr__(self) -> str:
        return f"Session(path={self.path!r}, name={self.name!r})"

    # -- session.md IO -------------------------------------------------------

    @classmethod
    def load(cls, path: str, name: str) -> Session:
        """Load from ``{path}/.context/sessions/{name}/session.md`` when present."""
        session = cls(path=path, name=name)
        md = session.session_md
        if not md.is_file():
            return session
        return cls._parse(md.read_text(encoding="utf-8"), path=path, name=name)

    def ensure_started(
        self,
        *,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
    ) -> Path:
        """Create sprint folder + session.md Start when missing; refresh fields if provided."""
        if not self.name:
            raise ValueError("session name is required to create a sprint folder")
        if goal:
            self.goal = goal
        if fidelities:
            self.fidelities = fidelities
        if contexts:
            self.contexts = contexts
        if not self.started:
            self.started = date.today().isoformat()
        self.folder.mkdir(parents=True, exist_ok=True)
        if not self.session_md.is_file():
            self.session_md.write_text(self._render(), encoding="utf-8")
        elif goal or fidelities or contexts:
            if not self.ended:
                self.session_md.write_text(self._render(), encoding="utf-8")
        return self.session_md

    def close(self, *, outcome: str = "", handoff: str = "handoff.md") -> Path:
        """Write End section (and handoff link) into session.md."""
        if not self.session_md.is_file():
            self.ensure_started()
        self.ended = date.today().isoformat()
        if handoff:
            self.handoff = handoff
        if not outcome and self.handoff:
            outcome = "handoff written"
        if outcome:
            self.outcome = outcome
        self.session_md.write_text(self._render(), encoding="utf-8")
        return self.session_md

    def _render(self) -> str:
        lines = [
            f"# Session: {self.name}",
            "",
            "## Start",
            "",
            f"- **date:** {self.started}",
            f"- **path:** {self.path}",
            f"- **goal:** {self.goal or '(unset)'}",
            f"- **fidelities:** {self.fidelities or '(unset)'}",
            f"- **contexts:** {self.contexts or '(unset)'}",
            "",
        ]
        if self.ended or self.outcome or self.handoff:
            lines.extend(
                [
                    "## End",
                    "",
                    f"- **ended:** {self.ended or '(unset)'}",
                    f"- **outcome:** {self.outcome or '(unset)'}",
                    f"- **handoff:** {self.handoff or '(unset)'}",
                    "",
                ]
            )
        return "\n".join(lines)

    @classmethod
    def _parse(cls, text: str, *, path: str, name: str) -> Session:
        fields: dict[str, str] = {}
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("- **") or ":**" not in stripped:
                continue
            key, _, value = stripped.partition(":**")
            key = key.removeprefix("- **").strip()
            value = value.strip()
            if value.startswith("(") and value.endswith(")"):
                value = ""
            fields[key] = value
        return cls(
            path=fields.get("path") or path,
            name=name,
            goal=fields.get("goal", ""),
            fidelities=fields.get("fidelities", ""),
            contexts=fields.get("contexts", ""),
            started=fields.get("date", "") or date.today().isoformat(),
            ended=fields.get("ended", ""),
            outcome=fields.get("outcome", ""),
            handoff=fields.get("handoff", ""),
        )

    # -- One entry action ----------------------------------------------------

    @action
    def open(self) -> str:
        """Open the workspace session in one step: set path (durable root), ensure the sprint exists (create if missing), load context index if present, record this tool's root when keyed. Follow session_guidance. Scope durable work to path and sprint docs to folder."""
        self.session_guidance
        self.active
        self.ensure_session()
        self.read_context_index()
        self.record_context_root()
        return (
            "Workspace open. "
            "durable root = path; "
            "sprint docs = folder; "
            "context index loaded when present."
        )

    # -- Tools (usable alone; also pulled in by open) ------------------------

    @tool
    def ensure_session(
        self,
        name: str = "",
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
    ) -> str:
        """ensure_session"""
        effective_path = path.strip() or self.path
        effective_name = name.strip() or (self.name or "")
        if not effective_name:
            return (
                "need session name — confirm working path and kebab slug with the user, "
                "then call ensure_session (or create_session) before grill/sketch"
            )
        if (
            self.name == effective_name
            and self.path == effective_path
            and self.session_md.is_file()
        ):
            self._bind_session_log()
            return str(self.session_md.resolve())
        loaded = type(self).load(effective_path, effective_name)
        if loaded.session_md.is_file():
            self._take_from(loaded)
            if goal or fidelities or contexts:
                self.ensure_started(
                    goal=goal, fidelities=fidelities, contexts=contexts
                )
        else:
            self.path = effective_path
            self.name = effective_name
            self.goal = goal
            self.fidelities = fidelities
            self.contexts = contexts
            self.ended = ""
            self.outcome = ""
            self.handoff = ""
            self.started = date.today().isoformat()
            self.ensure_started(
                goal=goal, fidelities=fidelities, contexts=contexts
            )
        self._bind_session_log()
        return str(self.session_md.resolve())

    @tool
    def create_session(
        self,
        name: str,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
    ) -> str:
        """create_session"""
        return self.ensure_session(
            name=name,
            goal=goal,
            fidelities=fidelities,
            contexts=contexts,
            path=path,
        )

    @tool
    def close_session(self, outcome: str = "", handoff: str = "handoff.md") -> str:
        """close_session"""
        md = self.close(outcome=outcome, handoff=handoff)
        return str(md.resolve())

    @tool
    def read_context_index(self) -> str:
        """read_context_index"""
        path = ContextIndex.context_index_path(self.workspace_root)
        if not path.is_file():
            self._context_index = None
            return f"missing: {path.as_posix()} (no roots recorded yet)"
        text = path.read_text(encoding="utf-8")
        self._context_index = text
        return text

    @tool
    def record_context_root(self, root: str = "", note: str = "") -> str:
        """record_context_root"""
        key = getattr(self, "context_index_key", "") or ""
        if not key:
            return "skipped: this toolset has no context_index_key"
        working = root if root else self.path
        glob = ContextIndex.path_to_root_glob(self.workspace_root, working)
        path = ContextIndex.upsert_entry(self.workspace_root, key, glob, note=note)
        if path.is_file():
            self._context_index = path.read_text(encoding="utf-8")
        return str(path.resolve())


# Back-compat alias for imports / decorator chain targets
WorkspaceSession = Session
