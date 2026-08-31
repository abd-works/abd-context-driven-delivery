# @toolset-manifest python -m tools manifest context_tools.actions.lifecycle:LifecycleAction
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""First-order action prelude — workspace, then the session's hanging turn and decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.agent import AgentSession, InMemoryRepo, Repo, Turn, Workspace
from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import agent_tool


class _ExpandOnlyTurn:
    """Expand-only stand-in so ``self._turn().finish_turn()`` still lists the tool."""

    @agent_tool
    def finish_turn(self, **_: Any) -> None:
        """Finish the turn that hangs off the agent session."""
        return None


@agentic_toolset
class LifecycleAction:
    """Open workspace if needed. Turn and decision records hang off the agent session."""

    def __init__(self, path: str = ".", session: str = "") -> None:
        super().__init__()
        self._workspace_path = str(path)
        self._session_name = session
        self.workspace = self._build_workspace(path)
        self._agent_session: AgentSession | None = None
        if session:
            self._open_session(name=session, path=path)

    def _build_workspace(self, path: str) -> Workspace:
        root = Path(path).resolve()
        repo = InMemoryRepo(root, Repo.Worktree(root, "main"))
        workspace = Workspace(path=root, repos=[repo], primary_repo=repo)
        self._load_path_overrides(workspace, root)
        return workspace

    @staticmethod
    def _load_path_overrides(workspace: Workspace, root: Path) -> None:
        index = root / ".context" / "context-index.md"
        if not index.is_file():
            return
        for line in index.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            parts = [part.strip() for part in stripped.strip("|").split("|")]
            if len(parts) < 3:
                continue
            tool, fidelity, row_path = parts[0], parts[1], parts[2]
            if tool in {"tool", "---", "*(none)*"} or tool.startswith("---"):
                continue
            if not tool or not fidelity or not row_path:
                continue
            workspace.upsert_path(tool, fidelity, row_path)

    def _resolve_context_root(self, workspace_path: Path) -> Path:
        override = self.workspace.lookup_path("agent", "contextRoot")
        if override is not None:
            return override
        root = workspace_path.resolve()
        context = root / ".context"
        if context.is_dir():
            return context
        return root

    def _open_session(self, name: str = "", path: str = "") -> AgentSession:
        working = Path((path or self._workspace_path or ".").strip()).resolve()
        effective_name = (name or self._session_name or "").strip()
        folder = working / ".agent_sessions" / (effective_name or "default")
        session = self.workspace.open(
            name=effective_name or None,
            context_root=self._resolve_context_root(working),
            open_existing=folder.is_dir(),
        )
        self._agent_session = session
        return session

    def _session(self) -> AgentSession | None:
        return self._agent_session

    def _decisions(self):
        session = self._session()
        if session is not None:
            return session.decisions
        from record_decisions.record_decisions import RecordDecisions

        return RecordDecisions()

    def _turn(self) -> Turn | Any:
        session = self._session()
        if session is not None:
            return session.turn
        return _ExpandOnlyTurn()

    @agent_tool
    def open_workspace(self, name: str = "", path: str = "") -> str:
        """Open the workspace if it is not already open. /open-workspace"""
        if self._agent_session is not None and not name:
            return self._agent_session.name
        return self._open_session(name=name or self._session_name, path=path).name

    @agent_instructions
    def begin(self, tools: list | None = None, action: str = "") -> str:
        """Open the workspace if it is not already open. The turn hangs off the agent session — it is already there when the session is awake. Decision records hang off the agent session."""
        if self._agent_session is None:
            self._open_session()
        session = self._session()
        turn = session.turn
        if action:
            turn._action = action
        self._decisions().record_decisions_session()
        return ""

    @agent_instructions
    def end(self) -> str:
        """Finish the turn that hangs off the agent session."""
        self._turn().finish_turn()
        return ""
