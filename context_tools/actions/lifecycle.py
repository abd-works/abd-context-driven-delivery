"""First-order action prelude — workspace, then the session's hanging turn and decisions."""

from __future__ import annotations

from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import agent_tool
from workspace.workspace import SessionModel, Workspace


@agentic_toolset
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
        from workspace.workspace import Turn

        # Expand-only stand-in so ``self._turn().finish_turn()`` still lists the tool
        # when no work session is open (Turn() would probe git for session/).
        return Turn.__new__(Turn)

    def _open_session(self, name: str = "", *, path: str = "") -> str:
        session_name = SessionModel.session_slug(name or self._session_name)
        session = self.workspace.open(
            name=session_name,
            path=path or self.workspace.path,
            isolate=session_name != SessionModel.DEFAULT_SESSION,
        )
        return session.branch_warning()

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
    def begin(self, tools: list | None = None, action: str = "") -> str:
        """Open the workspace if it is not already open. The turn hangs off the work session — it is already there when the session is awake. Decision records hang off the work session. Session is optional — actions work without one."""
        warning = ""
        if self.workspace.current_work_session is None:
            warning = self._open_session(self._session_name)
        session = self._session()
        if session is not None:
            try:
                session.turn
                if action:
                    session.turn.action = action
                self._decisions().record_decisions_session()
            except (AttributeError, TypeError):
                pass
            if not warning:
                warning = session.branch_warning()
        return warning

    @agent_instructions
    def end(self) -> str:
        """Finish the turn that hangs off the work session."""
        self._turn().finish_turn()
        return ""
