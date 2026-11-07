"""The two Python tiers the Session Board's shared scenarios replay on.

The domain tier hands a scenario's steps the domain classes themselves: `Board`, `Ticket`, `BacklogItem`, `Session`,
and the `Validate` and `Generate` actions, on a throwaway project.

The server tier hands them the same operations reached through the cdd server, the way an agent or the board app
reaches them: every call goes to `McpServer.invoke_tool` or `invoke_prompt` by its published name, with JSON in and
JSON out, on a server started with the board's toolsets on the throwaway project. `BoardTools`, `TicketTools`, and
`BacklogItemTools` are the Python form of the language adapter the board app reaches the same tools through
(`@language_adapter` on Board, Ticket, and BacklogItem): one method per tool, named as the tool is.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any

from harness.installation.destination import data_of
from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(Path(__file__).resolve().parents[2]).ensure_import_path()

from cdd_guidance.actions.generate.generate import Generate  # noqa: E402
from space.kanban.backlog_item import BacklogItem, BacklogItemNotFoundError  # noqa: E402
from space.kanban.board import Board, Stage  # noqa: E402
from space.kanban.session_board_examples import SURFACE_FIXTURE_PROJECT, SessionsProject  # noqa: E402
from space.kanban.story_test import World, progress_in, ticket_in  # noqa: E402
from space.kanban.ticket import FidelityNotFoundError, Ticket, TicketNotFoundError  # noqa: E402
from harness.mcp.mcp_server import McpServer  # noqa: E402
from space.session import Session, Sessions  # noqa: E402
from cdd_guidance.actions.validate.validate import Validate  # noqa: E402

TOOLSETS = (
    "space.kanban.board:Board",
    "space.kanban.board:Stage",
    "space.kanban.ticket:Ticket",
    "space.kanban.ticket:FidelityProgress",
    "space.session.session:Session",
    "space.session.sessions:Sessions",
    "space.session.practice_session_output:PracticeSessionOutput",
    "space.kanban.backlog_item:BacklogItem",
    "cdd_guidance.actions.validate.validate:Validate",
    "cdd_guidance.actions.generate.generate:Generate",
)


class DomainTier:
    """The board's domain on a throwaway project, with nothing between a step and the domain."""

    name = "domain"

    def open(self) -> World:
        project = SessionsProject(SURFACE_FIXTURE_PROJECT)
        on_project = {name: OnProject(domain_class, project.root) for name, domain_class in (("Board", Board), ("Stage", Stage), ("Ticket", Ticket), ("BacklogItem", BacklogItem))}
        # The cdd server makes each action for the session open in the call's project; so does this tier.
        sessions = Sessions(project.root)
        return World(
            project=project,
            **on_project,
            Session=Session,
            Validate=lambda: Validate(sessions.current()),
            Generate=lambda: Generate(sessions.current()),
            data_of=data_of,
        )

    def close(self, world: World) -> None:
        world.project.close()


class OnProject:
    """A board class whose loader and class tools are handed the throwaway project, as the cdd server hands each tool
    call the project the call names; every other member is the class's own."""

    _GIVEN_THE_PROJECT = ("load", "create")

    def __init__(self, domain_class: type, project: Path) -> None:
        self._domain_class = domain_class
        self._project = project

    def __call__(self, *arguments: Any) -> Any:
        return self._domain_class(*arguments)

    def __getattr__(self, member: str) -> Any:
        found = getattr(self._domain_class, member)
        return functools.partial(found, project=self._project) if member in self._GIVEN_THE_PROJECT else found


class ServerTier:
    """The board's operations through the cdd server started on a throwaway project."""

    name = "cdd tools"

    def open(self) -> World:
        project = SessionsProject(SURFACE_FIXTURE_PROJECT)
        cdd = CddTools(project)
        return World(
            project=project,
            Board=BoardTools(cdd),
            Stage=StageTools(cdd),
            Ticket=TicketTools(cdd),
            BacklogItem=BacklogItemTools(cdd),
            Validate=lambda: ActionPrompts(cdd, "validate"),
            Generate=lambda: ActionPrompts(cdd, "generate"),
            data_of=_server_data_of,
        )

    def close(self, world: World) -> None:
        world.project.close()


