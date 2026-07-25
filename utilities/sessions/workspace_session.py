"""Workspace binding for ContextTool — path defaults, context-index, session bout."""

from __future__ import annotations

from pathlib import Path

from primitives.instructions import Instruction
from primitives.instructions import _path_for_name
from primitives.instructions import instruction
from sessions.context_index import (
    context_index_path,
    lookup_root,
    path_to_root_glob,
    root_glob_to_path,
    upsert_entry,
)
from sessions.session import Session
from sessions.session_log import SessionLog
from tools.tool import resource, tool

_KIT_DIR = Path(__file__).resolve().parent


def _bind_session_log(session: Session) -> None:
    if session.name:
        SessionLog.instance().bind(session)


def _resolve_working_path(
    cls: type,
    workspace: str,
    path: str | None,
) -> str:
    if path is not None:
        return path
    key = getattr(cls, "context_index_key", "") or ""
    indexed = lookup_root(workspace, key) if key else None
    if indexed:
        return root_glob_to_path(workspace, indexed)
    folder = getattr(cls, "default_workspace_folder", ".") or "."
    if folder in (".", ""):
        return workspace
    return str(Path(workspace) / folder)


class WorkspaceSession:
    """Workspace root, path defaults, context-index, and session bout."""

    default_workspace_folder: str = "."
    context_index_key: str = ""

    def __init__(
        self,
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        super().__init__()
        self.format = format
        self.workspace = workspace if workspace is not None else "."
        working = _resolve_working_path(type(self), self.workspace, path)
        if session:
            self._session = Session.load(working, session)
        else:
            self._session = Session(path=working)
        _bind_session_log(self._session)

    @instruction(override=True)
    def session_guidance(self) -> str:
        """Kit-local session layout (``sessions.md`` § Session)."""
        return Instruction(_path_for_name(_KIT_DIR, "session"), _KIT_DIR).expand()

    @property
    @resource
    def session(self) -> Session:
        """session"""
        return self._session

    @tool
    def read_context_index(self) -> str:
        """read_context_index"""
        path = context_index_path(self.workspace)
        if not path.is_file():
            return f"missing: {path.as_posix()} (no roots recorded yet)"
        return path.read_text(encoding="utf-8")

    @tool
    def record_context_root(self, root: str = "", note: str = "") -> str:
        """record_context_root"""
        key = type(self).context_index_key
        if not key:
            return "skipped: this toolset has no context_index_key"
        working = root if root else self._session.path
        glob = path_to_root_glob(self.workspace, working)
        path = upsert_entry(self.workspace, key, glob, note=note)
        return str(path.resolve())

    @tool
    def create_session(
        self,
        name: str,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
    ) -> str:
        """create_session"""
        self._session = Session(
            path=self._session.path,
            name=name,
            goal=goal,
            fidelities=fidelities,
            contexts=contexts,
        )
        md = self._session.ensure_started(
            goal=goal, fidelities=fidelities, contexts=contexts
        )
        _bind_session_log(self._session)
        if type(self).context_index_key:
            self.record_context_root(note="create_session")
        return str(md.resolve())

    @tool
    def close_session(self, outcome: str = "", handoff: str = "handoff.md") -> str:
        """close_session"""
        md = self._session.close(outcome=outcome, handoff=handoff)
        return str(md.resolve())
