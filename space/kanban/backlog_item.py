"""A backlog item: an idea a person has added to the backlog folder as one markdown file."""

from __future__ import annotations

import os
import subprocess
import sys
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
from space.session.session import SESSION_FILE
from harness.mcp.mcp_server import mcp


def open_with_system(path: Path) -> None:
    """Hand path to the app this computer opens its kind of file with, as a double-click in the file browser does."""
    if sys.platform == "win32":
        os.startfile(path)  # noqa: S606 - a file of the Backlog, opened as the person's own file browser would
    else:
        subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", str(path)], check=True, timeout=30)


class BacklogNestingError(ValueError):
    """Raised when a backlog item cannot be made another's child: the Backlog nests one level, in plain idea folders."""

    def __init__(self, item: str, parent: str, reason: str) -> None:
        super().__init__(f"{item} cannot be a child of {parent}: {reason}")


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
        return self._held_ticket_folder.name if self._holds_ticket else ""

    @property
    @data_field
    def parent(self) -> str:
        """The title of the item whose folder keeps this one's file, as its child; empty for an item of its own."""
        parent_file = self._parent_file
        return self._board.make_backlog_item(parent_file).title if parent_file is not None else ""

    @property
    @data_field
    def is_stacked(self) -> bool:
        """Whether it shows inside its parent's card rather than as a card of its own: a child does."""
        return self._parent_file is not None

    @property
    @data_field
    def children(self) -> list[BacklogItem]:
        """The items whose files its folder keeps beside its own: stacked inside its card, and started with it as its
        children. Sent whole, since a stacked child shows in no column."""
        if not self._is_kept_in_own_folder or self._holds_ticket:
            return []
        return [item for item in self._board.backlog_items if item.path.parent == self._path.parent and item.path != self._path]

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
        """Start the backlog item titled backlog_item: open a ticket for it in Discovery, or bring back the ticket that was moved here, with its work. Its file goes into the ticket's session folder, text and all, and the change is committed on main and pushed. Its children start with it, each as a story ticket that is its child. scope is feature, story, or slice; path is the folder in the repository its session works on. Then run ticket.activate to open the ticket's own worktree, and do its work in a chat started there (start_session with cwd set to the ticket's worktree), not in this chat."""
        children = self.children
        ticket = self._ticket_brought_back(self._held_ticket_folder) if self._holds_ticket else self._ticket_opened(scope, path)
        # An item kept inside its folder went back with the folder; a file beside it or on its own moves in now.
        if self._path.exists():
            ticket.session.keep_file(self._path)
        for child in children:
            child.start("story", path).reassign_parent(ticket)
        self._remove_emptied_folder()
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
    def open_file(self) -> BacklogItem:
        """Open the backlog item titled backlog_item's file in the app this computer opens markdown files with, as the link under its text on the board does."""
        open_with_system(self._path)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def move_before(self, other: BacklogItem) -> BacklogItem:
        """Move the backlog item just above other in the Backlog, as dragging it there does; the Backlog keeps that order, in .sessions/_board.json. Committed on main and pushed."""
        super().move_before(other)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def move_after(self, other: BacklogItem) -> BacklogItem:
        """Move the backlog item just below other in the Backlog, as dragging it onto other's bottom edge does; the Backlog keeps that order, in .sessions/_board.json. Committed on main and pushed."""
        column = self.column.place_after(self, other)
        self._board.sessions.saves.later(f"sessions: move {self.key} after {other.key} in {column.name}")
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def nest_under(self, parent: BacklogItem) -> BacklogItem:
        """Make the backlog item titled backlog_item a child of parent, as dragging it onto parent's card in the Backlog does: its file moves into parent's folder, beside the file of parent's own name that holds parent's text; a parent kept as one file becomes that folder first. The Backlog nests one level: an item with children of its own cannot become a child, a child cannot take one, and neither can an item kept with a ticket's work. Committed on main and pushed."""
        if parent.path != self._path and parent.path.parent == self._path.parent and parent._is_kept_in_own_folder:
            return self
        self._refuse_nesting_under(parent)
        self._move_file_into(parent._folder_for_children(), f"sessions: nest {self.title} under {parent.title} in the Backlog")
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def leave_parent(self) -> BacklogItem:
        """Take the backlog item titled backlog_item out of its parent, as dragging it out of its parent's card onto the Backlog does: its file moves back to the Backlog folder, an item of its own again. Committed on main and pushed."""
        if self._parent_file is not None:
            self._move_file_into(self._board.sessions.backlog_folder, f"sessions: take {self.title} out of its parent in the Backlog")
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
        return self._path.parent if self._is_kept_in_own_folder else self._path.with_suffix("")

    # A folder holds a ticket's work when it keeps a session's record; a parent's folder keeps only ideas.
    @property
    def _holds_ticket(self) -> bool:
        return (self._held_ticket_folder / SESSION_FILE).is_file()

    @property
    def _is_kept_in_own_folder(self) -> bool:
        return self._path.parent.name == self._path.stem

    # The file of the parent whose folder keeps this item's file, beside the parent's own; none for an item of its own.
    @property
    def _parent_file(self) -> Path | None:
        folder = self._path.parent
        if folder.parent != self._board.sessions.backlog_folder or self._is_kept_in_own_folder:
            return None
        return folder / f"{folder.name}.md"

    def _refuse_nesting_under(self, parent: BacklogItem) -> None:
        folder = parent._held_ticket_folder
        reason = (
            "it is the same item" if parent.path == self._path
            else "it has children of its own" if self.children
            else "it is a child itself" if parent.is_stacked
            else "it is kept with a ticket's work" if self._holds_ticket or parent._holds_ticket
            else f"{parent.title}'s folder already keeps a file called {self._path.name}" if (folder / self._path.name).exists() or self._path.stem == folder.name
            else ""
        )
        if reason:
            raise BacklogNestingError(self.title, parent.title, reason)

    # The folder that keeps this item's children: its own folder, made from its one file the first time it takes one.
    def _folder_for_children(self) -> Path:
        if not self._is_kept_in_own_folder:
            folder = self._path.with_suffix("")
            folder.mkdir()
            self._move_file_into(folder, "")
        return self._path.parent

    # Move the item's file, never its idea's only copy lost, into folder; a parent's folder left empty goes with it.
    def _move_file_into(self, folder: Path, saved_as: str) -> None:
        left = self._path.parent
        moved = folder / self._path.name
        self._path.replace(moved)
        self._path = moved
        self._idea = IdeaFile(moved)
        if left != self._board.sessions.backlog_folder and not any(left.iterdir()):
            left.rmdir()
        self._board.reread()
        if saved_as:
            self._board.sessions.saves.later(saved_as)

    def _remove_emptied_folder(self) -> None:
        folder = self._held_ticket_folder
        if self._is_kept_in_own_folder and folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
        self._board.reread()

    def _ticket_brought_back(self, kept_folder: Path) -> Ticket:
        return self._board.ticket_of(self._board.sessions.load(kept_folder).reopen())

    def _ticket_opened(self, scope: str, path: str) -> Ticket:
        ticket = self._board.open_ticket(self.title, scope, "", path)
        ticket.work.record(f"backlog {self._path}")
        return ticket
