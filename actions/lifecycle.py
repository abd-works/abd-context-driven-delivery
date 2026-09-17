"""First-order action prelude — workspace, then the session's hanging turn and decisions."""

from __future__ import annotations

from primitives.harness.toolset_loader import ToolsetLoader
from agent_tools import agent_instructions, agent_tool, agent_toolset, instructions, tools
from workspace.workspace import SessionModel, Turn, Workspace


def listed(host) -> list:
    """Instantiate toolset refs bound on ``host._tool_items`` for lifecycle recipe bodies."""
    raw = getattr(host, "_tool_items", None) or []
    return ToolsetLoader.instance().instantiate_all(raw)


@agent_toolset
class LifecycleAction:
    """Open workspace if needed. Turn and decision records hang off the work session."""

    def __init__(self, path: str = ".", session: str = "") -> None:
        super().__init__()
        self.workspace = Workspace(str(path))
        self.workspace.load()
        self._session_name = session
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

    def listed(self) -> list:
        return listed(self)

    @agent_tool
    def open_workspace(self, name: str = "", path: str = "") -> str:
        """Open the workspace if it is not already open. /open-workspace"""
        if self.workspace.current_work_session is not None and not name:
            return self.workspace.current_work_session.name
        warning = self._open_session(name or self._session_name, path=path)
        session_name = self.workspace.current_work_session.name
        if warning:
            return f"{warning}\n{session_name}"
        return session_name

    @agent_instructions
    def begin(recipe, tools: list | None = None, action: str = "") -> str:
        """Open the workspace if it is not already open. The turn hangs off the work session — it is already there when the session is awake. Decision records hang off the work session. Session is optional — actions work without one."""
        toolset = recipe.toolset
        warning = ""
        if toolset.workspace.current_work_session is None:
            warning = toolset._open_session(toolset._session_name)
        session = toolset._session()
        if session is not None:
            try:
                session.turn
                if action:
                    session.turn.action = action
                instructions(toolset._decisions().record_decisions_session())
            except (AttributeError, TypeError):
                pass
            if not warning:
                warning = session.branch_warning()
        return warning

    @agent_instructions
    def end(recipe) -> str:
        """Commit the turn via ``/turn`` (``Turn.turn``)."""
        tools(recipe.toolset._turn().turn(utility="lifecycle"))
        return ""
