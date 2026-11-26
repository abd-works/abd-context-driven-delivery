"""A backlog item: an idea a person has added to the backlog folder as one markdown file."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from harness.agent_tools import agent_toolset
from harness.annotations.annotation import hosted_only
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.installation.data_class import data_field, identity, language_adapter
from harness.installation.files import command
from space.kanban.board import BACKLOG_COLUMN, Board, Card, Column
from space.kanban.card_name import BacklogItemTakenError, CardName
# Imported for real, not only for type checking: the backlog-item.start_under tool reads its parent's type to load the
# ticket the call names.
from space.kanban.ticket import Ticket
from space.session.idea_file import IdeaFile
from harness.process.log_timestamp import LogTimestamp
from space.session.session_log import LogLine
from harness.mcp.mcp_annotations import mcp


class BacklogNestingError(ValueError):
    """Raised when a backlog item cannot be made another's child: the Backlog nests one level, in plain idea folders."""

    def __init__(self, child: str, parent: str, reason: str) -> None:
        super().__init__(f"{child} cannot be a child of {parent}: {reason}")


@hosted_only
class BacklogOrderTools:
    """A backlog item's published moves within the Backlog's order: just above or just below another item, as dragging it
    there does. The Backlog keeps that order, in .sessions/_board.json."""

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
        super().move_after(other)
        return self


