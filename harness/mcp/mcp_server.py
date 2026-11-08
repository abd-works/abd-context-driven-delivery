"""The ``@mcp`` annotation, the install that writes each IDE's MCP entry, and the cdd server's MCP side: one *McpServer* of
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
from harness.agent_tools.tool_call import ToolCall
from harness.installation.destination import ServerInstallation, SkippedTool, SkippedTools
from harness.installation.data_class import data_of
from harness.installation.ide_layout import IdeLayout
from harness.installation.installer import Installer
from harness.installation.repository_toolsets import RepositoryToolsets
from harness.annotations.annotation import Destination, Annotation
from harness.mcp.cdd_home import CddHome
from harness.mcp.claude_plugins import ClaudePlugins
from harness.mcp.mcp_daemon import MCP_PATH, PING_PATH, PROJECT_HEADER, McpDaemon
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


class Mcp(Destination):
    flag = "_mcp"
    channel = InstallDestination.MCP


mcp = Mcp


class LongCall(Annotation):
    """Annotate an MCP operation whose call may take minutes, such as one that walks the repository, waits on git over the
    network, or probes every other tool. The cdd server waits ``LONG_CALL_SECONDS`` for its answer, not
    ``CALL_SECONDS``, before telling the chat it is still running."""

    flag = "_long_call"


long_call = LongCall


class McpStandupFailed(Exception):
    """The MCP host could not stand up over a checkout's toolsets."""

    def __init__(self, repo: Path, cause: BaseException) -> None:
        super().__init__(f"the MCP host could not stand up over {repo}: {cause}")
        self.repo = repo
        self.cause = cause


class McpConfigUnreadable(Exception):
    """An IDE config file that cdd edits exists but is not readable JSON. cdd leaves it as it is rather than write over
    whatever else it holds."""

    def __init__(self, path: Path, cause: BaseException) -> None:
        super().__init__(f"{path} is not readable JSON ({cause}); fix or remove it, then install again")
        self.path = path
        self.cause = cause


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
        dest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.track_write(dest)

    def allow_cdd_tools(self, settings: Path) -> None:
        """Let Claude Code call every ``cdd`` tool without a prompt. The user's settings file
        holds their own permissions too, so add the one entry and never track the file for clean."""
        try:
            data = self._config_json(settings, {})
        except McpConfigUnreadable as unreadable:
            logger.warning("Claude Code will ask before every cdd tool call: %s", unreadable)
            return
        if not isinstance(data, dict):
            logger.warning("Claude Code will ask before every cdd tool call: %s does not hold a JSON object", settings)
            return
        permissions = data.setdefault("permissions", {})
        allow = permissions.setdefault("allow", [])
        if CLAUDE_TOOLS_PERMISSION in allow:
            return
        allow.append(CLAUDE_TOOLS_PERMISSION)
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

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
        try:
            data = self._config_json(config, None)
        except McpConfigUnreadable as unreadable:
            logger.warning("a cdd entry in the %s config may still outrank the cdd plugin: %s", whose, unreadable)
            return
        servers = data.get(self.layout.mcp_servers_key) if isinstance(data, dict) else None
        if not isinstance(servers, dict) or "cdd" not in servers:
            return
        del servers["cdd"]
        if remove_when_empty and not servers and len(data) == 1:
            config.unlink()
            return
        config.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

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
            existing = self._config_json(dest, {})
        except McpConfigUnreadable:
            return False
        key = next(iter(manifest))
        servers = existing.get(key) if isinstance(existing, dict) else None
        return isinstance(servers, dict) and servers.get("cdd") == manifest[key]["cdd"]

    def _merged_with_other_servers(self, dest: Path, manifest: dict[str, Any]) -> dict[str, Any]:
        """The MCP config is shared with other servers (and, in ``~/.claude.json``, the IDE's own
        state); replace only ``cdd``. A config that cannot be read raises ``McpConfigUnreadable``, because writing it
        anyway would drop every other server it names."""
        existing = self._config_json(dest, {})
        merged = dict(existing) if isinstance(existing, dict) else {}
        key = next(iter(manifest))
        servers = merged.get(key)
        merged[key] = {**(servers if isinstance(servers, dict) else {}), **manifest[key]}
        return merged

    def _config_json(self, path: Path, missing: Any) -> Any:
        """The JSON in ``path``, or ``missing`` when there is no such file."""
        if not path.is_file():
            return missing
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise McpConfigUnreadable(path, error) from error

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
        for name, module in list(sys.modules.items()):
            if self._is_checkout_file(getattr(module, "__file__", None)):
                del sys.modules[name]
        importlib.invalidate_caches()

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
        """Map Cursor's underscore tool id (`slug_op`) back to the enrolled `slug.op`."""
        if name in self._tools or name in self._prompts:
            return name
        as_dots = name.replace("_", ".")
        if as_dots in self._tools or as_dots in self._prompts:
            return as_dots
        for builtin in (BUILTIN_PING_TOOL, BUILTIN_RESTART_TOOL):
            if name == builtin.replace(".", "_", 1):
                return builtin
        for enrolled in (*self._tools, *self._prompts):
            if enrolled.replace(".", "_") == name or enrolled.replace(".", "_", 1) == name:
                return enrolled
        return name

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
        resolved = self.resolve_call_name(mcp_name)
        if resolved not in self._tools:
            raise ToolNotEnrolled(resolved)
        return self._tools[resolved].answer(call)

    def answer_prompt(self, mcp_name: str, call: ToolCall) -> object:
        """Answer call with the instructions published as mcp_name, expanded for it."""
        resolved = self.resolve_call_name(mcp_name)
        if resolved not in self._prompts:
            raise ToolNotEnrolled(resolved)
        return self._prompts[resolved].answer(call)