class CddTools:
    """The cdd server on the project, called as the MCP host calls it: a tool or prompt by name, JSON in and out."""

    def __init__(self, project: SessionsProject) -> None:
        self._server = McpServer(project=project.root)
        self._server.start(TOOLSETS)

    def call(self, tool: str, **arguments: Any) -> Any:
        answered = self._server.invoke_tool(tool, arguments)
        return json.loads(json.dumps(answered, default=data_of))

    def prompt(self, name: str, **arguments: Any) -> Any:
        return self._server.invoke_prompt(name, arguments)


class BoardTools:
    """The board tools: board.show, and every other board tool by its name, such as board.help(practice=...)."""

    def __init__(self, cdd: CddTools) -> None:
        self._cdd = cdd

    def load(self) -> BoardTools:
        """The board of the project the cdd server was started on."""
        return self

    def show(self) -> BoardTools:
        return self

    def data(self) -> dict:
        return self._cdd.call("board.show")

    def folders(self, path: str = "") -> list[str]:
        return self._cdd.call("board.folders", path=path)

    def __getattr__(self, operation: str) -> Any:
        if operation.startswith("_"):
            raise AttributeError(operation)
        return lambda **arguments: _handle_of(self._cdd, self._cdd.call(f"board.{operation}", **arguments))


class StageTools:
    """The stage tools: each takes the stage by its name, such as Discovery."""

    def __init__(self, cdd: CddTools) -> None:
        self._cdd = cdd

    def load(self, stage: str) -> StageHandle:
        return StageHandle(self._cdd, stage)


class StageHandle:
    """One stage by name. Each operation is the stage tool of its name, called with the stage's name."""

    def __init__(self, cdd: CddTools, name: str) -> None:
        self._cdd = cdd
        self.name = name

    def __getattr__(self, operation: str) -> Any:
        if operation.startswith("_"):
            raise AttributeError(operation)
        return lambda **arguments: self._cdd.call(f"stage.{operation}", stage=self.name, **arguments)


class TicketTools:
    """The ticket tools that open or name a ticket: ticket.create, and the ticket every other ticket tool takes."""

    def __init__(self, cdd: CddTools) -> None:
        self._cdd = cdd

    def load(self, ticket: str) -> TicketHandle:
        return TicketHandle(self._cdd, ticket)

    def create(self, title: str, scope: str = "feature", parent: str = "", path: str = "") -> TicketHandle:
        opened = self._cdd.call("ticket.create", title=title, scope=scope, parent=parent, path=path)
        return TicketHandle(self._cdd, opened["name"])


class TicketHandle:
    """One ticket by name. Each operation is the ticket tool of its name, called with the ticket's name; an answer that
    is a ticket or a backlog item comes back as its handle, as the domain answers with the ticket or item itself."""

    def __init__(self, cdd: CddTools, name: str) -> None:
        self._cdd = cdd
        self.name = name

    def data(self) -> dict:
        found = ticket_in(self._cdd.call("board.show"), self.name)
        if found is None:
            raise TicketNotFoundError(self.name)
        return found

    @property
    def session(self) -> SessionHandle:
        return SessionHandle(self._cdd, self)

    def progress_of(self, slug: str) -> FidelityProgressHandle:
        if slug not in [progress["fidelity"]["slug"] for progress in self.data()["progress"]]:
            raise FidelityNotFoundError(slug, f"ticket {self.name!r}")
        return FidelityProgressHandle(self._cdd, self, slug)

    def __getattr__(self, operation: str) -> Any:
        if operation.startswith("_"):
            raise AttributeError(operation)

        def called(**arguments: Any) -> Any:
            return _handle_of(self._cdd, self._cdd.call(f"ticket.{operation}", ticket=self.name, **arguments))

        return called


class FidelityProgressHandle:
    """One fidelity's progress on a ticket. Each operation is the fidelity-progress tool of its name, called with the
    ticket's name and the fidelity's slug."""

    def __init__(self, cdd: CddTools, ticket: TicketHandle, slug: str) -> None:
        self._cdd = cdd
        self._ticket = ticket
        self.slug = slug

    def data(self) -> dict:
        return progress_in(self._ticket.data(), self.slug)

    def __getattr__(self, operation: str) -> Any:
        if operation.startswith("_"):
            raise AttributeError(operation)

        def called(**arguments: Any) -> Any:
            answered = self._cdd.call(f"fidelity-progress.{operation}", ticket=self._ticket.name, fidelity=self.slug, **arguments)
            return _handle_of(self._cdd, answered)

        return called


