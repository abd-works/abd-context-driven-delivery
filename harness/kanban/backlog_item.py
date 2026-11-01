"""A backlog item: an idea a person has added to the backlog folder as one markdown file."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.kanban.board import BACKLOG_FOLDER, Board, Card, Column, name_of
from harness.kanban.ticket import Ticket
from harness.mcp.mcp_server import mcp
from space.session import Session


class BacklogItemNotFoundError(LookupError):
    """Raised when a tool names a backlog item the board does not show."""

    def __init__(self, backlog_item: str) -> None:
        super().__init__(f"no backlog item titled {backlog_item!r} on the board")


@agent_toolset
class BacklogItem(Card):
    """Hold an idea not yet started. Starting it opens a ticket for it."""

    def __init__(self, path: Path, board: Board) -> None:
        super().__init__(board)
        self._path = Path(path)

    @classmethod
    @tool_subject
    def load(cls, backlog_item: str) -> BacklogItem:
        found = Board.current().backlog_item(backlog_item)
        if found is None:
            raise BacklogItemNotFoundError(backlog_item)
        return found

    @classmethod
    @mcp
    @agent_tool
    @noSessionLog
    def add(cls, title: str, text: str = "") -> BacklogItem:
        """Add an idea to the Backlog: one markdown file, with title as its heading and text under it."""
        return cls._written(Board.current(), name_of(title), title, text)

    @classmethod
    def holding(cls, ticket: Ticket, board: Board) -> BacklogItem:
        """The item a ticket moved back into the Backlog waits in; its ticket's folder sits beside it."""
        return cls._written(board, ticket.name, ticket.title, "")

    @classmethod
    def _written(cls, board: Board, file_name: str, title: str, text: str) -> BacklogItem:
        folder = board.sessions_folder / BACKLOG_FOLDER
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{file_name}.md"
        path.write_text(f"# {title}\n\n{text}\n".rstrip() + "\n", encoding="utf-8")
        return cls(path, board)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def title(self) -> str:
        """The item's first `# ` heading, or its file name in words."""
        for line in self._path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return self._path.stem.replace("-", " ").replace("_", " ").capitalize()

    @property
    def column(self) -> Column:
        return self._board.column("Backlog")

    @property
    def text(self) -> str:
        """The file's content after its heading."""
        content = self._path.read_text(encoding="utf-8")
        heading = f"# {self.title}"
        return content.split(heading, 1)[-1].strip() if heading in content else content.strip()

    @property
    def last_activity(self) -> str:
        """When the item's file last changed; a backlog item has no session log to read."""
        return self._timestamp(datetime.fromtimestamp(self._path.stat().st_mtime).astimezone())

    @mcp
    @agent_tool
    @noSessionLog
    def start(self, scope: str = "feature", path: str = "") -> Ticket:
        """Start the backlog item titled backlog_item: open a ticket for it in Discovery, or bring back the ticket that was moved here, with its work. scope is feature, story, or slice; path is the folder in the repository its session works on."""
        held = self._held_ticket_folder
        ticket = self._ticket_brought_back(held) if held.is_dir() else self._ticket_opened(scope, path)
        self._path.unlink()
        return ticket

    def move_next(self) -> Ticket:
        """A person's move forward out of the Backlog: starting the item."""
        return self.start()

    def move_previous(self) -> BacklogItem:
        """The Backlog is the first column, so an item has nowhere further back to go."""
        return self

    def to_json(self) -> dict[str, Any]:
        return {**super().to_json(), "text": self.text, "path": str(self._path)}

    @property
    def _held_ticket_folder(self) -> Path:
        return self._path.with_suffix("")

    def _ticket_brought_back(self, held: Path) -> Ticket:
        session = Session.at(held, self._board.repo_root).move_to(self._board.sessions_folder)
        return Ticket(session, self._board)

    def _ticket_opened(self, scope: str, path: str) -> Ticket:
        ticket = Ticket.new(self.title, scope, "", path)
        ticket.record(f"backlog {self._path}")
        return ticket