class _ProjectNamedOnly:
    """The ``/mcp`` endpoint for requests that name their project. Claude Code runs a chat's header helper again only
    when the server answers 401, so a chat that connected while the helper could not run, such as during a restart or
    an install, names its project on the next try instead of failing every call."""

    def __init__(self, app: Any) -> None:
        self._app = app
        self._header = PROJECT_HEADER.lower().encode("latin-1")
        self._refusal = {"error": f"name the chat's project in the {PROJECT_HEADER} header"}

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        from starlette.responses import JSONResponse

        if scope["type"] == "http" and not any(name == self._header and value for name, value in scope["headers"]):
            await JSONResponse(self._refusal, status_code=401)(scope, receive, send)
            return
        await self._app(scope, receive, send)


class ProjectNotNamed(Exception):
    """A tool call arrived without the ``X-CDD-Project`` header, so the server cannot tell which project it is for."""

    def __init__(self, tool: str) -> None:
        super().__init__(
            f"{tool} was called without naming a project: this chat's cdd entry sends no X-CDD-Project header. "
            "Run python scripts/install.py from a CDD checkout to write the entry again."
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
        listed = [types.Tool(name=tool.mcp_name, description=tool.description or None, inputSchema=tool.input_schema) for tool in enrolled]
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
        name, answered by this host."""
        resolved = self._checkout_server.resolve_call_name(name)
        return ToolCall.sent(arguments, self._requested_project(resolved), tool=resolved, mcp_host=self)

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
        """The project the calling chat works on, from its ``X-CDD-Project`` header. Only ``cdd.ping`` and
        ``cdd.restart`` work without one; anything else would act on whichever folder the server started in."""
        try:
            request = self._protocol.request_context.request
        except LookupError:
            request = None
        named = request.headers.get(PROJECT_HEADER) if request is not None else None
        if tool in (BUILTIN_PING_TOOL, BUILTIN_RESTART_TOOL):
            return Path(named) if named else None
        if named and Path(named).resolve() == self._claude_settings:
            raise ProjectIsClaudeSettings(tool, Path(named))
        if named:
            return Path(named)
        raise ProjectNotNamed(tool)

    def _answer_reporting(self, call: ToolCall, reporter: Callable[[str], None] | None) -> object:
        """Answer a chat's call on its worker thread: its progress goes to reporter, and the work it does knows it
        answers a chat (``answering_a_chat``), so work that would hold the interpreter runs in a worker process."""
        # Read them from their modules as they are now: a restart imports them again, and tools read the new ones.
        from harness.agent_tools.progress import reporting_to
        from harness.mcp.tool_calls import answering_a_chat

        with reporting_to(reporter), answering_a_chat():
            return self.answer(call)

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