class SessionHandle:
    """A ticket's session. Each operation is the session tool of its name, called with the session's file; its
    practices are each practice-session-output's tools, called with the session's file and the practice's name."""

    def __init__(self, cdd: CddTools, ticket: TicketHandle) -> None:
        self._cdd = cdd
        self._ticket = ticket

    def data(self) -> dict:
        return self._ticket.data()["session"]

    def practice(self, name: str) -> PracticeHandle:
        return PracticeHandle(self._cdd, self, name)

    @property
    def practices(self) -> dict[str, PracticeHandle]:
        return {name: PracticeHandle(self._cdd, self, name) for name in self.data()["practices"]}

    def __getattr__(self, operation: str) -> Any:
        if operation.startswith("_"):
            raise AttributeError(operation)

        def called(**arguments: Any) -> Any:
            return _handle_of(self._cdd, self._cdd.call(f"session.{operation}", session=self.data()["session_file"], **arguments))

        return called


class PracticeHandle:
    """One practice in a ticket's session: its practice-session-output tools, such as enable and choose_root."""

    def __init__(self, cdd: CddTools, session: SessionHandle, name: str) -> None:
        self._cdd = cdd
        self._session = session
        self.name = name

    def data(self) -> dict:
        return self._session.data()["practices"][self.name]

    def __getattr__(self, operation: str) -> Any:
        if operation.startswith("_"):
            raise AttributeError(operation)

        def called(**arguments: Any) -> Any:
            session_file = self._session.data()["session_file"]
            self._cdd.call(f"practice-session-output.{operation}", session=session_file, practice=self.name, **arguments)
            return self

        return called


class BacklogItemTools:
    """The backlog item tools: backlog-item.add, and the item backlog-item.start takes by its title."""

    def __init__(self, cdd: CddTools) -> None:
        self._cdd = cdd

    def load(self, backlog_item: str) -> BacklogItemHandle:
        return BacklogItemHandle(self._cdd, backlog_item)

    def create(self, title: str, text: str = "") -> BacklogItemHandle:
        added = self._cdd.call("backlog-item.create", title=title, text=text)
        return BacklogItemHandle(self._cdd, added["title"])


class BacklogItemHandle:
    def __init__(self, cdd: CddTools, title: str) -> None:
        self._cdd = cdd
        self.title = title

    def start(self, scope: str = "feature", path: str = "") -> TicketHandle:
        started = self._cdd.call("backlog-item.start", backlog_item=self.title, scope=scope, path=path)
        return TicketHandle(self._cdd, started["name"])

    def data(self) -> dict:
        backlog = next(column for column in self._cdd.call("board.show")["columns"] if column["name"] == "Backlog")
        found = next((item for item in backlog["items"] if item["title"] == self.title), None)
        if found is None:
            raise BacklogItemNotFoundError(self.title)
        return found


class ActionPrompts:
    """A guidance action's prompts, such as validate.validate, called by the action's own method names."""

    def __init__(self, cdd: CddTools, action: str) -> None:
        self._cdd = cdd
        self._action = action

    def __getattr__(self, prompt: str) -> Any:
        if prompt.startswith("_"):
            raise AttributeError(prompt)
        return lambda **arguments: self._cdd.prompt(f"{self._action}.{prompt}", **arguments)


def _server_data_of(value: Any) -> Any:
    """What a step reads: a handle's data as the server sends it now, and any other answer, already JSON, as it is."""
    handles = (BoardTools, TicketHandle, BacklogItemHandle, FidelityProgressHandle, SessionHandle, PracticeHandle)
    return value.data() if isinstance(value, handles) else value


def _handle_of(cdd: CddTools, answered: Any) -> Any:
    if isinstance(answered, dict) and {"ticket", "fidelity", "state"} <= set(answered):
        return FidelityProgressHandle(cdd, TicketHandle(cdd, answered["ticket"]["name"]), answered["fidelity"]["slug"])
    if isinstance(answered, dict) and {"name", "column"} <= set(answered):
        return TicketHandle(cdd, answered["name"])
    if isinstance(answered, dict) and {"title", "path", "text"} <= set(answered):
        return BacklogItemHandle(cdd, answered["title"])
    return answered
