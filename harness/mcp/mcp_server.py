"""MCP mark, install, and runtime — one destination packager."""
from __future__ import annotations

import importlib
import json
import logging
import os
import re
import socket
import sys
import tempfile
import threading
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import anyio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from harness.agent_tools.agent_tools import AgentTool, AgentToolSet, InstallDestination
from harness.installation.destination import Destination, Installation, data_of
from harness.mcp.restart_gate import RestartGate

logger = logging.getLogger(__name__)
BUILTIN_PING_TOOL = "cdd.ping"
# Reloads the server's Python in place, so every chat picks up changed code without a new connection.
BUILTIN_RESTART_TOOL = "cdd.restart"
# Workspace diagnostics call ``serving_mcp_host().dispatch`` for many tools; that path
# must not run on an anyio worker thread (deadlock / multi-minute stalls).
_SYNC_DISPATCH_TOOLS = frozenset(
    {
        "agent-tools-diagnostics.agent_tools_diagnostics",
        "guidance-diagnostics.guidance_diagnostics",
    }
)
_CALL_TIMEOUT_SECONDS = 10
# First graph builds walk the repo; cache hits must still finish under the default.
_LONG_CALL_TIMEOUT_SECONDS = {
    "graph.load_working_copy": 600,
    # Applying an overlay rebuilds the graph from the open folder.
    "graph.set_overlays": 600,
    # Branch and worktree commands push and pull over the network.
    "repo.switch_branch": 600,
    "repo.close_branch": 600,
    "repo.switch_worktree": 600,
    "repo.close_worktree": 600,
    "repo.push_commit": 600,
}
_SERVING_MCP_HOST: Any = None


def serving_mcp_host() -> Any:
    """The ``McpHost`` currently serving MCP requests in this process, if any."""
    return _SERVING_MCP_HOST


class Mcp(Destination):
    flag = "_mcp"


mcp = Mcp


class McpStandupFailed(Exception):
    """The MCP host could not stand up or failed diagnose."""

    def __init__(
        self,
        operation: str,
        host: Any,
        message: str,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message)
        self.operation = operation
        self.host = host
        self.cause = cause


class McpIllegitimateTool(Exception):
    """One published tool was skipped so the MCP host could finish standup."""

    def __init__(self, tool: str, reason: str, cause: BaseException | None = None) -> None:
        super().__init__(f"{tool}: {reason}")
        self.tool = tool
        self.reason = reason
        self.cause = cause


def _is_legal_mcp_name(name: str) -> bool:
    return bool(name) and re.fullmatch(r"[A-Za-z0-9_.-]+", name) is not None


class UserMcpConfig:
    """The IDE's own user-level MCP config — where CDD deploys its host for every project."""

    def __init__(self, ide: str) -> None:
        self.ide = ide

    @property
    def folder(self) -> Path | None:
        """The IDE's user settings folder; ``None`` for an IDE with no user-level MCP config."""
        if self.ide == "Cursor":
            return Path.home() / ".cursor"
        if self.ide == "Claude":
            return Path.home() / ".claude"
        if self.ide == "VS Code":
            return self._vscode_user_folder()
        return None

    @property
    def path(self) -> Path | None:
        if self.ide == "Claude":
            return Path.home() / ".claude.json"
        folder = self.folder
        return folder / "mcp.json" if folder is not None else None

    @property
    def servers_key(self) -> str:
        return "servers" if self.ide == "VS Code" else "mcpServers"

    @property
    def project_folder(self) -> str:
        """The open project as Cursor and VS Code spell it inside a user-level server entry."""
        return "${workspaceFolder}"

    def _vscode_user_folder(self) -> Path:
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA")
            base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
        return base / "Code" / "User"


# Claude Code names the cdd plugin's tools mcp__plugin_cdd_cdd__{tool}, so this one entry allows every one of them.
CLAUDE_TOOLS_PERMISSION = "mcp__plugin_cdd_cdd"


