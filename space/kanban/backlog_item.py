"""A backlog item: an idea a person has added to the backlog folder as one markdown file."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.data_class import data_field, identity, language_adapter
from harness.annotations.name import Name
from space.kanban.board import BACKLOG_COLUMN, Board, Card, Column
# Imported for real, not only for type checking: the backlog-item.start_under tool reads its parent's type to load the
# ticket the call names.
from space.kanban.ticket import Ticket
from space.session.idea_file import IdeaFile
from harness.mcp.mcp_server import mcp



@identity("title")
@language_adapter(language="typescript")
@agent_toolset
class BacklogItem(Card):
    """Hold an idea not yet started. Starting it opens a ticket for it."""

    def __init__(self, path: Path, board: Board) -> None:
        super().__init__(board)
        self._path = path
        # The idea the item holds: its heading is the item's title, and the text under it its text.
        self._idea = IdeaFile(path)

    @classmethod
    @tool_subject
    def load(cls, backlog_item: str, *, project: Path | str) -> BacklogItem:
        """The backlog item titled backlog_item on the board of project."""
        return Board.load(project).backlog_item_called(backlog_item)

    @classmethod
    @mcp
    @agent_tool
    @noSessionLog
    def create(cls, title: str, text: str = "", *, project: Path | str) -> BacklogItem:
        """Add an idea to the Backlog: one markdown file, with title as its heading and text under it, committed on main and pushed."""
        board = Board.load(project)
        item = cls(board.sessions.backlog_folder / f"{Name(title).title_slug}.md", board)
        item._idea.write(title, text)
        board.sessions.saves.later(f"sessions: add {title} to the Backlog")
        return item

    @classmethod
    def from_ticket(cls, ticket: Ticket) -> BacklogItem:
        """The item a ticket moved back into the Backlog becomes: its own folder, history and all, with its idea file
        inside."""
        board = ticket.board
        return cls(board.sessions.backlog_folder / ticket.name / f"{ticket.name}.md", board)

    def write_if_missing(self, title: str) -> None:
        """Give an item whose ticket never had an idea file one holding title, so it shows in the Backlog."""
        if not self._idea.exists():
            self._idea.write(title, "")

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
        return self._idea.heading or self._path.stem.replace("-", " ").replace("_", " ").capitalize()

    @property
    def key(self) -> str:
        return self.title

    @property
    @data_field(reference=True)
    def column(self) -> Column:
        """The Backlog, sent by its name, which with the item's title is where the board shows it."""
        return self._board.column(BACKLOG_COLUMN)

    @property
    @data_field
    def ticket(self) -> str:
        """The name of the ticket whose folder the item holds, a ticket moved back with its work; empty for an idea that
        has never been a ticket."""
        kept_folder = self._held_ticket_folder
        return kept_folder.name if kept_folder.is_dir() else ""

    @property
    @data_field
    def text(self) -> str:
        """The file's content after its heading."""
        return self._idea.text

    @property
    def last_activity(self) -> str:
        """When the item's file last changed; a backlog item has no session log to read."""
        return self._timestamp(datetime.fromtimestamp(self._path.stat().st_mtime).astimezone())

    @mcp
    @agent_tool
    @noSessionLog
    def start(self, scope: str = "feature", path: str = "") -> Ticket:
        """Start the backlog item titled backlog_item: open a ticket for it in Discovery, or bring back the ticket that was moved here, with its work. Its file goes into the ticket's session folder, text and all, and the change is committed on main and pushed. scope is feature, story, or slice; path is the folder in the repository its session works on. Then run ticket.activate to open the ticket's own worktree, and do its work in a chat started there (start_session with cwd set to the ticket's worktree), not in this chat."""
        kept_folder = self._held_ticket_folder
        ticket = self._ticket_brought_back(kept_folder) if kept_folder.is_dir() else self._ticket_opened(scope, path)
        # An item kept inside its folder went back with the folder; a file beside it or on its own moves in now.
        if self._path.exists():
            ticket.session.keep_file(self._path)
        return ticket

    @mcp
    @agent_tool
    @noSessionLog
    def start_under(self, parent: Ticket) -> Ticket:
        """Start the backlog item titled backlog_item as a child of parent, as dropping it on parent's card does: its ticket opens in Discovery, or comes back with its work, and takes parent as its parent. Committed on main and pushed."""
        return self.start().reassign_parent(parent)

    @mcp
    @agent_tool
    @noSessionLog
    def edit_text(self, text: str) -> BacklogItem:
        """Write text as the backlog item's idea, under its heading in its file, which keeps its title. Committed on main and pushed."""
        self._idea.rewrite_text(text)
        self._board.sessions.saves.later(f"sessions: edit {self.title}'s text in the Backlog")
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def move_before(self, other: BacklogItem) -> BacklogItem:
        """Move the backlog item just above other in the Backlog, as dragging it there does; the Backlog keeps that order, in .sessions/_board.json. Committed on main and pushed."""
        super().move_before(other)
        return self

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
        ticket.work.record(f"backlog {self._path}")
        return ticket
