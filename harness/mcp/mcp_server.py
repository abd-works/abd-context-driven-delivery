"""The install that writes each IDE's MCP entry, and the cdd server's MCP side: one *McpServer* of
toolsets for each project, and the *McpHost* answering every chat with them."""
from __future__ import annotations

import asyncio
import importlib
import json
import logging
import os
import re
import socket
import sys
import threading
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from types import ModuleType
from typing import Any

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import mcp.types as types
    from mcp.server.models import InitializationOptions
    from starlette.requests import Request
    from starlette.responses import JSONResponse

from harness.agent_tools.agent_tools import AgentTool, AgentToolSet, InstallDestination, ToolsetConfiguration, ToolsetReference, names_alike
from harness.agent_tools.chat_pointer import ChatPointer
from harness.process.claude_chat_process import ClaudeChatProcess, is_desktop_spare
from harness.agent_tools.tool_call import CALLS_BEING_ANSWERED, ToolCall, ToolRequest
from harness.installation.destination import ServerInstallation, SkippedTool, SkippedTools
from harness.installation.data_class import SentValue, data_of
from harness.installation.ide_layout import IdeLayout
from harness.installation.installer import SERVER_CHANNELS
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.installation.repository_toolsets import RUNNING_CHECKOUT, RepositoryToolsets
from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_annotations import LongCall, Mcp  # noqa: F401 - importing the server defines Mcp, the channel install reads
from harness.mcp.claude_plugins import ClaudePlugins
from harness.mcp.mcp_address import BUILTIN_LIST_TOOLS, CHAT_HEADER, CHAT_PROCESS_HEADER, LANE_CALL_PATH, MCP_PATH, PING_PATH, PROJECT_HEADER
from harness.mcp.mcp_daemon import McpDaemon
from harness.mcp.server_lanes import LaneCall, ServerLane, ServerLanes
from harness.mcp.server_hooks import CddServerHooks
from harness.mcp.restart_gate import _RestartGate
from harness.mcp.tool_calls import ThrottledReporter, _StillRunning, _ToolCalls

logger = logging.getLogger(__name__)
BUILTIN_PING_TOOL = "cdd.ping"
# What ``cdd.ping`` answers: the event loop answered, whatever the worker threads are busy with.
PONG = "pong"
# Reloads the server's Python in place, so every chat picks up changed code without a new connection.
BUILTIN_RESTART_TOOL = "cdd.restart"
# How long a chat waits for a call before it hears that the call is still running.
CALL_SECONDS = 10
# The wait for an operation annotated ``@long_call``, and for a restart, which waits for every running call to end.
LONG_CALL_SECONDS = 600
# What loading a toolset's module, making the toolset, or reading a tool's schema raises when that toolset's code or
# configuration is wrong. The server skips that toolset or tool and serves the rest; anything else stops the start.
_LEGAL_MCP_NAME = re.compile(r"[A-Za-z0-9_.-]+")
# Claude Code names the cdd plugin's tools mcp__plugin_cdd_cdd__{tool}, so this one entry allows every one of them.
CLAUDE_TOOLS_PERMISSION = "mcp__plugin_cdd_cdd"


class McpStandupFailed(Exception):
    """The MCP host could not stand up over a checkout's toolsets."""

    def __init__(self, repo: Path, cause: BaseException) -> None:
        super().__init__(f"the MCP host could not stand up over {repo}: {cause}")
        self.repo = repo
        self.cause = cause


class McpConfigUnreadable(JsonFileUnreadable):
    """An IDE config file that cdd edits exists but is not readable JSON. cdd leaves it as it is rather than write over
    whatever else it holds."""

    def message(self, path: Path, cause: Exception) -> str:
        return f"{path} is not readable JSON ({cause}); fix or remove it, then install again"


class ToolNotEnrolled(LookupError):
    """A call named a tool the server does not publish."""

    def __init__(self, tool: str) -> None:
        super().__init__(f"{tool} is not a tool the cdd server publishes")
        self.tool = tool


class _ChatCallFailed(Exception):
    """A call a chat sent failed; the chat hears the failure's kind and its words, as ``LedgerIsLocked: the ledger is
    locked``."""

    def __init__(self, failure: Exception) -> None:
        super().__init__(f"{type(failure).__name__}: {failure}")


