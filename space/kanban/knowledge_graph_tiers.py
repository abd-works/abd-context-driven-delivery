"""The Python tier the knowledge graph scenarios of Integrate Practice Content Editor Apps replay on.

The domain tier hands a scenario's steps the project's sessions and board on a throwaway project. The Graph app reaches
the graph through its generated adapter on the project it names (`?project=`, the `X-CDD-Project` header), so every
call it makes works in the session open in that project, as every board call does: the steps reach that graph through
`ToolCall(project=...)`, as the cdd server answers the app's calls.
"""

from __future__ import annotations

from types import SimpleNamespace

from harness.agent_tools.tool_call import ToolCall
from space.kanban.board import Board
from space.kanban.session_board_examples import SessionsProject
from space.session.sessions import Sessions


class DomainTier:
    """The sessions, the board and their graphs on a throwaway project, with nothing between a step and the domain."""

    name = "domain"

    def open(self) -> SimpleNamespace:
        project = SessionsProject(mocks_git=True)
        return SimpleNamespace(
            project=project,
            sessions=Sessions.of_project(project.root),
            board=lambda: Board.load(project.root),
            app_call=lambda: ToolCall(project=project.root),
        )

    def close(self, world: SimpleNamespace) -> None:
        world.project.close()
