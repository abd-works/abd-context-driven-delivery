"""A backlog item: an idea a person has added to the backlog folder as one markdown file."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.destination import data_field, identity, language_adapter
from harness.annotations.name import Name
from space.kanban.board import BACKLOG_COLUMN, Board, Card, Column
from space.kanban.ticket import Ticket
from harness.mcp.mcp_server import mcp


class BacklogItemNotFoundError(LookupError):
    """Raised when a tool names a backlog item the board does not show."""

    def __init__(self, backlog_item: str) -> None:
        super().__init__(f"no backlog item titled {backlog_item!r} on the board")


@identity("title")
@language_adapter(language="typescript")
@agent_toolset
class BacklogItem(Card):
    """Hold an idea not yet started. Starting it opens a ticket for it."""

    def __init__(self, path: Path, board: Board) -> None:
        super().__init__(board)
        self._path = path

    @classmethod
    @tool_subject
    def load(cls, backlog_item: str, *, project: Path | str) -> BacklogItem:
        """The backlog item titled backlog_item on the board of project."""
        found = Board.load(project).backlog_item(backlog_item)
        if found is None:
            raise BacklogItemNotFoundError(backlog_item)
        return found

    @classmethod
    @mcp
    @agent_tool
    @noSessionLog
    def create(cls, title: str, text: str = "", *, project: Path | str) -> BacklogItem:
        """Add an idea to the Backlog: one markdown file, with title as its heading and text under it."""
        board = Board.load(project)
        item = cls(board.sessions.backlog_folder / f"{Name(title).title_slug}.md", board)
        item._write(title, text)
        return item

    @classmethod
    def from_ticket(cls, ticket: Ticket) -> BacklogItem:
        """The item a ticket moved back into the Backlog becomes: its own folder, history and all, with its idea file
        inside."""
        board = ticket.board
        return cls(board.sessions.backlog_folder / ticket.name / f"{ticket.name}.md", board)

    def write_if_missing(self, title: str) -> None:
        """Give an item whose ticket never had an idea file one holding title, so it shows in the Backlog."""
        if not self._path.exists():
            self._write(title, "")

    def _write(self, title: str, text: str) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(f"# {title}\n\n{text}\n".rstrip() + "\n", encoding="utf-8")

    @property
    def path(self) -> Path:
        return self._path

    @property
    @data_field(key="path")
    def path_from_project(self) -> str:
        return self._board.repo.path_from_top(self._path)

    @property
    def title(self) -> str:
        """The item's first `# ` heading, or its file name in words."""
        for line in self._path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return self._path.stem.replace("-", " ").replace("_", " ").capitalize()

    @property
    def column(self) -> Column:
        return self._board.column(BACKLOG_COLUMN)

    @property
    @data_field
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
        """Start the backlog item titled backlog_item: open a ticket for it in Discovery, or bring back the ticket that was moved here, with its work. Its file goes into the ticket's session folder, text and all. scope is feature, story, or slice; path is the folder in the repository its session works on."""
        kept_folder = self._held_ticket_folder
        ticket = self._ticket_brought_back(kept_folder) if kept_folder.is_dir() else self._ticket_opened(scope, path)
        # An item kept inside its folder went back with the folder; a file beside it or on its own moves in now.
        if self._path.exists():
            ticket.session.keep_file(self._path)
        return ticket

    def move_next(self) -> Ticket:
        """A person's move forward out of the Backlog: starting the item."""
        return self.start()

    def move_previous(self) -> BacklogItem:
        """The Backlog is the first column, so an item has nowhere further back to go."""
        return self

    # The ticket folder an item holds: the folder it is kept in, or a folder of its name beside it.
    @property
    def _held_ticket_folder(self) -> Path:
        return self._path.parent if self._path.parent.name == self._path.stem else self._path.with_suffix("")

    def _ticket_brought_back(self, kept_folder: Path) -> Ticket:
        return self._board.ticket_of(self._board.sessions.load(kept_folder).reopen())

    def _ticket_opened(self, scope: str, path: str) -> Ticket:
        ticket = self._board.open_ticket(self.title, scope, "", path)
        return ticket.record(f"backlog {self._path}")
