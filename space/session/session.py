"""Session — in-memory graph, practice guidance, and repo ``.sessions/{slug}/`` folders."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from harness.graph.graph import Graph
    from harness.guidance.guidance import PracticeGuidance
    from workspace.legacy.workspace import WorkSession, Workspace


class Session:
    """Process session: graph, practices, and the active work-session folder on disk."""

    def __init__(self, workspace: str | Path = ".") -> None:
        self._workspace_path = str(Path(workspace))
        self._knowledge_graph = None
        self._practices = None
        self._workspace_parent: Workspace | None = None

    @property
    def workspace_path(self) -> str:
        return self._workspace_path

    def _repository_root(self) -> Path:
        from space.repo import Repo

        found = Repo(self._workspace_path).find_root()
        if found is not None:
            return Path(found)
        return Path(self._workspace_path).resolve()

    def _workspace(self) -> Workspace:
        if self._workspace_parent is None:
            from workspace.legacy.workspace import Workspace

            self._workspace_parent = Workspace(path=str(self._repository_root()))
        return self._workspace_parent

    @property
    def current(self) -> WorkSession:
        """Active named session, or implicit ``default`` when none was opened yet."""
        workspace = self._workspace()
        if workspace.current_work_session is not None:
            return workspace.current_work_session

        from harness.hooks.session_logs import SessionLogs
        from workspace.legacy.workspace import SessionModel

        repo_root = self._repository_root()
        logs = SessionLogs(repo_root)
        active_marker = repo_root / SessionLogs.ACTIVE
        if not active_marker.is_file():
            logs.ensure_default_session()
            slug = SessionModel.DEFAULT_SESSION
            isolate = False
        else:
            slug = logs.active_session_name()
            isolate = slug != SessionModel.DEFAULT_SESSION
        return self.open(
            name=slug,
            path=str(repo_root),
            isolate=isolate,
        )

    def open(
        self,
        name: str = "",
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
        *,
        isolate: bool = True,
    ) -> WorkSession:
        """Open a work session — creates ``{repo}/.sessions/{slug}/`` like legacy workspace."""
        from workspace.legacy.workspace import SessionModel

        slug = SessionModel().session_slug(name)
        if slug == SessionModel.DEFAULT_SESSION:
            isolate = False
        working = (path or "").strip() or str(self._repository_root())
        return self._workspace().open_work_session(
            name=slug,
            goal=goal,
            fidelities=fidelities,
            contexts=contexts,
            path=working,
            isolate=isolate,
        )

    @property
    def knowledge_graph(self):
        if self._knowledge_graph is None:
            from harness.graph.graph import Graph

            self._knowledge_graph = Graph()
        return self._knowledge_graph

    @knowledge_graph.setter
    def knowledge_graph(self, graph) -> None:
        self._knowledge_graph = graph

    @property
    def practices(self) -> dict[str, PracticeGuidance]:
        if self._practices is None:
            self._practices = self._instantiate_practices()
        return self._practices

    @practices.setter
    def practices(self, practices) -> None:
        self._practices = practices

    def reset(self) -> None:
        self._knowledge_graph = None
        self._practices = None
        self._workspace_parent = None

    def _instantiate_practices(self) -> dict[str, PracticeGuidance]:
        from practices.bdd.bdd import Bdd
        from practices.clean_engineering.clean_engineering import CleanEngineering
        from practices.ddd.ddd import Ddd
        from practices.stories.stories import Stories
        from practices.ux.ux import Ux

        return {
            "stories": Stories(),
            "clean_engineering": CleanEngineering(),
            "ddd": Ddd(),
            "bdd": Bdd(),
            "ux": Ux(),
        }
