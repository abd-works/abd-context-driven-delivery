"""Kanban — the session board as tools any IDE's agent can call through the cdd MCP server."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog
from harness.kanban.board import Board
from harness.mcp.mcp_server import mcp

SESSIONS_FOLDER = ".sessions"


@agent_toolset
class Kanban:
    """Show every work session as a ticket on a kanban, and move tickets through the stages."""

    # The board is read after every cdd call and every prompt, so its tools stay out of the session log;
    # a pull still writes its own `pull <stage>` line there.

    def __init__(self, project: str = "") -> None:
        self._project = project

    @mcp
    @agent_tool
    @noSessionLog
    def board(self) -> dict[str, Any]:
        """Return the session board: Backlog, Discovery, Specification, Implementation, and Complete, with every ticket's progress through Generate, Validate, and Review, and the active ticket."""
        return self._board().to_json()

    @mcp
    @agent_tool
    @noSessionLog
    def pull(self, ticket: str) -> dict[str, Any]:
        """Pull ticket into the next stage. Only a ticket whose stage is done can be pulled; a done ticket in Implementation is closed instead."""
        board = self._board()
        board.ticket(ticket).pull()
        return board.ticket(ticket).to_json()

    @mcp
    @agent_tool
    @noSessionLog
    def start(self, backlog_item: str, scope: str = "feature") -> dict[str, Any]:
        """Start the backlog item titled backlog_item: open a ticket for it in Discovery. scope is feature, story, or slice."""
        board = self._board()
        item = next(entry for entry in board.backlog_items if entry.title == backlog_item)
        return item.start(scope).to_json()

    @mcp
    @agent_tool
    @noSessionLog
    def close(self, ticket: str) -> dict[str, Any]:
        """Close ticket: its session folder moves to closed/ and it shows in Complete."""
        return self._board().ticket(ticket).close().to_json()

    @mcp
    @agent_tool
    @noSessionLog
    def archive(self, ticket: str) -> str:
        """Archive ticket: its session folder moves to _archive/ and it leaves the board."""
        self._board().ticket(ticket).archive()
        return f"{ticket} archived."

    def _board(self) -> Board:
        project = Path(self._project or os.environ.get("CDD_PROJECT") or os.getcwd()).resolve()
        return Board.load(project / SESSIONS_FOLDER)
