"""The session kanban: a board of columns, the stages work moves through, and the backlog."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.destination import data_field, language_adapter
from harness.mcp.mcp_server import mcp
from cdd_guidance.practices.stages import DISCOVERY, IMPLEMENTATION, SPECIFICATION
from space.session import Session
from space.work_state import board_checkout

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
    from harness.guidance.rule import Rule
    from harness.kanban.backlog_item import BacklogItem
    from harness.kanban.ticket import Ticket
    from space.repo.repo import Repo

BACKLOG_COLUMN = "Backlog"
COMPLETE_COLUMN = "Complete"
GENERATE = "generate"
VALIDATE = "validate"
REVIEW = "review"
# What every fidelity goes through in its stage, named as the session log names them.
STAGE_ACTIONS = (GENERATE, VALIDATE, REVIEW)
LEAVE_COMMIT = "commit"
LEAVE_PUSH = "push"
LEAVE_MERGE = "merge"
OPEN_BRANCH = "branch"
OPEN_WORKTREE = "worktree"
FORGE = "https://forge.abdworks.net/abd-context-driven-delivery"
FIDELITIES_WITHOUT_PAGE = ("ddd-model", "bdd-realization")


class ColumnNotFoundError(LookupError):
    """Raised when a caller names a column the board does not have. It names the column."""

    def __init__(self, column: str) -> None:
        self.column = column
        super().__init__(f"no column named {column!r} on the board")


class PracticeNotFoundError(LookupError):
    """Raised when a caller names a practice, such as clean_engineering, that the board or ticket does not have. It
    names the practice and what was searched for it."""

    def __init__(self, practice: str, within: str) -> None:
        self.practice = practice
        self.within = within
        super().__init__(f"no practice named {practice!r} on {within}")


class FidelityNotFoundError(LookupError):
    """Raised when a caller names a fidelity, such as stories-story_map, that a ticket or practice does not have. It
    names the fidelity and the ticket or practice searched, so a caller can say which request was refused."""

    def __init__(self, fidelity: str, within: str) -> None:
        self.fidelity = fidelity
        self.within = within
        super().__init__(f"no fidelity named {fidelity!r} on {within}")


@language_adapter(language="typescript")
@agent_toolset
class Board:
    """Show every work session as a ticket on a kanban: Backlog, Discovery, Specification, Implementation, and Complete."""

    # The board is read after every cdd call and every prompt, so its tools stay out of the session log.
    # Every ticket is in exactly one column; the board stores no ticket state.

    _built_practices: ClassVar[tuple[PracticeGuidance, ...] | None] = None

    def __init__(self, repo: Repo, practices: list[PracticeGuidance]) -> None:
        self._repo = repo
        self._practices = list(practices)
        self._columns = self._build_columns()

    @classmethod
    def load(cls, repo_root: Path | str) -> Board:
        """The board of the repository at repo_root, with every practice chosen."""
        from space.repo.repo import Repo

        return cls(Repo(repo_root), list(cls._every_practice()))

    @classmethod
    @tool_subject
    def current(cls) -> Board:
        """The board of the project the running call names. One cdd server answers every chat, so it reads the
        project from each request's X-CDD-Project header and runs the call inside working_on(project). A chat in a
        ticket's worktree reads the board of the project's main checkout, where every ticket's session lives."""
        return cls.load(board_checkout())

    @classmethod
    def _every_practice(cls) -> tuple[PracticeGuidance, ...]:
        """Built once per process: the practices do not change between tool calls, and building them took about 30 ms
        on every call."""
        if cls._built_practices is None:
            from bdd.bdd import Bdd
            from clean_engineering.clean_engineering import CleanEngineering
            from ddd.ddd import Ddd
            from stories.stories import Stories
            from ux.ux import Ux

            Board._built_practices = (Stories(), Ddd(), Ux(), CleanEngineering(), Bdd())
        return Board._built_practices

    @property
    def repo(self) -> Repo:
        return self._repo

    @property
    @data_field
    def project(self) -> str:
        return self._repo.root.name

    def worktree_of(self, ticket: str) -> Path | None:
        """The folder of the worktree that has ticket's branch checked out; none when it has no worktree."""
        return self._worktrees.get(ticket)

    @cached_property
    def _worktrees(self) -> dict[str, Path]:
        """Each branch's worktree, listed once per board read: the board is read after every call. A project that is no
        git clone has none."""
        if not self._repo.is_clone:
            return {}
        return {tree.branch.name: tree.path for tree in self._repo.list_worktrees() if tree.branch is not None}

    @property
    def practices(self) -> list[PracticeGuidance]:
        return list(self._practices)

    @property
    @data_field
    def columns(self) -> list[Column]:
        return list(self._columns)

    @property
    def tickets(self) -> list[Ticket]:
        from harness.kanban.ticket import Ticket

        return [Ticket(session, self) for session in self._repo.sessions()]

    @property
    def backlog_items(self) -> list[BacklogItem]:
        from harness.kanban.backlog_item import BacklogItem

        folder = self._repo.backlog_folder
        if not folder.is_dir():
            return []
        # An item is a file in the Backlog, or a folder holding a file of its own name: a ticket moved back keeps its
        # whole folder, history and all. A folder beside a file of its name is that file's ticket, not a second item.
        files = list(folder.glob("*.md"))
        kept = [entry / f"{entry.name}.md" for entry in folder.iterdir() if entry.is_dir() and not (folder / f"{entry.name}.md").exists()]
        return [BacklogItem(path, self) for path in sorted([*files, *(path for path in kept if path.is_file())], key=lambda path: path.stem)]

    @property
    def cards(self) -> list[Card]:
        return [*self.tickets, *self.backlog_items]

    @property
    def active(self) -> Ticket | None:
        """The ticket of the session saved as open; none while main is, since main is not on the board."""
        return self.ticket(Session.active_name(self._repo.root))

    @property
    @data_field(key="active")
    def active_name(self) -> str | None:
        active = self.active
        return active.name if active else None

    def column(self, name: str) -> Column:
        found = next((column for column in self._columns if column.name == name), None)
        if found is None:
            raise ColumnNotFoundError(name)
        return found

    def ticket(self, name: str) -> Ticket | None:
        return next((ticket for ticket in self.tickets if ticket.name == name), None)

    def backlog_item(self, title: str) -> BacklogItem | None:
        return next((item for item in self.backlog_items if item.title == title), None)

    @mcp
    @agent_tool
    @noSessionLog
    def show(self) -> Board:
        """Return the session board: Backlog, Discovery, Specification, Implementation, and Complete, with every ticket's progress through Generate, Validate, and Review, and the active ticket."""
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def activate(self, ticket: str, leaving: list[str] | None = None, opening: list[str] | None = None) -> Ticket:
        """Make ticket the current session. leaving names what to do with the active ticket's work first: commit, push, merge. opening names what to create for ticket: branch, worktree."""
        chosen = self._named_ticket(ticket)
        active = self.active
        if active is not None and active.name != chosen.name:
            self.leave(active, leaving or [])
        if OPEN_BRANCH in (opening or []):
            self.repo.switch_branch(chosen.name)
        if OPEN_WORKTREE in (opening or []):
            self.repo.switch_worktree(chosen.name)
        Session.switch(chosen.name, repo_path=self.repo.root)
        return chosen

    def leave(self, ticket: Ticket, leaving: list[str]) -> None:
        """Do what leaving names with ticket's work: commit, push, merge. Only on its own branch, checked out, because
        those steps act on whatever is checked out."""
        if not leaving or not self._is_on_its_branch(ticket.name):
            return
        if LEAVE_COMMIT in leaving or LEAVE_PUSH in leaving:
            self.repo.push_commit(f"{ticket.name}: leave session", sync_remote=LEAVE_PUSH in leaving)
        if LEAVE_MERGE in leaving:
            self.repo.close_branch(ticket.name)

    @mcp
    @agent_tool
    @noSessionLog
    def open_worktree(self, ticket: str) -> Ticket:
        """Open ticket's own worktree beside the repository, creating its branch when missing: the folder its chat works in, named as its worktree. The open session is left as it is."""
        name = self._named_ticket(ticket).name
        self.repo.branch_named(name).open_in_worktree()
        return Board.load(self.repo.root)._named_ticket(name)

    @mcp
    @agent_tool
    @noSessionLog
    def workspace(self, ticket: str) -> Workspace:
        """Say whether ticket already has its branch and its worktree, so activating it offers only what is missing, and whether the active ticket being left is on a branch of its own, so its work can be committed, pushed, and merged."""
        name = self._named_ticket(ticket).name
        active = self.active
        return Workspace(self.repo.has_branch(name), self.worktree_of(name) is not None, active is not None and self._is_on_its_branch(active.name))

    def _named_ticket(self, name: str) -> Ticket:
        from harness.kanban.ticket import TicketNotFoundError

        found = self.ticket(name)
        if found is None:
            raise TicketNotFoundError(name)
        return found

    def _is_on_its_branch(self, name: str) -> bool:
        """Whether the repository has the branch name checked out; a commit lands on whatever is checked out."""
        return self.repo.has_branch(name) and self.repo.current_branch == name

    @mcp
    @agent_tool
    @noSessionLog
    def set_wip_limit(self, stage: str, limit: int) -> Board:
        """Set how many tickets stage holds before its count shows as over its limit."""
        limits = {**self._saved_wip_limits, stage: limit}
        self._repo.board_file.write_text(json.dumps({"wip_limits": limits}), encoding="utf-8")
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def folders(self, path: str = "") -> list[str]:
        """List the folders inside path, a folder in the repository (its top when empty), as paths from the project, for a person choosing a workpath or a practice root. Installed packages, caches, and hidden folders hold no one's work, so they are left out."""
        return sorted(entry.path for entry in self._repo.file_manager.list(path).folders)

    @mcp
    @agent_tool
    @noSessionLog
    def help(self, practice: str, fidelity: str = "") -> Help:
        """Return the overview, guidance, and rules of practice, or of its fidelity when one is named, with the stage that fidelity belongs to and its page on the forge."""
        guidance = self.practice(practice)
        subject = self._fidelity_of(guidance, fidelity) if fidelity else guidance
        return Help(practice, fidelity, subject.stage.capitalize() if fidelity else "", subject, self._forge_page(practice, fidelity))

    def practice(self, key: str) -> PracticeGuidance:
        """The board's practice whose folder name is key, such as clean_engineering."""
        found = next((entry for entry in self._practices if entry.key == key), None)
        if found is None:
            raise PracticeNotFoundError(key, "the board")
        return found

    def wip_limit(self, stage: str) -> int:
        return self._saved_wip_limits.get(stage, Session.default_wip)

    @property
    def _saved_wip_limits(self) -> dict[str, int]:
        path = self._repo.board_file
        return json.loads(path.read_text(encoding="utf-8")).get("wip_limits", {}) if path.is_file() else {}

    def _fidelity_of(self, guidance: PracticeGuidance, name: str) -> FidelityGuidance:
        try:
            return guidance.fidelities[name]
        except KeyError as missing:
            raise FidelityNotFoundError(name, guidance.key) from missing

    def _forge_page(self, practice: str, fidelity: str) -> str:
        slug = f"{practice}-{fidelity}"
        if not fidelity or slug in FIDELITIES_WITHOUT_PAGE:
            return f"{FORGE}/context-tools/{practice}.html"
        return f"{FORGE}/fidelities/{slug}.html"

    def _build_columns(self) -> list[Column]:
        # The stage names come from the one place a fidelity's **Stage:** is read against, written as column titles.
        stages = [Stage(name.capitalize(), self, list(STAGE_ACTIONS)) for name in (DISCOVERY, SPECIFICATION, IMPLEMENTATION)]
        return [Backlog(self), *stages, Complete(self)]


