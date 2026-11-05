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

import json
from pathlib import Path
from typing import Any

from harness.installation.installer import Installer

Installer(repo=Path(__file__).resolve().parents[2]).ensure_import_path()

from generate.generate import Generate  # noqa: E402
from harness.kanban.backlog_item import BacklogItem, BacklogItemNotFoundError  # noqa: E402
from harness.kanban.board import Board  # noqa: E402
from harness.kanban.session_board_examples import SURFACE_FIXTURE_PROJECT, SessionsProject  # noqa: E402
from harness.kanban.story_test import World, ticket_in  # noqa: E402
from harness.kanban.ticket import Ticket, TicketNotFoundError  # noqa: E402
from harness.mcp.mcp_server import McpServer  # noqa: E402
from space.session import Session  # noqa: E402
from validate.validate import Validate  # noqa: E402

TOOLSETS = (
    "harness.kanban.board:Board",
    "harness.kanban.ticket:Ticket",
    "harness.kanban.backlog_item:BacklogItem",
    "validate.validate:Validate",
    "generate.generate:Generate",
)


class DomainTier:
    """The board's domain on a throwaway project, with nothing between a step and the domain."""

    name = "domain"

    def open(self) -> World:
        return World(project=SessionsProject(SURFACE_FIXTURE_PROJECT), Board=Board, Ticket=Ticket, BacklogItem=BacklogItem, Session=Session, Validate=Validate, Generate=Generate)

    def close(self, world: World) -> None:
        world.project.close()


class ServerTier:
    """The board's operations through the cdd server started on a throwaway project."""

    name = "cdd tools"

    def open(self) -> World:
        project = SessionsProject(SURFACE_FIXTURE_PROJECT)
        cdd = CddTools(project)
        return World(
            project=project,
            Board=BoardTools(cdd),
            Ticket=TicketTools(cdd),
            BacklogItem=BacklogItemTools(cdd),
            Validate=lambda: ActionPrompts(cdd, "validate"),
            Generate=lambda: ActionPrompts(cdd, "generate"),
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
        return json.loads(json.dumps(answered, default=lambda value: value.to_json()))

    def prompt(self, name: str, **arguments: Any) -> Any:
        return self._server.invoke_prompt(name, arguments)


class BoardTools:
    """The board tools: board.show, board.set_wip_limit, board.folders, and board.help."""

    def __init__(self, cdd: CddTools) -> None:
        self._cdd = cdd

    def current(self) -> BoardTools:
        """The board of the project the cdd server was started on."""
        return self

    def show(self) -> BoardTools:
        return self

    def to_json(self) -> dict:
        return self._cdd.call("board.show")

    def set_wip_limit(self, stage: str, limit: int) -> BoardTools:
        self._cdd.call("board.set_wip_limit", stage=stage, limit=limit)
        return self

    def folders(self, path: str = "") -> list[str]:
        return self._cdd.call("board.folders", path=path)

    def help(self, practice: str, fidelity: str = "") -> dict:
        return self._cdd.call("board.help", practice=practice, fidelity=fidelity)


class TicketTools:
    """The ticket tools that open or name a ticket: ticket.new, and the ticket every other ticket tool takes."""

    def __init__(self, cdd: CddTools) -> None:
        self._cdd = cdd

    def load(self, ticket: str) -> TicketHandle:
        return TicketHandle(self._cdd, ticket)

    def new(self, title: str, scope: str = "feature", parent: str = "", path: str = "") -> TicketHandle:
        opened = self._cdd.call("ticket.new", title=title, scope=scope, parent=parent, path=path)
        return TicketHandle(self._cdd, opened["name"])


class TicketHandle:
    """One ticket by name. Each operation is the ticket tool of its name, called with the ticket's name; an answer that
    is a ticket or a backlog item comes back as its handle, as the domain answers with the ticket or item itself."""

    def __init__(self, cdd: CddTools, name: str) -> None:
        self._cdd = cdd
        self.name = name

    def to_json(self) -> dict:
        found = ticket_in(self._cdd.call("board.show"), self.name)
        if found is None:
            raise TicketNotFoundError(self.name)
        return found

    def __getattr__(self, operation: str) -> Any:
        if operation.startswith("_"):
            raise AttributeError(operation)

        def called(**arguments: Any) -> Any:
            return _handle_of(self._cdd, self._cdd.call(f"ticket.{operation}", ticket=self.name, **arguments))

        return called


class BacklogItemTools:
    """The backlog item tools: backlog-item.add, and the item backlog-item.start takes by its title."""

    def __init__(self, cdd: CddTools) -> None:
        self._cdd = cdd

    def load(self, backlog_item: str) -> BacklogItemHandle:
        return BacklogItemHandle(self._cdd, backlog_item)

    def add(self, title: str, text: str = "") -> BacklogItemHandle:
        added = self._cdd.call("backlog-item.add", title=title, text=text)
        return BacklogItemHandle(self._cdd, added["title"])


class BacklogItemHandle:
    def __init__(self, cdd: CddTools, title: str) -> None:
        self._cdd = cdd
        self.title = title

    def start(self, scope: str = "feature", path: str = "") -> TicketHandle:
        started = self._cdd.call("backlog-item.start", backlog_item=self.title, scope=scope, path=path)
        return TicketHandle(self._cdd, started["name"])

    def to_json(self) -> dict:
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


def _handle_of(cdd: CddTools, answered: Any) -> Any:
    if isinstance(answered, dict) and {"name", "column"} <= set(answered):
        return TicketHandle(cdd, answered["name"])
    if isinstance(answered, dict) and {"title", "path", "text"} <= set(answered):
        return BacklogItemHandle(cdd, answered["title"])
    return answered