class McpInstallation(Installation):
    """Record ``@Mcp`` ops, write ``mcp.json``, enroll at server start."""

    channel = "mcp"

    def __init__(self, ide: str, path: Path | str, toolset_ref: str = "", repo: Path | str | None = None) -> None:
        super().__init__(ide, path, toolset_ref, repo=repo)
        self.mcp_operations: list[AgentTool] = []
        self._bound = False
        self.host: McpHost | None = None
        self.diagnosis: dict[str, Any] | None = None

    def write(self, tool: Any) -> None:
        if not tool.install_to_mcp:
            return
        self.record_operation(tool)
        self.write_mcp_manifest()

    def record_operation(self, tool: AgentTool) -> None:
        if not tool.install_to_mcp:
            return
        self.mcp_operations.append(tool)

    @property
    def user_config(self) -> UserMcpConfig | None:
        """The IDE's user-level MCP config; ``None`` for a temp install tree or an IDE without one."""
        config = UserMcpConfig(self.ide)
        if config.path is None or self._is_temp_path(Path(self.path)):
            return None
        return config

    def _is_temp_path(self, path: Path) -> bool:
        try:
            resolved = path.resolve()
            temp = Path(tempfile.gettempdir()).resolve()
            return resolved == temp or temp in resolved.parents
        except OSError:
            return False

    @property
    def manifest_path(self) -> Path:
        """The IDE's user-level MCP config. A temp install tree keeps ``<ide>/mcp.json``
        (Claude Code: ``.mcp.json`` at the project root) so specs never touch the user's own."""
        user = self.user_config
        if user is not None:
            return user.path
        if self.ide == "Claude":
            return self._project_root() / ".mcp.json"
        return self.path / "mcp.json"

    def write_mcp_manifest(self) -> None:
        if not self.mcp_operations:
            return
        dest = self.manifest_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if self.ide == "Claude" and self.user_config is not None:
            self.allow_cdd_tools(self.user_config.folder / "settings.json")
            self.drop_project_cdd_server()
            self.drop_user_cdd_server()
            for written in self.server_home.write_claude_plugin(self._claude_plugin_server()):
                self.track_write(written)
            return
        manifest = self._server_manifest()
        if self._has_cdd_entry(dest, manifest):
            self.track_write(dest)
            return
        if self.ide == "Claude" or self.user_config is not None:
            manifest = self._merged_with_other_servers(dest, manifest)
        dest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        self.track_write(dest)

    def allow_cdd_tools(self, settings: Path) -> None:
        """Let Claude Code call every ``cdd`` tool without a prompt. The user's settings file
        holds their own permissions too, so add the one entry and never track the file for clean."""
        try:
            data = json.loads(settings.read_text(encoding="utf-8")) if settings.is_file() else {}
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(data, dict):
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
        Code, so it goes; the project's other servers stay."""
        project_config = self._project_root() / ".mcp.json"
        try:
            data = json.loads(project_config.read_text(encoding="utf-8")) if project_config.is_file() else None
        except (OSError, json.JSONDecodeError):
            return
        servers = data.get("mcpServers") if isinstance(data, dict) else None
        if not isinstance(servers, dict) or "cdd" not in servers:
            return
        del servers["cdd"]
        if servers or len(data) > 1:
            project_config.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        else:
            project_config.unlink()

    def drop_user_cdd_server(self) -> None:
        """Claude Code runs a user-level entry's headersHelper in ``~/.claude`` for every chat, so the entry names no
        chat's project; the cdd plugin replaces it. ``~/.claude.json`` holds the app's own state too, so only ``cdd`` goes."""
        user = self.user_config
        try:
            data = json.loads(user.path.read_text(encoding="utf-8")) if user is not None and user.path.is_file() else None
        except (OSError, json.JSONDecodeError):
            return
        servers = data.get("mcpServers") if isinstance(data, dict) else None
        if not isinstance(servers, dict) or "cdd" not in servers:
            return
        del servers["cdd"]
        user.path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def _claude_plugin_server(self) -> dict[str, Any]:
        """The cdd server as the cdd plugin declares it: Claude Code fills in ``${CLAUDE_PROJECT_DIR}`` with the chat's
        folder and passes it to the connect script."""
        from harness.mcp.mcp_daemon import McpDaemon

        home = self.server_home
        return {"type": "http", "url": McpDaemon().url, "headersHelper": f'"{home.python}" "{home.connect_script}" "${{CLAUDE_PROJECT_DIR}}"'}

    def _server_manifest(self) -> dict[str, Any]:
        """The one ``cdd`` entry: the shared server's URL plus how each request names its project. A user-level entry
        serves every project, so it names the open one; a temp install tree names its own."""
        from harness.mcp.mcp_daemon import PROJECT_HEADER, McpDaemon

        server: dict[str, Any] = {"type": "http", "url": McpDaemon().url}
        user = self.user_config
        if user is None:
            server["headers"] = {PROJECT_HEADER: str(self._project_root().resolve())}
        else:
            server["headers"] = {PROJECT_HEADER: user.project_folder}
        if self.ide == "Cursor":
            del server["type"]
        key = user.servers_key if user is not None else "mcpServers"
        return {key: {"cdd": server}}

    def _has_cdd_entry(self, dest: Path, manifest: dict[str, Any]) -> bool:
        """Rewriting ``~/.claude.json`` makes Claude Code reconnect cdd in every open chat, so an entry already in
        place is left alone."""
        try:
            existing = json.loads(dest.read_text(encoding="utf-8")) if dest.is_file() else {}
        except (OSError, json.JSONDecodeError):
            return False
        key = next(iter(manifest))
        servers = existing.get(key) if isinstance(existing, dict) else None
        return isinstance(servers, dict) and servers.get("cdd") == manifest[key]["cdd"]

    def _merged_with_other_servers(self, dest: Path, manifest: dict[str, Any]) -> dict[str, Any]:
        """The MCP config is shared with other servers (and, in ``~/.claude.json``, the IDE's own
        state); replace only ``cdd``."""
        try:
            existing = json.loads(dest.read_text(encoding="utf-8")) if dest.is_file() else {}
        except (OSError, json.JSONDecodeError):
            existing = {}
        merged = dict(existing) if isinstance(existing, dict) else {}
        key = next(iter(manifest))
        servers = merged.get(key)
        merged[key] = {**(servers if isinstance(servers, dict) else {}), **manifest[key]}
        return merged

    def _project_root(self) -> Path:
        path = Path(self.path)
        return path.parent if path.name in {".cursor", ".claude"} else path

    def bind(self, server: Any) -> None:
        self._bound = True
        for tool in self.mcp_operations:
            server.enroll(tool)

    def standup(self) -> McpHost:
        self.host = McpHost.standup(repo=self.repo)
        return self.host

    def diagnose(self) -> dict[str, Any]:
        host = self.host if self.host is not None else self.standup()
        self.diagnosis = host.diagnose()
        return self.diagnosis

    @property
    def server_home(self) -> Any:
        from harness.mcp.cdd_home import CddHome

        return CddHome()

    @property
    def connect_script(self) -> Path:
        return Path(__file__).resolve().parent / "scripts" / "connect.py"

    def ensure_server(self) -> str:
        """Install ``~/.cdd/`` on first use and start the one server when none answers. An install that finds a
        server already running leaves it, and the code it serves, alone."""
        from harness.mcp.mcp_daemon import McpDaemon

        self.server_home.install(self._checkout, self.connect_script)
        return self._server_status(McpDaemon(self.server_home).ensure())

    def pin_server(self) -> str:
        """Serve this checkout's current commit from ``~/.cdd/runtime``, restarting the server onto it."""
        from harness.mcp.mcp_daemon import McpDaemon

        self.server_home.install(self._checkout, self.connect_script)
        self.server_home.pin(self._checkout)
        return self._server_status(McpDaemon(self.server_home).restart())

    def serve_from_checkout(self) -> str:
        """Serve this checkout as it is on disk, for working on CDD itself, restarting the server onto it."""
        from harness.mcp.mcp_daemon import McpDaemon

        self.server_home.install(self._checkout, self.connect_script)
        self.server_home.serve_from(self._checkout)
        return self._server_status(McpDaemon(self.server_home).restart())

    def server_is_running(self) -> bool:
        from harness.mcp.mcp_daemon import McpDaemon

        return McpDaemon(self.server_home).is_running

    @property
    def _checkout(self) -> Path:
        return Path(self.repo or Path(__file__).resolve().parents[2]).resolve()

    def _server_status(self, ping: dict[str, Any]) -> str:
        return f"running (pid {ping.get('pid')}, {self.server_home.mode} {ping.get('source')})"