class Column:
    """*Column* is one place on the board: Backlog, a stage, or Complete."""

    def __init__(self, name: str, board: Board) -> None:
        self._name = name
        self._board = board

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    def cards(self) -> list[Card]:
        return [card for card in self._board.cards if card.column is self]


class Backlog(Column):
    """*Backlog* is the first column: the ideas a person has added to the backlog folder."""

    def __init__(self, board: Board) -> None:
        super().__init__(BACKLOG_COLUMN, board)

    @property
    @data_field
    def items(self) -> list[BacklogItem]:
        return list(self.cards)


class Complete(Column):
    """*Complete* is the last column: the tickets whose sessions are closed."""

    def __init__(self, board: Board) -> None:
        super().__init__(COMPLETE_COLUMN, board)

    @property
    @data_field
    def tickets(self) -> list[Ticket]:
        return list(self.cards)


class Stage(Column):
    """*Stage* is a column where work is done: every chosen practice's fidelity for it goes through its actions."""

    def __init__(self, name: str, board: Board, actions: list[str]) -> None:
        super().__init__(name, board)
        self._actions = list(actions)

    @property
    def actions(self) -> list[str]:
        return list(self._actions)

    @property
    @data_field(key="work_required")
    def work_required_slugs(self) -> list[str]:
        return [self._slug(fidelity) for fidelity in self.work_required]

    @property
    @data_field
    def formats(self) -> dict[str, list[str]]:
        return {self._slug(fidelity): list(fidelity.outputs) for fidelity in self.work_required}

    @property
    @data_field
    def default_formats(self) -> dict[str, str]:
        return {self._slug(fidelity): fidelity.default_format for fidelity in self.work_required}

    @property
    def work_required(self) -> list[FidelityGuidance]:
        """Every fidelity of every chosen practice whose stage is this stage, in practice order."""
        stage = self.name.lower()
        return [fidelity for practice in self._board.practices for fidelity in practice.fidelities if fidelity.stage == stage]

    @property
    def next_stage(self) -> Stage | None:
        columns = self._board.columns
        following = columns[columns.index(self) + 1]
        return following if isinstance(following, Stage) else None

    @property
    def previous_stage(self) -> Stage | None:
        columns = self._board.columns
        earlier = columns[columns.index(self) - 1]
        return earlier if isinstance(earlier, Stage) else None

    @property
    @data_field
    def wip_limit(self) -> int:
        return self._board.wip_limit(self.name)

    @property
    @data_field
    def is_over_limit(self) -> bool:
        return len(self.cards) > self.wip_limit

    @property
    @data_field
    def in_progress(self) -> list[Ticket]:
        return [ticket for ticket in self.cards if not ticket.is_done]

    @property
    @data_field
    def done(self) -> list[Ticket]:
        return [ticket for ticket in self.cards if ticket.is_done]

    def _slug(self, fidelity: FidelityGuidance) -> str:
        return f"{fidelity.practice_guidance.key}-{fidelity.name}"


