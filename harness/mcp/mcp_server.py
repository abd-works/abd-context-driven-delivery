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
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

import anyio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from harness.agent_tools.agent_tools import AgentTool, AgentToolSet, InstallDestination, ToolsetReference
from harness.agent_tools.chat_pointer import ChatPointer
from harness.agent_tools.claude_chat_process import ClaudeChatProcess, is_desktop_spare
from harness.agent_tools.tool_call import ToolCall
from harness.installation.destination import ServerInstallation, SkippedTool, SkippedTools
from harness.installation.data_class import data_of
from harness.installation.ide_layout import IdeLayout
from harness.installation.installer import Installer
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.installation.repository_toolsets import RepositoryToolsets
from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_annotations import LongCall, Mcp  # noqa: F401 - importing the server defines Mcp, the channel install reads
from harness.mcp.claude_plugins import ClaudePlugins
from harness.mcp.mcp_daemon import CHAT_HEADER, CHAT_PROCESS_HEADER, MCP_PATH, PING_PATH, PROJECT_HEADER, McpDaemon
from harness.mcp.server_hooks import CddServerHooks
from harness.mcp.restart_gate import _RestartGate
from harness.mcp.tool_calls import ThrottledReporter, _StillRunning, _ToolCalls

logger = logging.getLogger(__name__)
BUILTIN_PING_TOOL = "cdd.ping"
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