class CddEntry:
    """The ``cdd`` entry of one installation's IDE: where its MCP config is, and the entry written there, so a chat
    knows the server's address and how to name its project. For Claude Code at user level the cdd plugin declares the
    server instead, and the entry goes from every config that would outrank it."""

    def __init__(self, installation: McpInstallation) -> None:
        self._installation = installation
        self._layout = installation.layout

    @property
    def is_user_level(self) -> bool:
        """Whether the entry goes in the IDE's user-level MCP config. A temp install tree keeps its entry in the tree,
        so specs never touch the user's own config."""
        return self._layout.user_mcp_config is not None and not self._installation.is_temporary

    @property
    def path(self) -> Path:
        """The IDE's user-level MCP config. A temp install tree keeps ``<ide>/mcp.json``
        (Claude Code: ``.mcp.json`` at the project root) so specs never touch the user's own."""
        if self.is_user_level:
            return self._layout.user_mcp_config
        if self._layout.is_claude_code:
            return self._project_root / ".mcp.json"
        return self._installation.path / self._layout.MCP_CONFIG_NAME

    def write(self) -> None:
        """Write the entry, or for Claude Code at user level the cdd plugin, once the whole install has been recorded;
        an install that publishes no MCP operation writes nothing."""
        if not self._installation.mcp_operations:
            return
        dest = self.path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if self._layout.is_claude_code and self.is_user_level:
            self._write_claude_plugin()
            return
        manifest = self._server_manifest()
        if self._has_cdd_entry(dest, manifest):
            self._installation.track_write(dest)
            return
        if self._layout.is_claude_code or self.is_user_level:
            manifest = self._merged_with_other_servers(dest, manifest)
        self._ide_config(dest).write(manifest)
        self._installation.track_write(dest)

    def _write_claude_plugin(self) -> None:
        self._allow_cdd_tools(self._layout.user_settings_folder / "settings.json")
        self.point_chats_at_served_lane()
        self._drop_cdd_entry(self._layout.user_mcp_config, "user's", remove_when_empty=False)
        for written in self._installation.daemon.home.write_claude_plugin(self._claude_plugin_server()):
            self._installation.track_write(written)

    def point_chats_at_served_lane(self) -> None:
        """Point the Claude Code chats working in this checkout at the server of the lane it is served on: the dev
        lane's through a ``cdd`` entry in the project's ``.mcp.json``, the stable lane's through the cdd plugin alone.
        A full install does this, and so does every switch of the server onto this checkout's code, so a ticket's
        worktree pinned on the dev lane is not left talking to the stable lane."""
        if self._installation.served.daemon.home.is_dev_lane:
            self._write_dev_lane_entry()
        else:
            self._drop_cdd_entry(self._project_root / ".mcp.json", "project's", remove_when_empty=True)

    def _write_dev_lane_entry(self) -> None:
        """Point the chats working in this checkout at the dev lane's server. The cdd plugin names the stable lane's
        server, which runs main and so lists none of the tools the feature adds; a ``cdd`` entry in the project's
        ``.mcp.json`` outranks the plugin, so a chat started in the worktree lists and calls the feature's own tools."""
        config_path = self._project_root / ".mcp.json"
        server = {"type": "http", "url": self._installation.served.daemon.url, "headers": {PROJECT_HEADER: str(self._project_root.resolve())}}
        manifest = self._merged_with_other_servers(config_path, {self._layout.mcp_servers_key: {"cdd": server}})
        self._ide_config(config_path).write(manifest)
        self._installation.track_write(config_path)

    def _allow_cdd_tools(self, settings_path: Path) -> None:
        """Let Claude Code call every ``cdd`` tool without a prompt. The user's settings file
        holds their own permissions too, so add the one entry and never track the file for clean."""
        settings_file = self._ide_config(settings_path)
        try:
            data = settings_file.read()
        except McpConfigUnreadable as unreadable:
            logger.warning("Claude Code will ask before every cdd tool call: %s", unreadable)
            return
        permissions = data.setdefault("permissions", {})
        allow = permissions.setdefault("allow", [])
        if CLAUDE_TOOLS_PERMISSION in allow:
            return
        allow.append(CLAUDE_TOOLS_PERMISSION)
        settings_file.write(data)

    def _drop_cdd_entry(self, config_path: Path, whose: str, *, remove_when_empty: bool) -> None:
        """A ``cdd`` entry in the project's ``.mcp.json`` outranks the cdd plugin in Claude Code, and a user-level one
        runs its headersHelper in ``~/.claude`` for every chat, so it names no chat's project: each goes. The config's
        other servers stay (``~/.claude.json`` holds the app's own state too), and a project file left holding nothing
        goes too."""
        config_file = self._ide_config(config_path)
        try:
            data = config_file.read()
        except McpConfigUnreadable as unreadable:
            logger.warning("a cdd entry in the %s config may still outrank the cdd plugin: %s", whose, unreadable)
            return
        servers = data.get(self._layout.mcp_servers_key)
        if not isinstance(servers, dict) or "cdd" not in servers:
            return
        del servers["cdd"]
        if remove_when_empty and not servers and len(data) == 1:
            config_path.unlink()
            return
        config_file.write(data)

    def _claude_plugin_server(self) -> dict[str, Any]:
        """The cdd server as the cdd plugin declares it: its address alone. The server names each call's project from
        the Claude Code process holding the connection, so a chat runs nothing before it connects: a headers helper
        has about ten seconds while a chat starts, and one that ran past them left the chat without cdd."""
        return {"type": "http", "url": self._installation.daemon.url}

    def _server_manifest(self) -> dict[str, Any]:
        """The one ``cdd`` entry: the shared server's URL plus how each request names its project. A user-level entry
        serves every project, so it names the open one; a temp install tree names its own."""
        server: dict[str, Any] = {"type": "http", "url": self._installation.daemon.url}
        if self.is_user_level:
            server["headers"] = {PROJECT_HEADER: IdeLayout.PROJECT_FOLDER}
        else:
            server["headers"] = {PROJECT_HEADER: str(self._project_root.resolve())}
        if not self._layout.names_mcp_transport:
            del server["type"]
        return {self._layout.mcp_servers_key: {"cdd": server}}

    def _has_cdd_entry(self, dest: Path, manifest: dict[str, Any]) -> bool:
        """Rewriting ``~/.claude.json`` makes Claude Code reconnect cdd in every open chat, so an entry already in
        place is left alone. An unreadable config has no entry in place; writing it then fails by name."""
        try:
            existing = self._ide_config(dest).read()
        except McpConfigUnreadable:
            return False
        key = next(iter(manifest))
        servers = existing.get(key)
        return isinstance(servers, dict) and servers.get("cdd") == manifest[key]["cdd"]

    def _merged_with_other_servers(self, dest: Path, manifest: dict[str, Any]) -> dict[str, Any]:
        """The MCP config is shared with other servers (and, in ``~/.claude.json``, the IDE's own
        state); replace only ``cdd``. A config that cannot be read raises ``McpConfigUnreadable``, because writing it
        anyway would drop every other server it names."""
        merged = self._ide_config(dest).read()
        key = next(iter(manifest))
        servers = merged.get(key)
        merged[key] = {**(servers if isinstance(servers, dict) else {}), **manifest[key]}
        return merged

    def _ide_config(self, path: Path) -> JsonFile:
        """An IDE config file cdd edits: one JSON object, empty when there is none; one cdd cannot read raises
        *McpConfigUnreadable*, so cdd never writes over what else it holds."""
        return JsonFile(path, McpConfigUnreadable)

    @property
    def _project_root(self) -> Path:
        path = Path(self._installation.path)
        return path.parent if path.name == self._layout.folder_name else path


