"""Module: harness/diagnostics. Model (clean-engineering-model, python): *App*, its status and its failures.
Implemented: harness/diagnostics/app.py.
Canonical: harness/.context/editor-apps/.context/editor-apps-model.md#app"""
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import ClassVar

from harness.agent_tools import agent_tool, agent_toolset
from harness.agent_tools.agent_tools import tool_subject
from harness.installation.data_class import data_field, identity, language_adapter
from harness.mcp.mcp_server import mcp


class AppStatus(str, Enum):
    """How far an app has got on this machine."""

    NOT_INSTALLED = "not installed"
    DOWN = "not running"
    RUNNING = "running"


class AppNotRegistered(KeyError):
    """A call named an app no module registered."""

    def __init__(self, label: str) -> None:
        self.label = label


class AppServer:
    """The server an app answers from: what the chat that opens the app starts, and its end stops."""

    def __init__(self, folder: Path, script: str, ports: tuple[int, ...]) -> None:
        ...

    @property
    @data_field
    def folder(self) -> str:
        ...

    @property
    @data_field
    def command(self) -> list[str]:
        # node on its script, through tsx for a TypeScript one
        ...


class AppNotStarted(Exception):
    """An app could not be installed or launched: which app, which step, and the output that says why."""

    def __init__(self, app: App, reason: str) -> None:
        self.app = app
        self.reason = reason


@language_adapter(language="typescript")
@agent_toolset
class App:
    """*App* is one CDD web app a person opens beside the chat (Story UI, Graph, Kanban), and the one registry of them."""
    # open never launches an app that is not installed, and never answers a url before one of its ports answers.
    # status is read from the folder and the ports each time it is asked; the app keeps no copy of it.

    _registered: ClassVar[list[App]] = []

    def __init__(self, label: str, folder: Path, server: AppServer, page: str = "/") -> None:
        ...

    def register(self) -> App:
        # registering a label again replaces the earlier app rather than listing it twice
        # -> App.registered
        ...

    @classmethod
    def registered(cls) -> list[App]:
        ...

    @classmethod
    @tool_subject
    def load(cls, app: str, *, project: Path) -> App:
        # a label no module registered is refused with AppNotRegistered
        # -> App.registered
        ...

    @property
    @data_field
    @identity
    def label(self) -> str:
        ...

    @property
    @data_field
    def status(self) -> AppStatus:
        ...

    @property
    @data_field
    def port(self) -> int | None:
        ...

    @property
    @data_field
    def url(self) -> str:
        ...

    @mcp
    @agent_tool
    def open(self) -> App:
        # -> self.install (while NOT_INSTALLED)
        # the chat that pressed it starts self.server while it is not running, and its end stops it
        ...

    def install(self) -> App:
        # npm install, then the page build (what BoardPage.rebuild did); report_progress at each step
        # raises AppNotStarted(self, "install", reason)
        ...