class McpInstallation(ServerInstallation):
    """Record ``@mcp`` operations, write each IDE's ``cdd`` entry, and start the one cdd server from ``~/.cdd``. Every
    install also publishes the hooks that start that server (*CddServerHooks*), and, for Claude Code, the cdd and
    board plugins."""

    channel = "mcp"
    toolsets = (CddServerHooks,)

    def __init__(
        self,
        layout: IdeLayout,
        path: Path | str,
        repo: Path | str | None = None,
        home: CddHome | None = None,
    ) -> None:
        super().__init__(layout, path, repo=repo)
        self.server_home = home or CddHome()
        self.daemon = McpDaemon(self.server_home)
        self.claude_plugins = ClaudePlugins(self.server_home)
        self.mcp_operations: list[AgentTool] = []
        self.host: McpHost | None = None
        self.diagnosis: dict[str, Any] | None = None

    def write(self, tool: AgentTool) -> None:
        if not tool.install_to_mcp:
            return
        self.record_operation(tool)
        self.write_mcp_manifest()

    def record_operation(self, tool: AgentTool) -> None:
        if not tool.install_to_mcp:
            return
        self.mcp_operations.append(tool)

    @property
    def published(self) -> list[str]:
        return sorted(str(tool.mcp_name) for tool in self.mcp_operations)

    @property
    def _user_level(self) -> bool:
        """Whether the entry goes in the IDE's user-level MCP config. A temp install tree keeps its entry in the tree,
        so specs never touch the user's own config."""
        return self.layout.user_mcp_config is not None and not self.is_temporary

    @property
    def manifest_path(self) -> Path:
        """The IDE's user-level MCP config. A temp install tree keeps ``<ide>/mcp.json``
        (Claude Code: ``.mcp.json`` at the project root) so specs never touch the user's own."""
        if self._user_level:
            return self.layout.user_mcp_config
        if self.layout.is_claude_code:
            return self._project_root() / ".mcp.json"
        return self.path / self.layout.MCP_CONFIG_NAME

    def write_mcp_manifest(self) -> None:
        if not self.mcp_operations:
            return
        dest = self.manifest_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if self.layout.is_claude_code and self._user_level:
            self.allow_cdd_tools(self.layout.user_settings_folder / "settings.json")
            self.drop_project_cdd_server()
            self.drop_user_cdd_server()
            for written in self.server_home.write_claude_plugin(self._claude_plugin_server()):
                self.track_write(written)
            return
        manifest = self._server_manifest()
        if self._has_cdd_entry(dest, manifest):
            self.track_write(dest)
            return
        if self.layout.is_claude_code or self._user_level:
            manifest = self._merged_with_other_servers(dest, manifest)
        self._ide_config(dest).write(manifest)
        self.track_write(dest)

    def allow_cdd_tools(self, settings: Path) -> None:
        """Let Claude Code call every ``cdd`` tool without a prompt. The user's settings file
        holds their own permissions too, so add the one entry and never track the file for clean."""
        settings_file = self._ide_config(settings)
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

    def drop_project_cdd_server(self) -> None:
        """A ``cdd`` entry in the project's ``.mcp.json`` outranks the user-level host in Claude
        Code, so it goes; the project's other servers stay, and a file left holding nothing goes too."""
        self._drop_cdd_entry(self._project_root() / ".mcp.json", "project's", remove_when_empty=True)

    def drop_user_cdd_server(self) -> None:
        """Claude Code runs a user-level entry's headersHelper in ``~/.claude`` for every chat, so the entry names no
        chat's project; the cdd plugin replaces it. ``~/.claude.json`` holds the app's own state too, so only ``cdd`` goes."""
        if self._user_level:
            self._drop_cdd_entry(self.layout.user_mcp_config, "user's", remove_when_empty=False)

    def _drop_cdd_entry(self, config: Path, whose: str, *, remove_when_empty: bool) -> None:
        config_file = self._ide_config(config)
        try:
            data = config_file.read()
        except McpConfigUnreadable as unreadable:
            logger.warning("a cdd entry in the %s config may still outrank the cdd plugin: %s", whose, unreadable)
            return
        servers = data.get(self.layout.mcp_servers_key)
        if not isinstance(servers, dict) or "cdd" not in servers:
            return
        del servers["cdd"]
        if remove_when_empty and not servers and len(data) == 1:
            config.unlink()
            return
        config_file.write(data)

    def _claude_plugin_server(self) -> dict[str, Any]:
        """The cdd server as the cdd plugin declares it: Claude Code fills in ``${CLAUDE_PROJECT_DIR}`` with the chat's
        folder and passes it to the connect script."""
        home = self.server_home
        helper = f'"{home.interpreter.executable}" "{home.connect_script}" "${{CLAUDE_PROJECT_DIR}}"'
        return {"type": "http", "url": self.daemon.url, "headersHelper": helper}

    def _server_manifest(self) -> dict[str, Any]:
        """The one ``cdd`` entry: the shared server's URL plus how each request names its project. A user-level entry
        serves every project, so it names the open one; a temp install tree names its own."""
        server: dict[str, Any] = {"type": "http", "url": self.daemon.url}
        if self._user_level:
            server["headers"] = {PROJECT_HEADER: IdeLayout.PROJECT_FOLDER}
        else:
            server["headers"] = {PROJECT_HEADER: str(self._project_root().resolve())}
        if not self.layout.names_mcp_transport:
            del server["type"]
        return {self.layout.mcp_servers_key: {"cdd": server}}

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

    def _project_root(self) -> Path:
        path = Path(self.path)
        return path.parent if path.name == self.layout.folder_name else path

    def standup(self) -> McpHost | None:
        """A host over every toolset in this installation's checkout, in this process, to check it stands up; none
        inside the cdd server, which already serves them."""
        if self.serves_this_process():
            return None
        self.host = McpHost.from_repo(self._checkout)
        return self.host

    def diagnose(self) -> dict[str, Any]:
        host = self.host if self.host is not None else self.standup()
        self.diagnosis = host.diagnose() if host is not None else {}
        return self.diagnosis

    def ensure_running(self) -> dict[str, str]:
        """Start the one cdd server when none answers; for Claude Code also install the cdd and board plugins, which
        declare the server to every chat."""
        status = {"mcp": self.ensure_server()}
        if self.layout.is_claude_code:
            status["cdd plugin"] = self.claude_plugins.install_cdd()
            status["board"] = self.claude_plugins.install_board()
        return status

    def status(self) -> list[str]:
        return [f"cdd server: {'running' if self.daemon.is_running() else 'not running'}"]

    def ensure_server(self) -> str:
        """Install ``~/.cdd/`` on first use and start the one server when none answers. An install that finds a
        server already running leaves it, and the code it serves, alone."""
        return self.daemon.ensure_from(self._checkout)

    def pin_server(self) -> str:
        """Serve this checkout's current commit from ``~/.cdd/runtime``, restarting the server onto it."""
        return self.daemon.pin_from(self._checkout)

    def keep_pinned_current(self) -> str | None:
        """After a plain install, serve this checkout's current commit when the server is pinned to an older one, so
        every chat runs the code just installed. Left alone: a server serving a checkout on disk, an install run from
        a linked worktree (its commit is not what every chat should run), and an install run inside the server itself.
        Returns the server's status when it was restarted, else None."""
        home = self.daemon.home
        if self.serves_this_process() or (self._checkout / ".git").is_file():
            return None
        if home.is_installed and home.mode != home.PINNED:
            return None
        if home.is_installed and home.is_pinned_to(self._checkout) and self.daemon.is_running():
            return None
        return self.pin_server()

    def serve_from_checkout(self) -> str:
        """Serve this checkout as it is on disk, for working on CDD itself, restarting the server onto it."""
        return self.daemon.serve_checkout(self._checkout)

    def serves_this_process(self) -> bool:
        """True when this process is the cdd server, as it is when an install runs as one of its tool calls."""
        return self.daemon.runs_this_process()

    @property
    def _checkout(self) -> Path:
        return Path(self.repo or RepositoryToolsets.of_running_checkout().root).resolve()