@identity("title")
@language_adapter(language="typescript")
@agent_toolset
class BacklogItem(BacklogOrderTools, Card):
    """Hold an idea not yet started. Starting it opens a ticket for it."""

    def __init__(self, path: Path, board: Board) -> None:
        super().__init__(board)
        # Where the idea's file lies in the Backlog, which moves it.
        self._place = board.backlog_folder.place_of(path)

    @classmethod
    @tool_subject
    def load(cls, backlog_item: str, *, project: Path | str, call: ToolCall | None = None) -> BacklogItem:
        """The backlog item titled backlog_item on the board of project, read for call."""
        return Board.load(project, call).reads.backlog_item_called(backlog_item)

    @classmethod
    @mcp
    @command(name="backlog")
    @agent_tool
    @noSessionLog
    def create(cls, title: str, text: str = "", *, project: Path | str) -> BacklogItem:
        """Add an idea to the Backlog, as the + on the board's Backlog column does: one markdown file, with title as its heading and text under it, committed on main and pushed. A title that gives no file name, or the name of an idea already in the Backlog, is refused, so no idea is written over. Run as the backlog slash command, the words after the command are the title, and any further lines its text."""
        board = Board.load(project)
        file = board.sessions.backlog_folder / f"{CardName(title).for_new_card()}.md"
        # An idea's file is its only copy, kept as that file or inside a folder of its name once it has children.
        if file.exists() or file.with_suffix("").exists():
            raise BacklogItemTakenError(title, board.repo.path_from_top(file))
        item = cls(file, board)
        item._idea.write(title, text)
        board.sessions.saves.later(f"sessions: add {title} to the Backlog")
        return item

    @classmethod
    def from_ticket(cls, ticket: Ticket) -> BacklogItem:
        """The item a ticket moved back into the Backlog becomes: its own folder, history and all, with its idea file
        inside, made holding its title when the ticket never had one."""
        board = ticket.board
        item = cls(board.sessions.backlog_folder / ticket.name / f"{ticket.name}.md", board)
        # A ticket that never had an idea file gets one holding its title, so it shows in the Backlog.
        if not item._idea.exists():
            item._idea.write(ticket.title, "")
        return item

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
        return self._place.ticket_folder.name if self._place.holds_ticket else ""

    @property
    @data_field
    def parent(self) -> str:
        """The title of the item whose folder keeps this one's file, as its child; empty for an item of its own."""
        parent_file = self._place.parent_file
        return self._board.placement.make_backlog_item(parent_file).title if parent_file is not None else ""

    @property
    @data_field
    def is_stacked(self) -> bool:
        """Whether it shows inside its parent's card rather than as a card of its own: a child does."""
        return self._place.parent_file is not None

    @property
    @data_field
    def children(self) -> list[BacklogItem]:
        """The items whose files its folder keeps beside its own: stacked inside its card, and started with it as its
        children. Sent whole, since a stacked child shows in no column."""
        if not self._place.is_in_own_folder or self._place.holds_ticket:
            return []
        return [item for item in self._board.backlog_items if item.path.parent == self._path.parent and item.path != self._path]

    @property
    @data_field
    def parent_choices(self) -> list[str]:
        """The titles of the items a person can drop it on to make it their child: any it is not already the child of,
        and that nest_under would not refuse."""
        return [item.title for item in self._board.backlog_items if item.title != self.parent and not self._nesting_refusal(item)]

    @property
    @data_field
    def text(self) -> str:
        """The file's content after its heading."""
        return self._idea.text

    @property
    def last_activity(self) -> str:
        """When the item's file last changed; a backlog item has no session log to read."""
        return str(LogTimestamp(datetime.fromtimestamp(self._path.stat().st_mtime).astimezone()))

    @mcp
    @agent_tool
    @noSessionLog
    def start(self, scope: str = "feature", path: str = "") -> Ticket:
        """Start the backlog item titled backlog_item: open a ticket for it in Discovery, or bring back the ticket that was moved here, with its work. Its file goes into the ticket's session folder, text and all, and the change is committed on main and pushed. Its children start with it, each as a story ticket that is its child. scope is feature, story, or slice; path is the folder in the repository its session works on. Then run ticket.activate to open the ticket's own worktree, and do its work in a chat started there (start_session with cwd set to the ticket's worktree), not in this chat."""
        children = self.children
        ticket = self._ticket_brought_back(self._place.ticket_folder) if self._place.holds_ticket else self._ticket_opened(scope, path)
        # An item kept inside its folder went back with the folder; a file beside it or on its own moves in now.
        if self._path.exists():
            ticket.session.folder.keep_file(self._path)
        for child in children:
            child.start("story", path).reassign_parent(ticket)
        for kept_child in self._kept_children_of(ticket):
            kept_child.start()
        self._place.remove_emptied_folder()
        self._board.placement.reread()
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
    def delete(self) -> None:
        """Delete the backlog item titled backlog_item, as Delete on its selected card does: its markdown file goes, or, for an item kept in a folder of its own name (a parent with its children, or a ticket moved back with its work), that whole folder. A child's file goes alone, and its parent stays. A file or folder a running program holds open refuses the delete with everything still in place. Committed on main and pushed."""
        title = self.title
        self._place.remove()
        self._moved(f"sessions: delete {title} from the Backlog")

    @mcp
    @agent_tool
    @noSessionLog
    def nest_under(self, parent: BacklogItem) -> BacklogItem:
        """Make the backlog item titled backlog_item a child of parent, as dragging it onto parent's card in the Backlog does: its file moves into parent's folder, beside the file of parent's own name that holds parent's text; a parent kept as one file becomes that folder first. The Backlog nests one level: an item with children of its own cannot become a child, a child cannot take one, and neither can an item kept with a ticket's work. Committed on main and pushed."""
        if parent.path != self._path and parent.path.parent == self._path.parent and parent._place.is_in_own_folder:
            return self
        self._refuse_nesting_under(parent)
        self._place.move_under(parent._place)
        self._moved(f"sessions: nest {self.title} under {parent.title} in the Backlog")
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def leave_parent(self) -> BacklogItem:
        """Take the backlog item titled backlog_item out of its parent, as dragging it out of its parent's card onto the Backlog does: its file moves back to the Backlog folder, an item of its own again. Committed on main and pushed."""
        if self._place.parent_file is not None:
            self._place.move_out()
            self._moved(f"sessions: take {self.title} out of its parent in the Backlog")
        return self

    # Its file as it lies now, which a move can have taken elsewhere.
    @property
    def _path(self) -> Path:
        return self._place.file

    # The idea the item holds: its heading is the item's title, and the text under it its text.
    @property
    def _idea(self) -> IdeaFile:
        return IdeaFile(self._place.file)

    def _refuse_nesting_under(self, parent: BacklogItem) -> None:
        reason = self._nesting_refusal(parent)
        if reason:
            raise BacklogNestingError(self.title, parent.title, reason)

    def _nesting_refusal(self, parent: BacklogItem) -> str:
        """Why this item cannot become parent's child; empty when it can. The Backlog nests one level, in plain idea
        folders."""
        folder = parent._place.ticket_folder
        return (
            "it is the same item" if parent.path == self._path
            else "it has children of its own" if self.children
            else "it is a child itself" if parent.is_stacked
            else "it is kept with a ticket's work" if self._place.holds_ticket or parent._place.holds_ticket
            else f"{parent.title}'s folder already keeps a file called {self._path.name}" if (folder / self._path.name).exists() or self._path.stem == folder.name
            else ""
        )

    # Its file moved: the board reads its cards again, and the move is committed on main and pushed.
    def _moved(self, saved_as: str) -> None:
        self._board.placement.reread()
        self._board.sessions.saves.later(saved_as)

    def _kept_children_of(self, ticket: Ticket) -> list[BacklogItem]:
        """The Backlog's items kept with the work of a ticket that names ticket as its parent: the children that went
        to the Backlog with it, which come back with it."""
        held = self._board.sessions.held
        kept = [item for item in self._board.backlog_items if item._place.holds_ticket]
        return [item for item in kept if held.load(item._place.ticket_folder).hierarchy.parent == ticket.name]

    def _ticket_brought_back(self, kept_folder: Path) -> Ticket:
        return self._board.placement.ticket_of(self._board.sessions.held.load(kept_folder).folder.reopen())

    def _ticket_opened(self, scope: str, path: str) -> Ticket:
        ticket = self._board.placement.open_ticket(self.title, scope, path)
        ticket.work.record(LogLine("backlog", paths=[self._path]))
        return ticket