class Card(ABC):
    """*Card* is anything on the board that a person moves: a ticket or a backlog item."""

    def __init__(self, board: Board) -> None:
        self._board = board

    @property
    @data_field
    @abstractmethod
    def title(self) -> str: ...

    @property
    @abstractmethod
    def column(self) -> Column: ...

    @property
    @data_field
    @abstractmethod
    def last_activity(self) -> str: ...

    @abstractmethod
    def move_next(self) -> Card: ...

    @abstractmethod
    def move_previous(self) -> Card: ...

    def _timestamp(self, moment: datetime) -> str:
        return Session.timestamp(moment)


class Help:
    """The overview, guidance, and rules of a practice or one of its fidelities, with its stage and its page on the forge."""

    def __init__(self, practice: str, fidelity: str, stage: str, subject: PracticeGuidance | FidelityGuidance, href: str) -> None:
        self._practice = practice
        self._fidelity = fidelity
        self._stage = stage
        self._subject = subject
        self._href = href

    @property
    @data_field
    def practice(self) -> str:
        return self._practice

    @property
    @data_field
    def fidelity(self) -> str:
        return self._fidelity

    @property
    @data_field
    def stage(self) -> str:
        return self._stage

    @property
    @data_field
    def overview(self) -> str:
        return (self._subject.overview or "").strip()

    @property
    @data_field
    def guidance(self) -> str:
        return (self._subject.guidance or "").strip()

    @property
    @data_field
    def rules(self) -> list[HelpRule]:
        return [HelpRule(rule) for rule in self._subject.rules]

    @property
    @data_field
    def href(self) -> str:
        return self._href


class HelpRule:
    """One rule as help shows it: its slug and its text."""

    def __init__(self, rule: Rule) -> None:
        self._rule = rule

    @property
    @data_field
    def slug(self) -> str:
        return self._rule.slug

    @property
    @data_field
    def text(self) -> str:
        return self._rule.body.strip()


class Workspace:
    """Whether a ticket has its branch and its worktree, and whether the active ticket being left is on a branch of its own."""

    def __init__(self, has_branch: bool, has_worktree: bool, leaving_has_branch: bool) -> None:
        self._has_branch = has_branch
        self._has_worktree = has_worktree
        self._leaving_has_branch = leaving_has_branch

    @property
    @data_field
    def has_branch(self) -> bool:
        return self._has_branch

    @property
    @data_field
    def has_worktree(self) -> bool:
        return self._has_worktree

    @property
    @data_field
    def leaving_has_branch(self) -> bool:
        return self._leaving_has_branch