class McpServer:
    """Load toolset refs and enroll only ``@Mcp`` ops from the deploy walk."""

    def __init__(
        self,
        *,
        repo: str | Path | None = None,
        project: str | Path | None = None,
    ) -> None:
        self.repo = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[2]
        self.project = Path(project).resolve() if project is not None else self.repo
        self.venv = self.repo / ".venv"
        self._apply_catalog_import_path()
        self.mcp_installations: list[McpInstallation] = []
        self._tools: dict[str, AgentTool] = {}
        self._prompts: dict[str, AgentTool] = {}
        self.exceptions: list[McpIllegitimateTool] = []
        self._started = False
        self._toolset_refs: tuple[str, ...] = ()
        self._constructor_context: dict[str, object] = {}
        from space.session import Session

        self.session = Session.current(self.project)

    def _apply_catalog_import_path(self) -> None:
        from harness.installation.installer import Installer

        Installer(repo=self.repo).ensure_import_path()

    @property
    def started(self) -> bool:
        return self._started

    @property
    def tools(self) -> dict[str, AgentTool]:
        return self._tools

    @property
    def prompts(self) -> dict[str, AgentTool]:
        return self._prompts

    def skip(self, tool: str, error: BaseException) -> None:
        skipped = (
            error
            if isinstance(error, McpIllegitimateTool)
            else McpIllegitimateTool(tool, str(error), error)
        )
        self.exceptions.append(skipped)
        logger.error(
            "MCP standup exception: skipped %s: %s",
            skipped.tool,
            skipped.reason,
            exc_info=skipped.cause,
        )

    def enroll(self, tool: AgentTool) -> None:
        """Publish tool under its MCP name: an operation as a tool, instructions as a prompt whose call answers with
        them expanded."""
        name = tool.mcp_name
        if not _is_legal_mcp_name(name):
            self.skip(name, McpIllegitimateTool(name, "illegal MCP tool name"))
            return
        if name in self._tools or name in self._prompts:
            self.skip(name, McpIllegitimateTool(name, "MCP name is already enrolled"))
            return
        if tool.kind == "tool":
            self._tools[name] = tool
        else:
            self._prompts[name] = tool

    def bind_from(self, installation: McpInstallation) -> None:
        installation.bind(self)
        if installation not in self.mcp_installations:
            self.mcp_installations.append(installation)

    def start(
        self,
        toolset_refs: tuple[str, ...],
        *,
        constructor_context: dict[str, object] | None = None,
    ) -> None:
        context = dict(constructor_context or {})
        self._toolset_refs = tuple(toolset_refs)
        self._constructor_context = context
        self.mcp_installations = []
        self._tools.clear()
        self._prompts.clear()
        self.exceptions = []
        for ref in toolset_refs:
            try:
                loaded = AgentToolSet.from_items([ref], context=context)
            except Exception as error:
                self.skip(str(ref), error)
                continue
            for toolset in loaded:
                try:
                    self._enroll_toolset(toolset)
                    for child in toolset.child_toolsets():
                        self._enroll_toolset(child)
                except Exception as error:
                    self.skip(toolset.registration_name, error)
        self._started = True

    def for_project(self, project: Path) -> McpServer:
        """A runtime with the same toolsets working on ``project``. Toolsets keep state between calls, so each project
        gets objects of its own and one chat's work never shows up in another's."""
        runtime = type(self)(repo=self.repo, project=project)
        runtime.start(self._toolset_refs, constructor_context=self._constructor_context)
        return runtime

    def restarted(self) -> McpServer:
        """A new runtime with the same toolsets, on the code as it is now. Every module from this checkout is imported
        again, this one included, because a toolset enrolled by the old loader would keep the old classes."""
        self._forget_checkout_modules()
        fresh = importlib.import_module(__name__)
        runtime = fresh.McpServer(repo=self.repo, project=self.project)
        runtime.start(self._toolset_refs, constructor_context=self._constructor_context)
        return runtime

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
        if getattr(toolset, "practice_guidance", "missing") is None:
            return
        for tool in toolset.tools_for(InstallDestination.MCP):
            self.enroll(tool)

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

    def invoke_tool(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        resolved = self.resolve_call_name(mcp_name)
        if resolved not in self._tools:
            raise KeyError(resolved)
        return self._tools[resolved].invoke(arguments)

    def invoke_prompt(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        return self._prompts[self.resolve_call_name(mcp_name)].invoke(arguments)


class _ProjectNamedOnly:
    """The ``/mcp`` endpoint for requests that name their project. Claude Code runs a chat's header helper again only
    when the server answers 401, so a chat that connected while the helper could not run, such as during a restart or
    an install, names its project on the next try instead of failing every call."""

    def __init__(self, app: Any) -> None:
        from harness.mcp.mcp_daemon import PROJECT_HEADER

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
    """The cdd server's MCP side: one set of toolsets for each project a chat works on, answering every chat."""

    def __init__(self, runtime: McpServer) -> None:
        # New projects get their toolsets from this runtime; it also answers the tool list, which every project shares.
        self._runtime = runtime
        self._runtimes: dict[Path, McpServer] = {runtime.project: runtime}
        self._runtimes_lock = threading.Lock()
        self._restart_gate = RestartGate()
        self._server = _CddProtocolServer("cdd")
        self._register_handlers()

    def runtime_for(self, project: Path) -> McpServer:
        """The toolsets working on ``project``, started the first time a call names it."""
        with self._runtimes_lock:
            runtime = self._runtimes.get(project)
            if runtime is None:
                runtime = self._runtime.for_project(project)
                self._runtimes[project] = runtime
            return runtime

    @property
    def projects(self) -> list[Path]:
        with self._runtimes_lock:
            return sorted(self._runtimes)

    def _bind_as_serving(self) -> None:
        global _SERVING_MCP_HOST
        _SERVING_MCP_HOST = self

    def _unbind_as_serving(self) -> None:
        global _SERVING_MCP_HOST
        if _SERVING_MCP_HOST is self:
            _SERVING_MCP_HOST = None

    def _register_handlers(self) -> None:
        @self._server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            tools = [
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
            enrolled = (*self._runtime._tools.values(), *self._runtime._prompts.values())
            tools.extend(listed for listed in map(self._listed_tool, enrolled) if listed is not None)
            return tools

        @self._server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, object] | None
        ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            blocks = await self._call_tool_blocks(name, arguments)
            # A worker thread runs to the end even when the client cancels it, and
            # the cancellation has already answered the request. Stop here, because
            # a second answer raises in the MCP session and takes down the host.
            await anyio.lowlevel.checkpoint()
            return blocks

        @self._server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            return []

        @self._server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: dict[str, str] | None
        ) -> types.GetPromptResult:
            prompt = self._runtime._prompts.get(name)
            if prompt is None:
                raise ValueError(f"unknown prompt: {name}")
            return types.GetPromptResult(
                description=prompt.description or None,
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=prompt.description or "",
                        ),
                    )
                ],
            )

    async def _call_tool_blocks(
        self, name: str, arguments: dict[str, object] | None
    ) -> list[types.TextContent]:
        try:
            resolved = self._runtime.resolve_call_name(name)
            project = self._requested_project(resolved)
            if resolved in _SYNC_DISPATCH_TOOLS:
                value = self._dispatch_reporting(name, arguments, None, project)
            else:
                # Dispatch off the event loop. A synchronous tool call blocks
                # stdin and stdout, and the client then waits until its timeout.
                # A call that is still running after the limit is a failed call.
                timeout = _LONG_CALL_TIMEOUT_SECONDS.get(
                    resolved, _CALL_TIMEOUT_SECONDS
                )
                reporter = self._progress_reporter()
                try:
                    with anyio.fail_after(timeout):
                        value = await anyio.to_thread.run_sync(
                            self._dispatch_reporting, name, arguments, reporter, project
                        )
                except TimeoutError:
                    return self._content_blocks(
                        f"TimeoutError: {name} exceeded {timeout} seconds"
                    )
            if resolved == BUILTIN_RESTART_TOOL:
                await self._announce_tool_list_changed()
            return self._content_blocks(value)
        except Exception as error:
            logger.exception("MCP tool %s failed", name)
            return self._content_blocks(f"{type(error).__name__}: {error}")

    async def _announce_tool_list_changed(self) -> None:
        """A restart can add or drop tools, so the client is told to list them again."""
        try:
            await self._server.request_context.session.send_tool_list_changed()
        except LookupError:
            return

    def _progress_reporter(self) -> Callable[[str], None] | None:
        """Sends a tool's progress reports as notifications for its call, when the caller asked for them with a progress
        token. The tool runs on a worker thread, so each report goes back through the event loop."""
        try:
            context = self._server.request_context
        except LookupError:
            return None
        token = context.meta.progressToken if context.meta else None
        if token is None:
            return None
        reported = iter(range(1, sys.maxsize))

        def report(message: str) -> None:
            anyio.from_thread.run(context.session.send_progress_notification, token, next(reported), None, message)

        return report

    def _requested_project(self, tool: str) -> Path | None:
        """The project the calling chat works on, from its ``X-CDD-Project`` header. Only ``cdd.ping`` and
        ``cdd.restart`` work without one; anything else would act on whichever folder the server started in."""
        from harness.mcp.mcp_daemon import PROJECT_HEADER

        try:
            request = self._server.request_context.request
        except LookupError:
            request = None
        named = request.headers.get(PROJECT_HEADER) if request is not None else None
        if tool in (BUILTIN_PING_TOOL, BUILTIN_RESTART_TOOL):
            return Path(named) if named else None
        if named and Path(named).resolve() == UserMcpConfig("Claude").folder.resolve():
            raise ProjectIsClaudeSettings(tool, Path(named))
        if named:
            return Path(named)
        raise ProjectNotNamed(tool)

    def _dispatch_reporting(
        self,
        name: str,
        arguments: dict[str, object] | None,
        reporter: Callable[[str], None] | None,
        project: Path | None,
    ) -> object:
        # Read both from the modules as they are now: a restart imports them again, and tools read the new ones.
        from harness.agent_tools.progress import reporting_to
        from space.work_state import working_on

        if project is None:
            return self.dispatch(name, arguments)
        with working_on(project), reporting_to(reporter):
            return self.dispatch(name, arguments)

    def _listed_tool(self, tool: AgentTool) -> types.Tool | None:
        """tool as the tool list shows it; one whose schema cannot be read is skipped, so the rest still list."""
        try:
            return types.Tool(name=tool.mcp_name, description=tool.description or None, inputSchema=tool.input_schema)
        except Exception as error:
            self._runtime.skip(tool.mcp_name, error)
            return None

    def dispatch(self, name: str, arguments: dict[str, object] | None = None) -> object:
        """Run one tool call on the project being worked on. A true ``ping`` argument answers without entering the
        tool."""
        resolved = self._runtime.resolve_call_name(name)
        if resolved == BUILTIN_PING_TOOL:
            return self.ping()
        if resolved == BUILTIN_RESTART_TOOL:
            return self.restart()
        return self._dispatch_on_project(resolved, arguments)

    def _dispatch_on_project(self, resolved: str, arguments: dict[str, object] | None) -> object:
        with self._restart_gate.running_call():
            return self._dispatch_between_restarts(resolved, arguments)

    def _dispatch_between_restarts(self, resolved: str, arguments: dict[str, object] | None) -> object:
        from space.session import Session
        from space.session.chat_pointer import ChatPointer
        from space.work_state import project_checkout

        project = project_checkout()
        runtime = self.runtime_for(project)
        Session.refresh_current_from_repo(project)
        chat, args = ChatPointer.taken_from(arguments)
        with ChatPointer.serving(chat):
            try:
                if args.get("ping") is True:
                    if not self._enrolled(resolved):
                        raise KeyError(resolved)
                    return {"ping": "pong", "tool": resolved}
                if resolved in runtime.prompts:
                    return runtime.invoke_prompt(resolved, args)
                return runtime.invoke_tool(resolved, args)
            except BaseException as failure:
                Session.current(project).record_failure(failure, tool=resolved)
                raise

    def _enrolled(self, name: str) -> bool:
        return (
            name in (BUILTIN_PING_TOOL, BUILTIN_RESTART_TOOL)
            or name in self._runtime._tools
            or name in self._runtime._prompts
        )

    def _content_blocks(self, value: object) -> list[types.TextContent]:
        text = value if isinstance(value, str) else json.dumps(data_of(value))
        return [types.TextContent(type="text", text=text)]

    def serve(self, daemon: Any, listener: socket.socket) -> None:
        """Answer every chat over HTTP on ``listener``, which ``daemon`` claimed, until the process is stopped."""
        import uvicorn

        self._bind_as_serving()
        daemon.publish(self._runtime.repo)
        try:
            config = uvicorn.Config(self.http_app(daemon.port), log_level="warning")
            uvicorn.Server(config).run(sockets=[listener])
        finally:
            daemon.withdraw()
            self._unbind_as_serving()

    def http_app(self, port: int) -> Any:
        """MCP over Streamable HTTP at ``/mcp`` and a ``/ping`` that says which pid and checkout are serving. Only this
        machine's own clients get in: the Host must name this port, and a browser page's Origin is refused."""
        from mcp.server.fastmcp.server import StreamableHTTPASGIApp
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
        from mcp.server.transport_security import TransportSecuritySettings
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route

        from harness.mcp.mcp_daemon import MCP_PATH, PING_PATH

        security = TransportSecuritySettings(allowed_hosts=[f"127.0.0.1:{port}", f"localhost:{port}"], allowed_origins=[])
        # A chat can sit idle for hours, so its session lives until the chat closes it.
        manager = StreamableHTTPSessionManager(app=self._server, security_settings=security, session_idle_timeout=None)

        async def ping(_request: Any) -> JSONResponse:
            return JSONResponse(
                {"ok": True, "pid": os.getpid(), "source": str(self._runtime.repo), "projects": [str(item) for item in self.projects]}
            )

        return Starlette(
            routes=[Route(PING_PATH, ping), Route(MCP_PATH, endpoint=_ProjectNamedOnly(StreamableHTTPASGIApp(manager)))],
            lifespan=lambda _app: manager.run(),
        )

    def ping(self) -> str:
        return "pong"

    def restart(self) -> dict[str, Any]:
        """Swap in a runtime on the code as it is now, for every chat. Connections, and this host object holding them,
        stay. Each project's toolsets start again on the new code the next time a call names it."""
        # A call running on the old classes would find their modules gone, so the restart waits for it to end.
        with self._restart_gate.restarting():
            self._runtime = self._runtime.restarted()
            with self._runtimes_lock:
                self._runtimes = {self._runtime.project: self._runtime}
            sys.modules[__name__]._SERVING_MCP_HOST = self
        return {
            "is_restarted": True,
            "tools": len(self._runtime.tools) + len(self._runtime.prompts),
            "exceptions": [{"tool": item.tool, "reason": item.reason} for item in self._runtime.exceptions],
        }

    def diagnose(self) -> dict[str, Any]:
        reply = self.ping()
        if reply != "pong":
            raise McpStandupFailed("diagnose", self, "MCP host ping failed")
        tools = [
            BUILTIN_PING_TOOL,
            BUILTIN_RESTART_TOOL,
            *sorted(self._runtime.tools),
            *sorted(self._runtime.prompts),
        ]
        exceptions = [
            {"tool": item.tool, "reason": item.reason}
            for item in self._runtime.exceptions
        ]
        return {
            "ok": True,
            "ping": reply,
            "tools": tools,
            "exceptions": exceptions,
            "notice": self.notice(),
        }

    def notice(self) -> str:
        if not self._runtime.exceptions:
            return ""
        lines = ["MCP standup skipped illegitimate tools and continued:"]
        for item in self._runtime.exceptions:
            lines.append(f"- {item.tool}: {item.reason}")
        return "\n".join(lines)

    def notify_exceptions(self) -> None:
        text = self.notice()
        if text:
            print(text, file=sys.stderr)

    @classmethod
    def standup(cls, *, repo: Path | str | None = None) -> McpHost:
        """A host over every annotated toolset in ``repo``, in this process, to check it stands up."""
        from harness.installation.installer import Installer

        resolved = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[2]
        refs = tuple(Installer(repo=resolved).collect_toolsets())
        try:
            return cls.from_refs(refs, repo=str(resolved), project=str(resolved))
        except Exception as error:
            raise McpStandupFailed("standup", None, str(error), error) from error

    @classmethod
    def from_refs(
        cls,
        toolset_refs: tuple[str, ...],
        *,
        constructor_context: dict[str, object] | None = None,
        repo: str | None = None,
        project: str | None = None,
    ) -> McpHost:
        runtime = McpServer(repo=repo, project=project)
        if toolset_refs:
            runtime.start(toolset_refs, constructor_context=constructor_context)
        host = cls(runtime)
        host.notify_exceptions()
        return host
