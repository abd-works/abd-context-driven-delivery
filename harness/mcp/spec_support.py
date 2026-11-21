"""Spec support: a throwaway user home, and a real cdd server serving this checkout from a throwaway ``~/.cdd``."""
from __future__ import annotations

import asyncio
import contextlib
import json
import os
import shutil
import socket
import tempfile
import uuid
from collections.abc import AsyncIterator
from datetime import timedelta
from pathlib import Path

from harness.mcp.cdd_home import CDD_HOME_ENV, CddHome
from harness.mcp.mcp_address import CHAT_HEADER, CHAT_PROCESS_HEADER, PROJECT_HEADER, SERVER_PORT_ENV, McpAddress
from harness.mcp.mcp_daemon import CONNECT_SCRIPT, SERVER_OWNER_ENV, McpDaemon
from harness.process.server_daemon import RunningServer

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TOOLSET_REFS_ENV = "MCP_TOOLSET_REFS"
# How long a spec chat waits on one call: a ticket's first call builds its worktree.
_CALL_SECONDS = 180


class UserHome:
    """Points HOME, USERPROFILE and APPDATA at a temp folder so specs never touch the user's own config, and the cdd home
    at its ``.cdd``, as it is for a user with no ``CDD_HOME`` of their own; a test run names a ``CDD_HOME`` of its own."""

    _KEYS = ("HOME", "USERPROFILE", "APPDATA", CDD_HOME_ENV)

    def __init__(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="cdd-user-home-"))
        self._prior = {key: os.environ.get(key) for key in self._KEYS}

    def enter(self) -> Path:
        os.environ["HOME"] = str(self.root)
        os.environ["USERPROFILE"] = str(self.root)
        os.environ["APPDATA"] = str(self.root / "AppData" / "Roaming")
        os.environ[CDD_HOME_ENV] = str(self.root / ".cdd")
        return self.root

    def leave(self) -> None:
        for key, value in self._prior.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        shutil.rmtree(self.root, ignore_errors=True)


class SpecServer:
    """The cdd server as chats meet it: its own process on its own port, started through ``~/.cdd/connect.py``, here
    with a throwaway ``~/.cdd`` that serves this checkout and only the toolsets a spec names."""

    def __init__(self, toolsets: tuple[str, ...] = (), home: Path | str | None = None, port: int | None = None) -> None:
        self.home = CddHome(home or tempfile.mkdtemp(prefix="cdd-home-"))
        self.daemon = McpDaemon(self.home, McpAddress(port or self._free_port()))
        self._toolsets = toolsets
        self._prior = {key: os.environ.get(key) for key in (CDD_HOME_ENV, SERVER_PORT_ENV, SERVER_OWNER_ENV, _TOOLSET_REFS_ENV)}

    @property
    def url(self) -> str:
        return self.daemon.url

    def install(self) -> None:
        """Install the throwaway ``~/.cdd`` serving this checkout, with no server started yet. The server it starts
        belongs to this process and ends when it does."""
        os.environ[CDD_HOME_ENV] = str(self.home.folder)
        os.environ[SERVER_PORT_ENV] = str(self.daemon.port)
        os.environ[SERVER_OWNER_ENV] = str(os.getpid())
        os.environ[_TOOLSET_REFS_ENV] = ",".join(self._toolsets)
        self.home.serve_from(_REPO_ROOT)
        self.home.install(_REPO_ROOT, CONNECT_SCRIPT)

    def start(self) -> RunningServer:
        """Install the throwaway ``~/.cdd`` and start the server on it, as the connect script does for an IDE."""
        self.install()
        return self.daemon.ensure()

    def stop(self) -> None:
        # A call still finishing could run the connect script and start the server again, so the script goes first.
        self.home.connect_script.unlink(missing_ok=True)
        self.daemon.stop()
        for key, value in self._prior.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        shutil.rmtree(self.home.folder, ignore_errors=True)

    @contextlib.asynccontextmanager
    async def chat(self, project: Path | str | None, seconds: float | None = None) -> AsyncIterator[object]:
        """An initialized MCP client session, as a chat working on ``project`` holds one. ``None`` names no project."""
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        headers = {PROJECT_HEADER: str(project)} if project is not None else {}
        timeout = None if seconds is None else timedelta(seconds=seconds)
        async with streamablehttp_client(self.url, headers=headers) as (read_stream, write_stream, _session_id):
            async with ClientSession(read_stream, write_stream, read_timeout_seconds=timeout) as session:
                await session.initialize()
                yield session

    def _free_port(self) -> int:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            return probe.getsockname()[1]


class SpecChat:
    """A chat as the cdd server meets it: the folder it connected from, its id, and optionally its Claude Code process."""

    def __init__(self, server: SpecServer, project: Path, chat_id: str = "", process: str = "") -> None:
        self._server = server
        self._headers = {PROJECT_HEADER: str(project), CHAT_HEADER: chat_id or str(uuid.uuid4())}
        if process:
            self._headers[CHAT_PROCESS_HEADER] = process

    def call(self, tool: str, **arguments) -> tuple[object, str]:
        """The tool's answer and an empty error, or no answer and the error the server gave."""
        return asyncio.run(self._call(tool, arguments))

    def answer(self, tool: str, **arguments) -> object:
        value, error = self.call(tool, **arguments)
        if error:
            raise AssertionError(f"{tool} failed: {error}")
        return value

    async def _call(self, tool: str, arguments: dict) -> tuple[object, str]:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        async with streamablehttp_client(self._server.url, headers=self._headers, timeout=_CALL_SECONDS, sse_read_timeout=_CALL_SECONDS) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool, arguments)
        text = result.content[0].text if result.content else ""
        if result.isError:
            return None, text
        try:
            return json.loads(text), ""
        except ValueError:
            return text, ""


class ThrowawayMachine:
    """A throwaway user home and ``~/.cdd`` for a whole spec file. An install into a real IDE path writes the user-level
    MCP entry and starts the cdd server; here both go to temp folders that are removed afterwards."""

    def __init__(self) -> None:
        self.home = UserHome()
        self.server = SpecServer()

    def enter(self) -> None:
        self.home.enter()
        self.server.install()

    def leave(self) -> None:
        self.server.stop()
        self.home.leave()


def main(arguments: list[str]) -> None:
    """For specs in another language, which reach the server through ``~/.cdd/connect.py`` like an IDE does.

    ``install`` sets up a throwaway ``~/.cdd`` serving this checkout and prints its folder and port as JSON; the spec
    then names both in ``CDD_HOME`` and ``CDD_SERVER_PORT``, and its first call starts the server. ``stop FOLDER PORT``
    stops that server and removes the folder."""
    import json

    if arguments[:1] == ["install"]:
        server = SpecServer()
        server.install()
        print(json.dumps({"home": str(server.home.folder), "port": server.daemon.port}))
    elif arguments[:1] == ["stop"] and len(arguments) == 3:
        SpecServer(home=arguments[1], port=int(arguments[2])).stop()
    else:
        raise SystemExit("usage: python -m harness.mcp.spec_support install | stop FOLDER PORT")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