class McpInstallation(ServerInstallation):
    """Record ``@mcp`` operations, write each IDE's ``cdd`` entry, and start the one cdd server from ``~/.cdd``. Every
    install also publishes the hooks that start that server (*CddServerHooks*), and, for Claude Code, the cdd and
    board plugins."""

    channel = "mcp"
    toolsets = (CddServerHooks,)

    def __init__(self, layout: IdeLayout, path: Path | str, served: ServedCheckout) -> None:
        """served is the checkout the cdd server is installed from and serves, on the lane its folder runs on: the
        stable lane for a main checkout, the dev lane for a ticket's worktree."""
        super().__init__(layout, path, repo=served.checkout)
        self.served = served
        # The stable lane's server is the one every chat's cdd plugin names, so the plugins and the IDE entry follow it.
        self.daemon = ServerLanes.from_serving(served.daemon.home, served.daemon.address).stable.daemon
        self.claude_plugins = ClaudePlugins(self.daemon.home)
        # The IDE's cdd entry, written once the whole install has been recorded.
        self.cdd_entry = CddEntry(self)
        self.mcp_operations: list[AgentTool] = []
        self.host: McpHost | None = None
        self.diagnosis: dict[str, Any] | None = None

    @classmethod
    def create(cls, layout: IdeLayout, path: Path | str, repo: Path | str | None = None) -> McpInstallation:
        """The cdd server's installation into path, serving repo, else the running checkout, on the lane its folder runs
        on (*ServerLanes*)."""
        checkout = Path(repo or RUNNING_CHECKOUT).resolve()
        return cls(layout, path, ServerLanes().for_project(checkout).served_checkout(checkout))

    def write(self, tool: AgentTool) -> None:
        """Record the tool; the MCP config and the plugins are written once the whole install has been recorded, in
        standup, rather than again after every tool."""
        if tool.install_to_mcp:
            self.mcp_operations.append(tool)

    @property
    def published(self) -> list[str]:
        return sorted(str(tool.mcp_name) for tool in self.mcp_operations)

    def standup(self) -> McpHost | None:
        """A host over every toolset in this installation's checkout, in this process, to check it stands up; none
        inside the cdd server, which already serves them. The MCP config and the plugins are written first, once."""
        self.cdd_entry.write()
        if self.serves_this_process():
            return None
        self.host = McpHost.from_repo(self.served.checkout)
        return self.host

    def diagnose(self) -> dict[str, Any]:
        host = self.host if self.host is not None else self.standup()
        self.diagnosis = host.diagnose() if host is not None else {}
        return self.diagnosis

    def ensure_running(self) -> dict[str, str]:
        """Start the one cdd server when none answers, installing ``~/.cdd/`` on first use; an install that finds a
        server already running leaves it, and the code it serves, alone. For Claude Code also install the cdd and
        board plugins, which declare the server to every chat."""
        status = {"mcp": self.served.ensure()}
        if self.layout.is_claude_code:
            status["cdd plugin"] = self.claude_plugins.install_cdd()
            status.update(self.install_mods())
        return status

    def install_mods(self) -> dict[str, str]:
        """Install the board and prompt queue mods of the code the served lane runs. Chats install mods from the stable
        lane's marketplace, so a dev lane's mods are published there first."""
        if self.served.home.is_dev_lane:
            self.daemon.home.publish_mods_of(self.served.home)
        return {"board": self.claude_plugins.install_board(), "prompt queue": self.claude_plugins.install_queue()}

    def status(self) -> list[str]:
        return [f"cdd server: {'running' if self.daemon.is_running() else 'not running'}"]

    def serves_this_process(self) -> bool:
        """True when this process is the cdd server, as it is when an install runs as one of its tool calls."""
        return self.daemon.this_process.is_this_process()