class McpServer:
    """The toolsets one project's calls are answered by: every ``@mcp`` operation of the toolsets it was started with,
    published under its MCP name, made for that project."""

    def __init__(
        self,
        *,
        repo: str | Path | None = None,
        project: str | Path | None = None,
    ) -> None:
        self.repo = Path(repo).resolve() if repo is not None else RepositoryToolsets.of_running_checkout().root
        self.project = Path(project).resolve() if project is not None else self.repo
        self.venv = self.repo / ".venv"
        self._tools: dict[str, AgentTool] = {}
        self._prompts: dict[str, AgentTool] = {}
        self.skipped = SkippedTools("MCP", "tools")
        self._started = False
        self._toolsets: tuple[Any, ...] = ()

    @property
    def started(self) -> bool:
        return self._started

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
        for item in self._toolsets:
            for toolset in self._loaded(item):
                self._enroll_with_children(toolset)
        self._started = True

    def _loaded(self, item: Any) -> list[Any]:
        try:
            return AgentToolSet.from_items([item])
        except AgentToolSet.LOAD_FAILURES as error:
            self.skipped.skip(str(item), error)
            return []

    def _enroll_with_children(self, toolset: Any) -> None:
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

    def _is_checkout_module(self, module: Any) -> bool:
        """Whether module was imported from this checkout. A package folder with no ``__init__.py`` has no file, only
        its folders, and kept while the packages around it are forgotten it looks for a parent that is gone."""
        folders = list(getattr(module, "__path__", None) or [])
        return any(self._is_checkout_file(file) for file in (getattr(module, "__file__", None), *folders))

    def _is_checkout_file(self, file: str | None) -> bool:
        if not file:
            return False
        path = Path(file).resolve()
        return self.repo in path.parents and self.venv not in path.parents

    def _enroll_toolset(self, toolset: Any) -> None:
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
            if AgentTool.spelled(name) == AgentTool.spelled(builtin):
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

    def invoke_tool(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        """Call the tool published as mcp_name on this server's project."""
        return self.answer_tool(mcp_name, ToolCall(arguments, self.project, tool=mcp_name))

    def invoke_prompt(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        """The instructions published as mcp_name, expanded for a call on this server's project."""
        return self.answer_prompt(mcp_name, ToolCall(arguments, self.project, tool=mcp_name))

    def answer_tool(self, mcp_name: str, call: ToolCall) -> object:
        """Answer call with the tool published as mcp_name."""
        return self._answer_from(self._tools, mcp_name, call)

    def answer_prompt(self, mcp_name: str, call: ToolCall) -> object:
        """Answer call with the instructions published as mcp_name, expanded for it."""
        return self._answer_from(self._prompts, mcp_name, call)

    def _answer_from(self, published: dict[str, AgentTool], mcp_name: str, call: ToolCall) -> object:
        """Answer call with what published holds under mcp_name, or under the name a client spelled it."""
        resolved = self.resolve_call_name(mcp_name)
        if resolved not in published:
            raise ToolNotEnrolled(resolved)
        return published[resolved].answer(call)


class _ProjectNamedOnly:
    """The ``/mcp`` endpoint for requests that name their project. A request that names none is refused as a bad
    request (400), naming the missing header. It is never refused as unauthorized (401): Claude Code answers a 401 with
    a sign-in attempt, Dynamic Client Registration, which this server does not offer, and then cuts cdd off for that
    chat until its plugins are reloaded."""

    def __init__(self, app: Any) -> None:
        self._app = app
        self._header = PROJECT_HEADER.lower().encode("latin-1")
        self._refusal = {"error": f"name the chat's project in the {PROJECT_HEADER} header"}

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        from starlette.responses import JSONResponse

        if scope["type"] == "http" and not any(name == self._header and value for name, value in scope["headers"]):
            await JSONResponse(self._refusal, status_code=400)(scope, receive, send)
            return
        await self._app(scope, receive, send)


class ProjectNotNamed(Exception):
    """A tool call arrived from a chat whose folder the server cannot find, so it cannot tell which project it is for."""

    def __init__(self, tool: str) -> None:
        super().__init__(
            f"{tool} was called from a chat whose folder the server cannot find: the X-CDD-Project header names none or "
            "only a desktop spare folder, and neither the chat's Claude Code process, the process holding its "
            "connection, nor its transcript records one. Open the chat in a project folder and run /reload-plugins so "
            "the cdd header helper runs again; when it still fails, run python scripts/install.py from a CDD checkout "
            "to write the cdd entry again."
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


class _CddProtocolServer(Server):
    """The MCP protocol server, telling every client that a restart can change the tool list."""

    def create_initialization_options(
        self,
        notification_options: NotificationOptions | None = None,
        experimental_capabilities: dict[str, dict[str, Any]] | None = None,
    ) -> InitializationOptions:
        return super().create_initialization_options(
            notification_options or NotificationOptions(tools_changed=True), experimental_capabilities
        )


class McpHost:
    """The cdd server's MCP side: one *McpServer* for each project a chat works on, answering every chat. The server
    on the checkout it serves from answers the tool list, which every project shares, and gives each new project its
    toolsets."""

    def __init__(self, checkout_server: McpServer) -> None:
        self._checkout_server = checkout_server
        self._servers: dict[Path, McpServer] = {checkout_server.project: checkout_server}
        self._servers_lock = threading.Lock()
        self._restart_gate = _RestartGate()
        self._tool_calls = _ToolCalls()
        self._protocol = _CddProtocolServer("cdd")
        # A user-level cdd entry names Claude Code's own settings folder as its project; calls naming it are refused.
        self._claude_settings = IdeLayout("Claude").user_settings_folder.resolve()
        self._register_handlers()

    @property
    def checkout_server(self) -> McpServer:
        """The server on the checkout this host serves from: the tools every chat lists, and what start-up skipped."""
        return self._checkout_server

    def server_for(self, project: Path) -> McpServer:
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

    def _register_handlers(self) -> None:
        @self._protocol.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            return self._tool_list()

        @self._protocol.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, object] | None) -> types.CallToolResult:
            result = await self._answer_chat(name, arguments)
            # A worker thread runs to the end even when the client cancels it, and
            # the cancellation has already answered the request. Stop here, because
            # a second answer raises in the MCP session and takes down the host.
            await anyio.lowlevel.checkpoint()
            return result

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

    def _tool_list(self) -> list[types.Tool]:
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
        """Answer one call a chat sent. A failure goes back as an error result, which the client shows as a failed call
        rather than as the tool's output."""
        try:
            call = self._call_from_chat(name, arguments)
            value = await self._answer_off_loop(call)
            if call.tool == BUILTIN_RESTART_TOOL:
                await self._announce_tool_list_changed()
            return types.CallToolResult(content=self._content_blocks(value))
        except Exception as failure:
            logger.exception("MCP tool %s failed", name)
            text = f"{type(failure).__name__}: {failure}"
            return types.CallToolResult(content=[types.TextContent(type="text", text=text)], isError=True)

    def _call_from_chat(self, name: str, arguments: dict[str, object] | None) -> ToolCall:
        """The call as the chat sent it: the tool it names, the project its header names, and the chat its arguments
        name, answered by this host for that chat."""
        resolved = self._checkout_server.resolve_call_name(name)
        return ToolCall.sent(arguments, self._requested_project(resolved), tool=resolved, mcp_host=self, answers_a_chat=True, sender=self._requesting_chat())

    def _requesting_chat(self) -> ChatPointer | None:
        """The chat the request comes from, so what it keeps open is its own and never shared with every chat in the
        same folder: the session the Claude Code process ``X-CDD-Chat-Process`` names runs now, else the chat
        ``X-CDD-Chat`` names; none when the request names neither."""
        headers = self._request_headers()
        process = self._requesting_process(headers)
        running = process.session_id if process is not None else ""
        return ChatPointer.from_request(running or headers.get(CHAT_HEADER) or "")

    async def _answer_off_loop(self, call: ToolCall) -> object:
        """Run the call on a worker thread, because a synchronous call on the event loop holds every other chat's
        requests. A call still running at its time limit keeps running and is reported as still running, not failed.
        ``cdd.ping`` answers on the event loop itself, so it says whether the loop answers, whatever the worker threads
        are busy with."""
        if call.tool == BUILTIN_PING_TOOL:
            return self.ping()
        seconds = self._checkout_server.call_seconds(call.tool)
        answer = await self._tool_calls.run(
            call, seconds, lambda reporter: self._answer_reporting(call, reporter), self._progress_reporter()
        )
        return answer.message if isinstance(answer, _StillRunning) else answer

    async def _announce_tool_list_changed(self) -> None:
        """A restart can add or drop tools, so the client is told to list them again."""
        try:
            await self._protocol.request_context.session.send_tool_list_changed()
        except LookupError:
            return

    def _progress_reporter(self) -> Callable[[str], None] | None:
        """Sends a tool's progress reports as notifications for its call, when the caller asked for them with a progress
        token. The tool runs on a worker thread, so each report goes back through the event loop, at most four a
        second (*ThrottledReporter*), however often the tool reports."""
        try:
            context = self._protocol.request_context
        except LookupError:
            return None
        token = context.meta.progressToken if context.meta else None
        if token is None:
            return None
        reported = iter(range(1, sys.maxsize))

        def report(message: str) -> None:
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
        # A desktop spare folder is never the project: it only means the chat has not reached its folder yet.
        connected_from = Path(named) if self._names_a_project(headers) else None
        process = self._requesting_process(headers)
        project = (
            (process.working_folder if process is not None else None)
            or self._folder_of_chat(process.session_id if process is not None else None)
            or self._folder_of_chat(headers.get(CHAT_HEADER))
            or connected_from
        )
        if project is None:
            raise ProjectNotNamed(tool)
        if project.resolve() == self._claude_settings:
            raise ProjectIsClaudeSettings(tool, project)
        return project

    def _requesting_process(self, headers: Any) -> ClaudeChatProcess | None:
        """The Claude Code process the request comes from: the one ``X-CDD-Chat-Process`` names, else, when the request
        names no project either, the one holding the request's connection. Claude Code runs the headers helper once,
        when a chat connects, and the desktop app can connect a chat from its spare folder before it records the
        chat's process, so those headers stay that way for the whole connection."""
        named = ClaudeChatProcess.from_header(headers.get(CHAT_PROCESS_HEADER))
        if named is not None or self._names_a_project(headers):
            return named
        return ClaudeChatProcess.from_connection(self._request_client_port())

    def _names_a_project(self, headers: Any) -> bool:
        """Whether ``X-CDD-Project`` names a folder to work in: a desktop spare folder only means the chat has not
        reached its folder yet."""
        named = headers.get(PROJECT_HEADER)
        return bool(named) and not is_desktop_spare(Path(named))

    def _request_headers(self) -> Any:
        """The headers of the request being answered; none for a call made outside a request."""
        request = self._current_request()
        return request.headers if request is not None else {}

    def _request_client_port(self) -> int | None:
        """The port the caller's end of the request's connection uses; none outside a request or over no connection."""
        client = getattr(self._current_request(), "client", None)
        return client[1] if client else None

    def _current_request(self) -> Any:
        try:
            return self._protocol.request_context.request
        except LookupError:
            return None

    def _folder_of_chat(self, chat_id: str | None) -> Path | None:
        chat = ChatPointer.from_claude_session(chat_id or "")
        return chat.working_folder if chat is not None else None

    def _answer_reporting(self, call: ToolCall, reporter: Callable[[str], None] | None) -> object:
        """Answer a chat's call on its worker thread: its progress goes to reporter. The call says it answers a chat
        (``call.answers_a_chat``), so work it starts that would hold the interpreter runs in a worker process."""
        # Read it from its module as it is now: a restart imports it again, and tools read the new one.
        from harness.agent_tools.progress import reporting_to

        # The answer is read into JSON while the call is still the one being answered: properties such as a board's
        # active ticket depend on the chat that asked, and read after the call they would answer for no chat.
        with reporting_to(reporter), call.being_answered():
            value = self.answer(call)
            return value if isinstance(value, str) else data_of(value)

    def dispatch(self, name: str, arguments: dict[str, object] | None = None, project: Path | None = None) -> object:
        """Run one tool call made in process on project; one that names no project works on the folder ``CDD_PROJECT``
        names, else the current folder. A true ``ping`` argument answers without entering the tool."""
        resolved = self._checkout_server.resolve_call_name(name)
        call = ToolCall.sent(arguments, project or self._project_named_outside_a_chat(), tool=resolved, mcp_host=self)
        return self.answer(call)

    def answer(self, call: ToolCall) -> object:
        """Answer call: the built-in ping and restart here, any other tool on the server of the project it names."""
        if call.tool == BUILTIN_PING_TOOL:
            return self.ping()
        if call.tool == BUILTIN_RESTART_TOOL:
            return self.restart()
        with self._restart_gate.running_call():
            return self._answer_between_restarts(call)

    def _project_named_outside_a_chat(self) -> Path:
        """The project of a call made in process, which no chat names: the folder ``CDD_PROJECT`` names, else the
        current folder. ``CDD_REPO`` names the checkout serving the tools, never the project."""
        named = os.environ.get("CDD_PROJECT")
        return Path(named).resolve() if named else Path.cwd().resolve()

    def _answer_between_restarts(self, call: ToolCall) -> object:
        server = self.server_for(call.project)
        try:
            if call.arguments.get("ping") is True:
                return self._ping_tool(call.tool)
            if call.tool in server.prompts:
                return server.answer_prompt(call.tool, call)
            return server.answer_tool(call.tool, call)
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
            session.log.by(call.chat).failure(failure, tool=call.tool)

    def _content_blocks(self, value: object) -> list[types.TextContent]:
        text = value if isinstance(value, str) else json.dumps(data_of(value))
        return [types.TextContent(type="text", text=text)]

    def serve(self, daemon: McpDaemon, listener: socket.socket) -> None:
        """Answer every chat over HTTP on ``listener``, which ``daemon`` claimed, until the process is stopped."""
        import uvicorn

        from harness.mcp.listening_loop import _ListeningLoop

        daemon.publish(self._checkout_server.repo)
        try:
            server = uvicorn.Server(uvicorn.Config(self.http_app(daemon.port), log_level="warning"))
            asyncio.run(server.serve(sockets=[listener]), loop_factory=_ListeningLoop(server).new_event_loop)
        finally:
            daemon.withdraw()

    def http_app(self, port: int) -> Any:
        """MCP over Streamable HTTP at ``/mcp`` and a ``/ping`` that says which pid and checkout are serving. Only this
        machine's own clients get in: the Host must name this port, and a browser page's Origin is refused."""
        from mcp.server.fastmcp.server import StreamableHTTPASGIApp
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
        from mcp.server.transport_security import TransportSecuritySettings
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route

        security = TransportSecuritySettings(allowed_hosts=[f"127.0.0.1:{port}", f"localhost:{port}"], allowed_origins=[])
        # A chat can sit idle for hours, so its session lives until the chat closes it.
        manager = StreamableHTTPSessionManager(app=self._protocol, security_settings=security, session_idle_timeout=None)

        async def ping(_request: Any) -> JSONResponse:
            return JSONResponse(
                {"ok": True, "pid": os.getpid(), "source": str(self._checkout_server.repo), "projects": [str(item) for item in self.projects]}
            )

        return Starlette(
            routes=[Route(PING_PATH, ping), Route(MCP_PATH, endpoint=_ProjectNamedOnly(StreamableHTTPASGIApp(manager)))],
            lifespan=lambda _app: manager.run(),
        )

    def ping(self) -> str:
        return "pong"

    def restart(self) -> dict[str, Any]:
        """Swap in a server on the code as it is now, for every chat. Connections, and this host object holding them,
        stay. Each project's toolsets start again on the new code the next time a call names it."""
        # A call running on the old classes would find their modules gone, so the restart waits for it to end.
        with self._restart_gate.restarting():
            self._checkout_server = self._checkout_server.restarted()
            with self._servers_lock:
                self._servers = {self._checkout_server.project: self._checkout_server}
        tools = self._checkout_server.tools
        return {"is_restarted": True, "tools": len(tools) + len(self._checkout_server.prompts), "exceptions": self._checkout_server.skipped.as_data}

    def diagnose(self) -> dict[str, Any]:
        """What this host publishes: the ping's answer, every tool name, and what start-up skipped."""
        server = self._checkout_server
        return {
            "ok": True,
            "ping": self.ping(),
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


Installer.installs_through(McpInstallation)