class McpServer:
    """The toolsets one project's calls are answered by: every ``@mcp`` operation of the toolsets it was started with,
    published under its MCP name, made for that project."""

    def __init__(
        self,
        *,
        repo: str | Path | None = None,
        project: str | Path | None = None,
    ) -> None:
        self.repo = Path(repo).resolve() if repo is not None else RUNNING_CHECKOUT
        self.project = Path(project).resolve() if project is not None else self.repo
        self.venv = self.repo / ".venv"
        self._tools: dict[str, AgentTool] = {}
        self._prompts: dict[str, AgentTool] = {}
        self.skipped = SkippedTools("MCP", "tools")
        self._toolsets: tuple[Any, ...] = ()

    @property
    def tools(self) -> dict[str, AgentTool]:
        return dict(self._tools)

    @property
    def prompts(self) -> dict[str, AgentTool]:
        return dict(self._prompts)

    def enroll(self, tool: AgentTool) -> None:
        """Publish tool under its MCP name: an operation as a tool, instructions as a prompt whose call answers with
        them expanded. A tool whose name is not a legal MCP name, is taken, or whose arguments' schema cannot be read
        is skipped, so the tool list never fails."""
        name = tool.mcp_name
        if not self._is_legal_name(name):
            self.skipped.skip(name, SkippedTool(name, "illegal MCP tool name"))
            return
        if name in self._tools or name in self._prompts:
            self.skipped.skip(name, SkippedTool(name, "MCP name is already enrolled"))
            return
        try:
            tool.input_schema
        except AgentToolSet.LOAD_FAILURES as unreadable:
            self.skipped.skip(name, SkippedTool(name, f"its argument schema cannot be read: {unreadable}", unreadable))
            return
        if tool.kind == "tool":
            self._tools[name] = tool
        else:
            self._prompts[name] = tool

    def start(self, toolsets: Iterable[Any]) -> None:
        """Enroll the ``@mcp`` operations of each toolset and its child toolsets; each is a toolset class, or a
        ``module:Class`` reference as a process is started with. A toolset whose code or configuration is wrong is
        skipped and recorded, so the server still serves the rest."""
        self._toolsets = tuple(toolsets)
        self._tools.clear()
        self._prompts.clear()
        self.skipped.clear()
        for configured in self._toolsets:
            for toolset in self._loaded(configured):
                self._enroll_with_children(toolset)

    def _loaded(self, configured: ToolsetConfiguration) -> list[AgentToolSet]:
        try:
            return AgentToolSet.from_items([configured])
        except AgentToolSet.LOAD_FAILURES as error:
            self.skipped.skip(str(configured), error)
            return []

    def _enroll_with_children(self, toolset: AgentToolSet) -> None:
        try:
            for each in (toolset, *toolset.child_toolsets()):
                self._enroll_toolset(each)
        except AgentToolSet.LOAD_FAILURES as error:
            self.skipped.skip(toolset.registration_name, error)

    def for_project(self, project: Path) -> McpServer:
        """A server with the same toolsets working on ``project``. Toolsets keep state between calls, so each project
        gets objects of its own and one chat's work never shows up in another's."""
        server = type(self)(repo=self.repo, project=project)
        server.start(self._toolsets)
        return server

    def restarted(self) -> McpServer:
        """A new server with the same toolsets, on the code as it is now. Every module from this checkout is imported
        again, this one included, because a toolset enrolled by the old loader would keep the old classes."""
        self._forget_checkout_modules()
        fresh = importlib.import_module(__name__)
        server = fresh.McpServer(repo=self.repo, project=self.project)
        server.start(self._references())
        return server

    def _references(self) -> list[str]:
        """Each toolset by its ``module:Class`` reference, the one name that finds its class again once its module is
        imported anew."""
        return [item if isinstance(item, str) else str(ToolsetReference.of(item)) for item in self._toolsets]

    def _forget_checkout_modules(self) -> None:
        # Every module is judged before any is forgotten: a namespace package reads its folders through its parent.
        forgotten = [name for name, module in list(sys.modules.items()) if self._is_checkout_module(module)]
        for name in forgotten:
            del sys.modules[name]
        importlib.invalidate_caches()

    def _is_checkout_module(self, module: ModuleType) -> bool:
        """Whether module was imported from this checkout. A package folder with no ``__init__.py`` has no file, only
        its folders, and kept while the packages around it are forgotten it looks for a parent that is gone."""
        folders = list(getattr(module, "__path__", None) or [])
        return any(self._is_checkout_file(file) for file in (getattr(module, "__file__", None), *folders))

    def _is_checkout_file(self, file: str | None) -> bool:
        if not file:
            return False
        path = Path(file).resolve()
        return self.repo in path.parents and self.venv not in path.parents

    def _enroll_toolset(self, toolset: AgentToolSet) -> None:
        if not toolset.is_served_on_mcp:
            return
        for tool in toolset.tools_for(InstallDestination.MCP):
            self.enroll(tool)

    def _is_legal_name(self, name: str) -> bool:
        return bool(name) and _LEGAL_MCP_NAME.fullmatch(name) is not None

    def resolve_call_name(self, name: str) -> str:
        """The enrolled name a client's spelling of a tool names, such as Cursor's ``slug_op`` for ``slug.op``: each
        tool says whether a spelling names it (``AgentTool.is_called``), the one rule a rules hook uses too; name itself
        when nothing enrolled answers to it."""
        if name in self._tools or name in self._prompts:
            return name
        for builtin in (BUILTIN_PING_TOOL, BUILTIN_RESTART_TOOL):
            if names_alike(name, builtin):
                return builtin
        enrolled = (*self._tools.items(), *self._prompts.items())
        return next((published for published, tool in enrolled if tool.is_called(name)), name)

    def enrolled(self, name: str) -> AgentTool | None:
        """The tool or instructions published as name, or under the name a client spelled it; none when not published."""
        resolved = self.resolve_call_name(name)
        return self._tools.get(resolved) or self._prompts.get(resolved)

    def call_seconds(self, name: str) -> float:
        """How long a chat waits for a call of the tool published as name: longer for an operation annotated
        ``@long_call``, and for a restart."""
        if name == BUILTIN_RESTART_TOOL:
            return LONG_CALL_SECONDS
        tool = self.enrolled(name)
        return LONG_CALL_SECONDS if tool is not None and LongCall.annotates(tool.callable) else CALL_SECONDS

    def invoke(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        """Call the tool or the instructions published as mcp_name on this server's project."""
        return self.answer(mcp_name, ToolCall(arguments, self.project, ToolRequest(tool=mcp_name)))

    def answer(self, mcp_name: str, call: ToolCall) -> object:
        """Answer call with the tool published as mcp_name, or with the instructions published so, expanded for it;
        either may be named the way a client spelled it."""
        published = self.enrolled(mcp_name)
        if published is None:
            raise ToolNotEnrolled(self.resolve_call_name(mcp_name))
        return published.answer(call)


class ProjectNotNamed(Exception):
    """A tool call arrived from a chat whose folder the server cannot find, so it cannot tell which project it is for."""

    def __init__(self, tool: str) -> None:
        super().__init__(
            f"{tool} was called from a chat whose folder the server cannot find: the Claude Code process holding its "
            f"connection records none, nor does its transcript, and no {PROJECT_HEADER} header names one. Open the "
            "chat in a project folder and call again; a client that is not a Claude Code chat names its project in the "
            f"{PROJECT_HEADER} header."
        )
        self.tool = tool


class ProjectIsClaudeSettings(Exception):
    """A tool call named Claude Code's own settings folder as its project. A user-level cdd entry does that for every
    chat, because Claude Code runs its headersHelper there, so the call would act on a board no chat works on."""

    def __init__(self, tool: str, folder: Path) -> None:
        super().__init__(
            f"{tool} named {folder} as its project, which is Claude Code's settings folder, not this chat's folder. "
            "The cdd entry in ~/.claude.json causes this: run python scripts/install.py --ide Claude from a CDD checkout, "
            "which replaces it with the cdd plugin, then reconnect cdd in this chat with /mcp."
        )
        self.tool = tool
        self.folder = folder


class McpHost:
    """The cdd server's MCP side: one *McpServer* for each project a chat works on, answering every chat. The server
    on the checkout it serves from answers the tool list, which every project shares, and gives each new project its
    toolsets."""

    def __init__(self, checkout_server: McpServer) -> None:
        self._checkout_server = checkout_server
        self._servers: dict[Path, McpServer] = {checkout_server.project: checkout_server}
        self._servers_lock = threading.Lock()
        self._restart_gate = _RestartGate()
        self._tool_calls = _ToolCalls(self._answer_reporting)
        self._protocol_server: Any = None
        # A user-level cdd entry names Claude Code's own settings folder as its project; calls naming it are refused.
        self._claude_settings = IdeLayout("Claude").user_settings_folder.resolve()
        # The cdd home of the server process, once it serves chats; a host made in-process for a probe or spec has none.
        self._home: CddHome | None = None
        # The two lanes as the running server sees them; none for a host answering calls in process.
        self._lanes: ServerLanes | None = None

    @property
    def _protocol(self) -> Any:
        """The MCP protocol server answering chats, made with its handlers the first time the host speaks MCP: a call
        dispatched in-process (a probe, a script, a spec) never loads the SDK."""
        if self._protocol_server is None:
            self._protocol_server = self._cdd_protocol_server("cdd")
            self._register_handlers()
        return self._protocol_server

    def _request_context(self) -> Any:
        """The MCP request being answered; none outside one, which is always so before the protocol server is made."""
        if self._protocol_server is None:
            return None
        try:
            return self._protocol_server.request_context
        except LookupError:
            return None

    @property
    def checkout_server(self) -> McpServer:
        """The server on the checkout this host serves from: the tools every chat lists, and what start-up skipped."""
        return self._checkout_server

    def _server_for(self, project: Path) -> McpServer:
        """The toolsets working on ``project``, started the first time a call names it."""
        with self._servers_lock:
            server = self._servers.get(project)
            if server is None:
                server = self._checkout_server.for_project(project)
                self._servers[project] = server
            return server

    @property
    def projects(self) -> list[Path]:
        with self._servers_lock:
            return sorted(self._servers)

    def _mcp_types(self) -> Any:
        """The MCP SDK's types, loaded the first time the host speaks the protocol: the SDK takes seconds to import, and
        making or asking a server about its toolsets never needs it."""
        import mcp.types

        return mcp.types


    def _cdd_protocol_server(self, name: str) -> Any:
        """The MCP protocol server, telling every client that a restart can change the tool list."""
        from mcp.server import NotificationOptions, Server

        class _CddProtocolServer(Server):
            def create_initialization_options(
                self,
                notification_options: NotificationOptions | None = None,
                experimental_capabilities: dict[str, dict[str, Any]] | None = None,
            ) -> InitializationOptions:
                return super().create_initialization_options(
                    notification_options or NotificationOptions(tools_changed=True), experimental_capabilities
                )

        return _CddProtocolServer(name)

    def _register_handlers(self) -> None:
        types = self._mcp_types()

        @self._protocol.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            import anyio.to_thread

            project = self._listing_project()
            listed = await anyio.to_thread.run_sync(self.tools_listed_for, project)
            return [types.Tool(**tool) for tool in listed]

        @self._protocol.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, object] | None) -> types.CallToolResult:
            import anyio.lowlevel

            try:
                return await self._answer_chat(name, arguments)
            finally:
                # A worker thread runs to the end even when the client cancels it, and
                # the cancellation has already answered the request. Stop here, because
                # a second answer raises in the MCP session and takes down the host.
                await anyio.lowlevel.checkpoint()

        self._register_prompt_handlers()

    def _register_prompt_handlers(self) -> None:
        """The prompt list is empty: every cdd operation is a tool, so a prompt is answered only by its name."""
        types = self._mcp_types()

        @self._protocol.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            return []

        @self._protocol.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
            prompt = self._checkout_server.prompts.get(name)
            if prompt is None:
                raise ToolNotEnrolled(name)
            text = prompt.description or ""
            message = types.PromptMessage(role="user", content=types.TextContent(type="text", text=text))
            return types.GetPromptResult(description=prompt.description or None, messages=[message])

    def tools_listed_for(self, project: Path | None) -> list[dict[str, Any]]:
        """The tools a chat working on project is listed, as data: the other lane's when that lane answers project's
        calls, as the dev lane does a ticket's worktree while it serves a feature, so the chat can call every tool the
        feature adds; else this server's own."""
        other_lane = self._other_lane_answering(ToolCall.sent({}, project, ToolRequest(tool=BUILTIN_LIST_TOOLS, mcp_host=self))) if project else None
        if other_lane is not None:
            return other_lane.tools_for(project)
        return [tool.model_dump(exclude_none=True) for tool in self._tool_list()]

    def _listing_project(self) -> Path | None:
        """The project the chat listing its tools works on; none when it names none, which lists this server's own."""
        try:
            return self._requested_project(BUILTIN_LIST_TOOLS)
        except (ProjectNotNamed, ProjectIsClaudeSettings):
            return None

    def _tool_list(self) -> list[types.Tool]:
        types = self._mcp_types()
        builtins = [
            types.Tool(
                name=BUILTIN_PING_TOOL,
                description="Health check for the CDD MCP host process.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name=BUILTIN_RESTART_TOOL,
                description="Restart the CDD MCP host on the code as it is now: reload its Python and start its toolsets again, on the same connection.",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]
        enrolled = (*self._checkout_server.tools.values(), *self._checkout_server.prompts.values())
        listed = [types.Tool(name=tool.mcp_name, description=tool.listed_description or None, inputSchema=tool.input_schema) for tool in enrolled]
        return [*builtins, *listed]

    async def _answer_chat(self, name: str, arguments: dict[str, object] | None) -> types.CallToolResult:
        """Answer one call a chat sent. A failure is logged and raised as *_ChatCallFailed*, which the protocol answers
        as an error result naming it, so the client shows a failed call rather than the tool's output."""
        types = self._mcp_types()
        try:
            call = self._call_from_chat(name, arguments)
            value = await self._answer_off_loop(call)
            if call.request.tool == BUILTIN_RESTART_TOOL:
                await self._announce_tool_list_changed()
            return types.CallToolResult(content=self._content_blocks(value))
        except Exception as failure:
            logger.exception("MCP tool %s failed", name)
            raise _ChatCallFailed(failure) from failure

    def _call_from_chat(self, name: str, arguments: dict[str, object] | None) -> ToolCall:
        """The call as the chat sent it: the tool it names, the project its header names, and the chat its arguments
        name, answered by this host for that chat."""
        resolved = self._checkout_server.resolve_call_name(name)
        return ToolCall.sent(arguments, self._requested_project(resolved), ToolRequest(self._requesting_chat(), resolved, self, answers_a_chat=True))

    def _requesting_chat(self) -> ChatPointer | None:
        """The chat the request comes from, so what it keeps open is its own and never shared with every chat in the
        same folder: the session the Claude Code process ``X-CDD-Chat-Process`` names runs now, else the chat
        ``X-CDD-Chat`` names; none when the request names neither."""
        headers = self._request_headers()
        process = self._requesting_process(headers)
        running = process.session_id if process is not None else ""
        return ChatPointer.from_request(running or headers.get(CHAT_HEADER) or "")

    async def _answer_off_loop(self, call: ToolCall) -> SentValue:
        """Run the call on a worker thread, because a synchronous call on the event loop holds every other chat's
        requests. A call still running at its time limit keeps running and is reported as still running, not failed.
        ``cdd.ping`` answers on the event loop itself, so it says whether the loop answers, whatever the worker threads
        are busy with."""
        if call.request.tool == BUILTIN_PING_TOOL:
            return PONG
        seconds = self._checkout_server.call_seconds(call.request.tool)
        answer = await self._tool_calls.run(call, seconds, self._progress_reporter())
        return answer.message if isinstance(answer, _StillRunning) else answer

    async def _announce_tool_list_changed(self) -> None:
        """A restart can add or drop tools, so the client is told to list them again."""
        context = self._request_context()
        if context is not None:
            await context.session.send_tool_list_changed()

    def _progress_reporter(self) -> Callable[[str], None] | None:
        """Sends a tool's progress reports as notifications for its call, when the caller asked for them with a progress
        token. The tool runs on a worker thread, so each report goes back through the event loop, at most four a
        second (*ThrottledReporter*), however often the tool reports."""
        context = self._request_context()
        if context is None:
            return None
        token = context.meta.progressToken if context.meta else None
        if token is None:
            return None
        reported = iter(range(1, sys.maxsize))

        def report(message: str) -> None:
            import anyio.from_thread

            anyio.from_thread.run(context.session.send_progress_notification, token, next(reported), None, message)

        return ThrottledReporter(report)

    def _requested_project(self, tool: str) -> Path | None:
        """The project the calling chat works on: the folder its session works in now, read on every call. That is the
        folder Claude Code records for the process ``X-CDD-Chat-Process`` names, else the folder the transcript of the
        session that process runs records last, else that of the chat ``X-CDD-Chat`` names, else the ``X-CDD-Project``
        header. A desktop spare folder counts as no folder at any step. Headers are sent once, when the chat
        connects, so the project header holds the folder the chat started in, such as the desktop app's spare folder,
        which is wrong once the chat moves. Only ``cdd.ping`` and ``cdd.restart`` work without
        one; anything else would act on whichever folder the server started in."""
        headers = self._request_headers()
        named = headers.get(PROJECT_HEADER)
        if tool in (BUILTIN_PING_TOOL, BUILTIN_RESTART_TOOL):
            return Path(named) if named else None
        project = self._folder_the_chat_works_in(headers)
        if project is None:
            raise ProjectNotNamed(tool)
        if project.resolve() == self._claude_settings:
            raise ProjectIsClaudeSettings(tool, project)
        return project

    def _folder_the_chat_works_in(self, headers: Mapping[str, str]) -> Path | None:
        """The first folder the request's chat is known to work in, in the order ``_requested_project`` gives."""
        # A desktop spare folder is never the project: it only means the chat has not reached its folder yet.
        connected_from = Path(headers[PROJECT_HEADER]) if self._names_a_project(headers) else None
        process = self._requesting_process(headers)
        return (
            (process.working_folder if process is not None else None)
            or self._folder_of_chat(process.session_id if process is not None else None)
            or self._folder_of_chat(headers.get(CHAT_HEADER))
            or connected_from
        )

    def _requesting_process(self, headers: Mapping[str, str]) -> ClaudeChatProcess | None:
        """The Claude Code process the request comes from: the one ``X-CDD-Chat-Process`` names, else, when the request
        names no project either, the one holding the request's connection. Claude Code runs the headers helper once,
        when a chat connects, and the desktop app can connect a chat from its spare folder before it records the
        chat's process, so those headers stay that way for the whole connection."""
        named = ClaudeChatProcess.from_header(headers.get(CHAT_PROCESS_HEADER))
        if named is not None or self._names_a_project(headers):
            return named
        return ClaudeChatProcess.from_connection(self._request_client_port())

    def _names_a_project(self, headers: Mapping[str, str]) -> bool:
        """Whether ``X-CDD-Project`` names a folder to work in: a desktop spare folder only means the chat has not
        reached its folder yet."""
        named = headers.get(PROJECT_HEADER)
        return bool(named) and not is_desktop_spare(Path(named))

    def _request_headers(self) -> Mapping[str, str]:
        """The headers of the request being answered; none for a call made outside a request."""
        request = self._current_request()
        return request.headers if request is not None else {}

    def _request_client_port(self) -> int | None:
        """The port the caller's end of the request's connection uses; none outside a request or over no connection."""
        client = getattr(self._current_request(), "client", None)
        return client[1] if client else None

    def _current_request(self) -> Any:
        context = self._request_context()
        return context.request if context is not None else None

    def _folder_of_chat(self, chat_id: str | None) -> Path | None:
        chat = ChatPointer.from_claude_session(chat_id or "")
        return chat.working_folder if chat is not None else None

    def _answer_reporting(self, call: ToolCall, reporter: Callable[[str], None] | None) -> object:
        """Answer a chat's call on its worker thread: its progress goes to reporter. The call says it answers a chat
        (``call.request.answers_a_chat``), so work it starts that would hold the interpreter runs in a worker process."""
        # Read it from its module as it is now: a restart imports it again, and tools read the new one.
        from harness.agent_tools.progress import reporting_to

        # The answer is read into JSON while the call is still the one being answered: properties such as a board's
        # active ticket depend on the chat that asked, and read after the call they would answer for no chat.
        with reporting_to(reporter), CALLS_BEING_ANSWERED.answering(call):
            value = self.answer(call)
            return value if isinstance(value, str) else data_of(value)

    def dispatch(self, name: str, arguments: dict[str, object] | None = None, project: Path | None = None) -> object:
        """Run one tool call made in process on project; one that names no project works on the folder ``CDD_PROJECT``
        names, else the current folder. A true ``ping`` argument answers without entering the tool."""
        resolved = self._checkout_server.resolve_call_name(name)
        call = ToolCall.sent(arguments, project or self._project_named_outside_a_chat(), ToolRequest(tool=resolved, mcp_host=self))
        return self.answer(call)

    def answer(self, call: ToolCall) -> object:
        """Answer call: the built-in ping and restart here, any other tool on the server of the project it names."""
        if call.request.tool == BUILTIN_PING_TOOL:
            return PONG
        other_lane = self._other_lane_answering(call)
        if other_lane is not None:
            return other_lane.answer(call)
        if call.request.tool == BUILTIN_RESTART_TOOL:
            return self.restart()
        if call.request.tool == BUILTIN_LIST_TOOLS:
            return self.tools_listed_for(None)
        with self._restart_gate.running_call():
            return self._answer_between_restarts(call)

    def route_between_lanes(self, lanes: ServerLanes, home: CddHome) -> None:
        """Answer as the server running from home: as the stable lane, hand each call whose project runs on the dev lane
        to the dev lane's server."""
        self._lanes = lanes
        self._home = home

    def _other_lane_answering(self, call: ToolCall) -> ServerLane | None:
        if self._lanes is None or self._home is None:
            return None
        return self._lanes.other_lane_answering(self._home, call.project)

    def _project_named_outside_a_chat(self) -> Path:
        """The project of a call made in process, which no chat names: the folder ``CDD_PROJECT`` names, else the
        current folder. ``CDD_REPO`` names the checkout serving the tools, never the project."""
        named = os.environ.get("CDD_PROJECT")
        return Path(named).resolve() if named else Path.cwd().resolve()

    def _answer_between_restarts(self, call: ToolCall) -> object:
        server = self._server_for(call.project)
        try:
            if call.arguments.get("ping") is True:
                return self._ping_tool(call.request.tool)
            return server.answer(call.request.tool, call)
        except BaseException as failure:
            self._log_failure(call, failure)
            raise

    def _ping_tool(self, tool: str) -> dict[str, str]:
        if self._checkout_server.enrolled(tool) is None:
            raise ToolNotEnrolled(tool)
        return {"ping": "pong", "tool": tool}

    def _log_failure(self, call: ToolCall, failure: BaseException) -> None:
        session = call.session
        if session is not None:
            session.log.by(call.request.chat).failure(failure, tool=call.request.tool)

    def _content_blocks(self, answer: SentValue) -> list[types.TextContent]:
        types = self._mcp_types()
        text = answer if isinstance(answer, str) else json.dumps(data_of(answer))
        return [types.TextContent(type="text", text=text)]

    def serve(self, daemon: McpDaemon, listener: socket.socket) -> None:
        """Answer every chat over HTTP on ``listener``, which ``daemon`` claimed, until the process is stopped."""
        import uvicorn

        from harness.mcp.listening_loop import _ListeningLoop

        daemon.this_process.publish(self._checkout_server.repo)
        self.route_between_lanes(ServerLanes.from_serving(daemon.home, daemon.address), daemon.home)
        try:
            server = uvicorn.Server(uvicorn.Config(self._http_app(daemon.port), log_level="warning"))
            asyncio.run(server.serve(sockets=[listener]), loop_factory=_ListeningLoop(server).new_event_loop)
        finally:
            daemon.this_process.withdraw()

    def _http_app(self, port: int) -> Any:
        """MCP over Streamable HTTP at ``/mcp`` and a ``/ping`` that says which pid and checkout are serving. Only this
        machine's own clients get in: the Host must name this port, and a browser page's Origin is refused."""
        from mcp.server.fastmcp.server import StreamableHTTPASGIApp
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
        from mcp.server.transport_security import TransportSecuritySettings
        from starlette.applications import Starlette
        from starlette.routing import Route

        security = TransportSecuritySettings(allowed_hosts=[f"127.0.0.1:{port}", f"localhost:{port}"], allowed_origins=[])
        # A chat can sit idle for hours, so its session lives until the chat closes it.
        manager = StreamableHTTPSessionManager(app=self._protocol, security_settings=security, session_idle_timeout=None)

        return Starlette(
            routes=[
                Route(PING_PATH, self._answer_ping),
                Route(LANE_CALL_PATH, self._answer_lane_call, methods=["POST"]),
                Route(MCP_PATH, endpoint=StreamableHTTPASGIApp(manager)),
            ],
            lifespan=lambda _app: manager.run(),
        )

    async def _answer_lane_call(self, request: Request) -> JSONResponse:
        """Answer a tool call the other lane's server handed over, for the chat that sent it there. Only a server on
        this machine may hand one over: a browser page, which names its Origin, is refused."""
        from starlette.responses import JSONResponse

        if request.headers.get("origin"):
            return JSONResponse({"failure": {"kind": "LaneCallRefused", "message": "a browser page may not hand over tool calls"}}, status_code=403)
        lane_call = LaneCall.from_data(await request.json())
        return JSONResponse(await self._lane_reply(self._call_from_lane(lane_call)))

    def _call_from_lane(self, lane_call: LaneCall) -> ToolCall:
        request = ToolRequest(ChatPointer.from_request(lane_call.chat), lane_call.tool, self, answers_a_chat=True)
        return ToolCall.sent(lane_call.arguments, lane_call.project or None, request)

    async def _lane_reply(self, call: ToolCall) -> dict[str, Any]:
        """The reply the other lane reads: the answer, or the failure named by its kind and message, so the chat sees
        the same failure it would have seen here."""
        import anyio.to_thread

        try:
            return {"answer": await anyio.to_thread.run_sync(self._answer_reporting, call, None)}
        except Exception as failure:  # noqa: BLE001 - handed back by name to the lane that raises it for the chat
            return {"failure": {"kind": type(failure).__name__, "message": str(failure)}}

    async def _answer_ping(self, _request: Request) -> JSONResponse:
        """The ``/ping`` answer: which process and checkout serve, and the projects its chats work on."""
        from starlette.responses import JSONResponse

        return JSONResponse(
            {"ok": True, "pid": os.getpid(), "source": str(self._checkout_server.repo), "projects": [str(project) for project in self.projects]}
        )

    def restart(self) -> dict[str, Any]:
        """Swap in a server on the code as it is now, for every chat. Connections, and this host object holding them,
        stay. Each project's toolsets start again on the new code the next time a call names it."""
        # A call running on the old classes would find their modules gone, so the restart waits for it to end.
        with self._restart_gate.restarting():
            self._checkout_server = self._checkout_server.restarted()
            with self._servers_lock:
                self._servers = {self._checkout_server.project: self._checkout_server}
        self._publish_mods()
        tools = self._checkout_server.tools
        return {"is_restarted": True, "tools": len(tools) + len(self._checkout_server.prompts), "exceptions": self._checkout_server.skipped.as_data}

    def _publish_mods(self) -> None:
        """Publish the chat bar and the prompt queue from the code the server now runs, so a chat watching the published
        copy reloads it with the server's restart rather than at the next install."""
        if self._home is not None and self._home.is_installed:
            self._home.write_mod_plugins()

    def diagnose(self) -> dict[str, Any]:
        """What this host publishes: the ping's answer, every tool name, and what start-up skipped."""
        server = self._checkout_server
        return {
            "ok": True,
            "ping": PONG,
            "tools": [BUILTIN_PING_TOOL, BUILTIN_RESTART_TOOL, *sorted(server.tools), *sorted(server.prompts)],
            "exceptions": server.skipped.as_data,
            "notice": server.skipped.notice,
        }

    @classmethod
    def from_repo(cls, repo: Path | str) -> McpHost:
        """A host over every annotated toolset in ``repo``, in this process, to check it stands up."""
        resolved = Path(repo).resolve()
        toolsets = RepositoryToolsets(resolved)
        try:
            server = McpServer(repo=resolved, project=resolved)
            server.start(toolsets.classes())
            for unloadable in toolsets.unloadable:
                server.skipped.skip(unloadable.reference, unloadable.cause)
            return cls._serving(server)
        except Exception as error:
            raise McpStandupFailed(resolved, error) from error

    @classmethod
    def from_refs(cls, toolset_refs: tuple[str, ...], *, repo: str | None = None, project: str | None = None) -> McpHost:
        """A host over the toolsets the ``module:Class`` references name, as a process is started with them."""
        server = McpServer(repo=repo, project=project)
        if toolset_refs:
            server.start(toolset_refs)
        return cls._serving(server)

    @classmethod
    def _serving(cls, server: McpServer) -> McpHost:
        host = cls(server)
        server.skipped.notify()
        return host


SERVER_CHANNELS.register(McpInstallation)
