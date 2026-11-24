"""The install that writes each IDE's MCP entry, and the cdd server's MCP side: one *ProjectToolsets* of
toolsets for each project, and the *McpHost* answering every chat with them."""
from __future__ import annotations

import asyncio
import functools
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

from harness.agent_tools.agent_tools import AgentTool, AgentToolSet, ToolsetReference, names_alike
from harness.agent_tools.chat_pointer import ChatPointer
from harness.process.claude_chat_process import ClaudeChatProcess, is_desktop_spare
from harness.agent_tools.tool_call import ToolCall, ToolRequest
from harness.installation.destination import ChannelServer, RegisteredChannel, SkippedTool, SkippedTools, StandUp
from harness.installation.data_class import SentValue, data_of
from harness.installation.ide_layout import IdeLayout
from harness.installation.install_record import InstallRecord
from harness.installation.install_target import InstallTarget
from harness.installation.installer import SERVER_CHANNELS
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.installation.repository_toolsets import RUNNING_CHECKOUT, RepositoryToolsets
from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_annotations import LongCall, Mcp  # noqa: F401 - importing the server defines Mcp, the channel install reads
from harness.mcp.claude_plugins import ClaudePlugins
from harness.mcp.mcp_address import BUILTIN_LIST_TOOLS, CHAT_HEADER, CHAT_PROCESS_HEADER, LANE_CALL_PATH, MCP_PATH, PING_PATH, PROJECT_HEADER, LaneReply
from harness.mcp.mcp_daemon import McpDaemon, ServedCheckout
from harness.mcp.server_lanes import ServerLane, ServerLanes
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

    @property
    def names_running_server(self) -> bool:
        """Whether the server the entry names, the stable lane's, answers."""
        return self._installation.daemon.is_running()

    def write(self) -> None:
        """Write the entry, or for Claude Code at user level the cdd plugin."""
        dest = self.path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if self._layout.is_claude_code and self.is_user_level:
            self._write_claude_plugin()
            return
        manifest = self._server_manifest()
        if self._has_cdd_entry(dest, manifest):
            self._installation.wrote(dest)
            return
        if self._layout.is_claude_code or self.is_user_level:
            manifest = self._merged_with_other_servers(dest, manifest)
        self._ide_config(dest).write(manifest)
        self._installation.wrote(dest)

    def _write_claude_plugin(self) -> None:
        self._allow_cdd_tools(self._layout.user_settings_folder / "settings.json")
        self.point_chats_at_served_lane()
        self._drop_cdd_entry(self._layout.user_mcp_config, "user's", remove_when_empty=False)
        for written in self._installation.daemon.home.marketplace.publish_cdd_plugin(self._claude_plugin_server()):
            self._installation.wrote(written)

    def point_chats_at_served_lane(self) -> None:
        """Point the Claude Code chats working in the project installed into at the server of its lane: the dev lane's
        through a ``cdd`` entry in the project's ``.mcp.json``, the stable lane's through the cdd plugin alone. A full
        install does this, and so does every switch of the server onto the served checkout's code, so a ticket's
        worktree pinned on the dev lane is not left talking to the stable lane."""
        if self.points_at_dev_lane:
            self._write_dev_lane_entry()
        else:
            self._drop_cdd_entry(self._project_root / ".mcp.json", "project's", remove_when_empty=True)

    @property
    def points_at_dev_lane(self) -> bool:
        """Whether the project's chats reach the dev lane: the served checkout's own chats run on the lane it is served
        on, and any other project's on the stable lane unless the install was asked for the dev lane, so an install
        into a person's project never follows the lane of the checkout that ran it."""
        served = self._installation.served
        if self._project_root.resolve() == served.checkout.resolve():
            return served.home.is_dev_lane
        return self._installation.target.dev_lane

    def _write_dev_lane_entry(self) -> None:
        """Point the chats working in this checkout at the dev lane's server. The cdd plugin names the stable lane's
        server, which runs main and so lists none of the tools the feature adds; a ``cdd`` entry in the project's
        ``.mcp.json`` outranks the plugin, so a chat started in the worktree lists and calls the feature's own tools."""
        config_path = self._project_root / ".mcp.json"
        server = {"type": "http", "url": self._installation.lanes.dev.daemon.url, "headers": {PROJECT_HEADER: str(self._project_root.resolve())}}
        manifest = self._merged_with_other_servers(config_path, {self._layout.mcp_servers_key: {"cdd": server}})
        self._ide_config(config_path).write(manifest)
        self._installation.wrote(config_path)

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


class McpChannelServer(ChannelServer):
    """The one cdd server as an install handles it: stood up in the install's process over every toolset of the served
    checkout, to check it loads, then started from ``~/.cdd``, and, for Claude Code, the cdd plugin, which declares the
    server to every chat, and the mods of the code the server runs installed from the home's marketplace. Inside the cdd
    server, as an install through MCP runs, it stands up nothing: the server already serves them."""

    def __init__(self, served: ServedCheckout, lanes: ServerLanes, claude_plugins: ClaudePlugins | None) -> None:
        """claude_plugins installs the plugins for Claude Code; none for any other IDE, which has no plugins."""
        self.served = served
        # The stable lane's server, which every chat's cdd plugin names, and the dev lane, whose feature an install
        # withdraws once that feature's worktree is gone.
        self._daemon = lanes.stable.daemon
        self._dev_lane = lanes.dev
        self._claude_plugins = claude_plugins

    @property
    def runs_this_process(self) -> bool:
        """True when this process is the cdd server, as it is when an install runs as one of its tool calls."""
        return self._daemon.this_process.is_this_process()

    def stand_up(self) -> StandUp:
        if self.runs_this_process:
            self.stood_up = StandUp([], SkippedTools("MCP", "tools"))
        else:
            host = McpHost.from_repo(self.served.checkout)
            self.stood_up = StandUp(host.diagnose()["tools"], host.checkout_toolsets.skipped)
        return self.stood_up

    def ensure_running(self) -> list[str]:
        """Start the one cdd server when none answers, installing ``~/.cdd/`` on first use; an install that finds a
        server already running leaves it, and the code it serves, alone. For Claude Code also install its plugins
        (``install_plugins``). A dev lane whose served feature's worktree is gone goes back to main first, and the
        install says so."""
        returned = self._dev_lane.return_to_main_when_feature_gone()
        lines = [f"dev lane: {returned}"] if returned else []
        lines.append(f"mcp: {self.served.ensure()}")
        return lines + self.install_plugins()

    def install_plugins(self) -> list[str]:
        """Have Claude Code load every cdd plugin from its fixed folder in the cdd home, never a cached copy, one line
        for each: the cdd plugin the stable lane publishes, whose server every chat names, and the mods of the lane the
        person approved by serving it, such as the board and the prompt queue: the dev lane's when the install serves a
        feature there, else the stable lane's. The stable lane's marketplace is never written with a feature's mods. An
        install for any IDE but Claude Code installs none."""
        if self._claude_plugins is None:
            return []
        lines = [f"cdd plugin: {self._claude_plugins.install(self._daemon.home.marketplace.cdd_plugin)}"]
        return lines + [f"{plugin.name}: {self._claude_plugins.install(plugin)}" for plugin in self.served.home.marketplace.mods]


class McpInstallation(RegisteredChannel):
    """Record ``@mcp`` operations and write each IDE's ``cdd`` entry; its server is the one cdd server
    (*McpChannelServer*). Every install also publishes the hooks that start that server (*CddServerHooks*)."""

    destination = Mcp
    toolsets = (CddServerHooks,)

    def __init__(self, target: InstallTarget, record: InstallRecord, served: ServedCheckout) -> None:
        """served is the checkout the cdd server is installed from and serves, on the lane its folder runs on: the
        stable lane for a main checkout, the dev lane for a ticket's worktree."""
        super().__init__(target, record, RepositoryToolsets(served.checkout))
        self.served = served
        # Both lanes as the served checkout's sees them. The stable lane's server is the one every chat's cdd plugin
        # names, so the plugins and the IDE entry follow it; a project pointed at the dev lane names the dev lane's.
        self.lanes = ServerLanes.from_serving(served.daemon.home, served.daemon.address)
        self.daemon = self.lanes.stable.daemon
        claude_plugins = ClaudePlugins(self.daemon.home) if target.layout.is_claude_code else None
        self.server = McpChannelServer(served, self.lanes, claude_plugins)
        # The IDE's cdd entry, written once the whole install has been recorded.
        self.cdd_entry = CddEntry(self)
        self.mcp_operations: list[AgentTool] = []

    @classmethod
    def create(cls, target: InstallTarget, record: InstallRecord, repository: RepositoryToolsets | None = None) -> McpInstallation:
        """The cdd server's installation into target, serving repository, else the running checkout, on the lane its
        folder runs on (*ServerLanes*)."""
        checkout = (repository.root if repository is not None else RUNNING_CHECKOUT).resolve()
        return cls(target, record, ServerLanes().for_project(checkout).served_checkout(checkout))

    def write(self, tool: AgentTool) -> None:
        """Record the tool; the MCP config and the plugins are written once the whole install has been recorded, rather
        than again after every tool."""
        if tool.is_published_to(Mcp):
            self.mcp_operations.append(tool)

    def write_once_recorded(self) -> None:
        """Write the IDE's cdd entry, or for Claude Code the cdd plugin, once; an install that publishes no MCP operation
        writes nothing."""
        if self.mcp_operations:
            self.cdd_entry.write()

    @property
    def published(self) -> list[str]:
        return sorted(str(tool.mcp_name) for tool in self.mcp_operations)

    def status(self) -> list[str]:
        return [f"cdd server: {'running' if self.cdd_entry.names_running_server else 'not running'}"]


class ProjectToolsets:
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
        self._toolsets: tuple[ToolsetReference, ...] = ()

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

    def start(self, toolsets: Iterable[ToolsetReference]) -> None:
        """Enroll the ``@mcp`` operations of each toolset its reference names, made for this server's project, and of
        its child toolsets. A toolset whose code or configuration is wrong is skipped and recorded, so the server still
        serves the rest."""
        self._toolsets = tuple(toolsets)
        self._tools.clear()
        self._prompts.clear()
        self.skipped.clear()
        for reference in self._toolsets:
            try:
                toolset = reference.made()
            except AgentToolSet.LOAD_FAILURES as error:
                self.skipped.skip(str(reference), error)
                continue
            self._enroll_with_children(toolset)

    def _enroll_with_children(self, toolset: AgentToolSet) -> None:
        try:
            for each in (toolset, *toolset.child_toolsets()):
                self._enroll_toolset(each)
        except AgentToolSet.LOAD_FAILURES as error:
            self.skipped.skip(str(toolset.reference), error)

    def for_project(self, project: Path) -> ProjectToolsets:
        """A server with the same toolsets working on ``project``. Toolsets keep state between calls, so each project
        gets objects of its own and one chat's work never shows up in another's."""
        server = type(self)(repo=self.repo, project=project)
        server.start(self._toolsets)
        return server

    def restarted(self) -> ProjectToolsets:
        """A new server with the same toolsets, on the code as it is now. Every module from this checkout is imported
        again, this one included, because a toolset enrolled by the old loader would keep the old classes."""
        self._forget_checkout_modules()
        fresh = importlib.import_module(__name__)
        server = fresh.ProjectToolsets(repo=self.repo, project=self.project)
        server.start([fresh.ToolsetReference.parsed(str(reference)) for reference in self._toolsets])
        return server

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
        for tool in toolset.tools_published_to(Mcp):
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

    @classmethod
    def of_repo(cls, repo: Path | str) -> ProjectToolsets:
        """The toolsets of every annotated toolset class in ``repo``, working on repo itself; a class that cannot be
        loaded is skipped and recorded. One that cannot stand up at all raises *McpStandupFailed*."""
        resolved = Path(repo).resolve()
        toolsets = RepositoryToolsets(resolved)
        try:
            server = cls(repo=resolved, project=resolved)
            server.start([ToolsetReference.of(toolset_class) for toolset_class in toolsets.classes()])
            for unloadable in toolsets.unloadable:
                server.skipped.skip(str(unloadable.reference), unloadable.cause)
            server.skipped.notify()
        except Exception as error:
            raise McpStandupFailed(resolved, error) from error
        return server

    @classmethod
    def of_refs(cls, toolset_refs: tuple[str, ...], *, repo: str | None = None, project: str | None = None) -> ProjectToolsets:
        """The toolsets the ``module:Class`` references name, as a process is started with them."""
        server = cls(repo=repo, project=project)
        if toolset_refs:
            server.start([ToolsetReference.parsed(text) for text in toolset_refs])
        server.skipped.notify()
        return server


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


class ChatRequest:
    """One request a chat sent the cdd server, made by *McpHost* for each request: its headers and the port the caller's
    end of its connection uses. It answers which Claude Code process sent it (`process`), the chat it comes from
    (`chat`), the project a tool it calls works on (`project_for`), and the *ToolRequest* a call it makes answers
    (`tool_request`). A restart imports the checkout again but keeps the host, so the host makes each request from this
    module as it is now, and the request names chats and calls with the classes the restarted tools know."""

    def __init__(self, headers: Mapping[str, str], client_port: int | None, claude_settings: Path) -> None:
        self._headers = headers
        self._client_port = client_port
        # A user-level cdd entry names Claude Code's own settings folder as its project; calls naming it are refused.
        self._claude_settings = claude_settings

    @functools.cached_property
    def process(self) -> ClaudeChatProcess | None:
        """The Claude Code process the request comes from: the one ``X-CDD-Chat-Process`` names, else, when the request
        names no project either, the one holding the request's connection. Claude Code runs the headers helper once,
        when a chat connects, and the desktop app can connect a chat from its spare folder before it records the
        chat's process, so those headers stay that way for the whole connection."""
        named = ClaudeChatProcess.from_header(self._headers.get(CHAT_PROCESS_HEADER))
        if named is not None or self._names_a_project:
            return named
        return ClaudeChatProcess.from_connection(self._client_port)

    @functools.cached_property
    def chat(self) -> ChatPointer | None:
        """The chat the request comes from, so what it keeps open is its own and never shared with every chat in the
        same folder: the session the Claude Code process ``X-CDD-Chat-Process`` names runs now, else the chat
        ``X-CDD-Chat`` names; none when the request names neither."""
        running = self.process.session_id if self.process is not None else ""
        return ChatPointer.from_request(running or self._headers.get(CHAT_HEADER) or "")

    def project_for(self, tool: str) -> Path | None:
        """The project the calling chat works on for tool: the folder its session works in now, read on every call. That
        is the folder Claude Code records for the process ``X-CDD-Chat-Process`` names, else the folder the transcript of
        the session that process runs records last, else that of the chat ``X-CDD-Chat`` names, else the
        ``X-CDD-Project`` header. A desktop spare folder counts as no folder at any step. Headers are sent once, when the
        chat connects, so the project header holds the folder the chat started in, such as the desktop app's spare
        folder, which is wrong once the chat moves. Only ``cdd.ping`` and ``cdd.restart`` work without one; anything
        else raises *ProjectNotNamed*, and a project that is Claude Code's settings folder *ProjectIsClaudeSettings*."""
        named = self._headers.get(PROJECT_HEADER)
        if tool in (BUILTIN_PING_TOOL, BUILTIN_RESTART_TOOL):
            return Path(named) if named else None
        project = self._folder_the_chat_works_in()
        if project is None:
            raise ProjectNotNamed(tool)
        if project.resolve() == self._claude_settings:
            raise ProjectIsClaudeSettings(tool, project)
        return project

    def tool_request(self, tool: str, host: McpHost) -> ToolRequest:
        """The request a call to tool answers: this request's chat, answered by host for that chat."""
        return ToolRequest(self.chat, tool, host, answers_a_chat=True)

    @property
    def _names_a_project(self) -> bool:
        """Whether ``X-CDD-Project`` names a folder to work in: a desktop spare folder only means the chat has not
        reached its folder yet."""
        named = self._headers.get(PROJECT_HEADER)
        return bool(named) and not is_desktop_spare(Path(named))

    def _folder_the_chat_works_in(self) -> Path | None:
        """The first folder the request's chat is known to work in, in the order ``project_for`` gives."""
        # A desktop spare folder is never the project: it only means the chat has not reached its folder yet.
        connected_from = Path(self._headers[PROJECT_HEADER]) if self._names_a_project else None
        process = self.process
        return (
            (process.working_folder if process is not None else None)
            or self._folder_of_chat(process.session_id if process is not None else None)
            or self._folder_of_chat(self._headers.get(CHAT_HEADER))
            or connected_from
        )

    def _folder_of_chat(self, chat_id: str | None) -> Path | None:
        chat = ChatPointer.from_claude_session(chat_id or "")
        return chat.working_folder if chat is not None else None


class _LaneCallFailed(Exception):
    """A call the other lane handed over failed; the lane hears the failure by its kind and its words, as the chat would
    have heard it here."""

    def __init__(self, failure: Exception) -> None:
        super().__init__(f"{type(failure).__name__}: {failure}")
        self.failure = failure


class McpHost:
    """The cdd server's MCP side: one *ProjectToolsets* for each project a chat works on, answering every chat. The
    toolsets of the checkout it serves from answer the tool list, which every project shares, and give each new project
    its toolsets. It speaks MCP to chats through its *ChatProtocol* and answers over HTTP through its *HttpEndpoints*. A
    host serving chats is made with the two lanes as the running server sees them and its cdd home, so it hands a call
    whose project runs on the other lane to that lane; a host made in process for a probe or spec has neither."""

    def __init__(self, checkout_toolsets: ProjectToolsets, lanes: ServerLanes | None = None, home: CddHome | None = None) -> None:
        self._checkout_toolsets = checkout_toolsets
        self._servers: dict[Path, ProjectToolsets] = {checkout_toolsets.project: checkout_toolsets}
        self._servers_lock = threading.Lock()
        self._restart_gate = _RestartGate()
        self._home = home
        self._lanes = lanes
        self._chat_protocol = ChatProtocol(self)
        self._http_endpoints = HttpEndpoints(self, self._chat_protocol)

    @property
    def checkout_toolsets(self) -> ProjectToolsets:
        """The server on the checkout this host serves from: the tools every chat lists, and what start-up skipped."""
        return self._checkout_toolsets

    @property
    def chat_protocol(self) -> ChatProtocol:
        """The MCP protocol this host speaks to chats."""
        return self._chat_protocol

    @property
    def http_endpoints(self) -> HttpEndpoints:
        """The HTTP endpoints this host answers on: MCP, the ping, and the other lane's handed-over calls."""
        return self._http_endpoints

    @property
    def projects(self) -> list[Path]:
        with self._servers_lock:
            return sorted(self._servers)

    def _server_for(self, project: Path) -> ProjectToolsets:
        """The toolsets working on ``project``, started the first time a call names it."""
        with self._servers_lock:
            server = self._servers.get(project)
            if server is None:
                server = self._checkout_toolsets.for_project(project)
                self._servers[project] = server
            return server

    def tools_listed_for(self, project: Path | None) -> list[dict[str, Any]]:
        """The tools a chat working on project is listed, as data: the other lane's when that lane answers project's
        calls, as the dev lane does a ticket's worktree while it serves a feature, so the chat can call every tool the
        feature adds; else this server's own, the built-in ping and restart first."""
        other_lane = self._other_lane_answering(self.call_sent({}, project, self.tool_request(BUILTIN_LIST_TOOLS))) if project else None
        if other_lane is not None:
            return other_lane.tools_for(project)
        enrolled = (*self._checkout_toolsets.tools.values(), *self._checkout_toolsets.prompts.values())
        listed = [_listed_tool(tool.mcp_name, tool.listed_description, tool.input_schema) for tool in enrolled]
        return [*_BUILTIN_TOOLS, *listed]

    def call_sent(self, arguments: dict[str, object] | None, project: Path | None, request: ToolRequest) -> ToolCall:
        """A call this host answers, made from ``tool_call`` as it is now. A restart imports the checkout again but keeps
        this host, so the ``ToolCall`` this module was first imported with would open the call's session from practices of
        classes the restarted tools no longer know."""
        return importlib.import_module("harness.agent_tools.tool_call").ToolCall.sent(arguments, project, request)

    def tool_request(self, tool: str) -> ToolRequest:
        """The request a call this host answers outside a chat's request answers, made from ``tool_call`` as it is now,
        for the same reason as ``call_sent``."""
        return importlib.import_module("harness.agent_tools.tool_call").ToolRequest(None, tool, self)

    def answer_for_chat(self, call: ToolCall, reporter: Callable[[str], None] | None) -> object:
        """Answer a chat's call on its worker thread, as data: reporter listens to its progress. The call says it answers
        a chat (``call.request.answers_a_chat``), so work it starts that would hold the interpreter runs in a worker
        process."""
        # Read from its module as it is now: a restart imports it again, and tools read the new one.
        from harness.agent_tools.tool_call import CALLS_BEING_ANSWERED

        call.reporter = reporter
        # The answer is read into JSON while the call is still the one being answered: properties such as a board's
        # active ticket depend on the chat that asked, and read after the call they would answer for no chat.
        with CALLS_BEING_ANSWERED.answering(call):
            value = self.answer(call)
            return value if isinstance(value, str) else data_of(value)

    def dispatch(self, name: str, arguments: dict[str, object] | None = None, project: Path | None = None) -> object:
        """Run one tool call made in process on project; one that names no project works on the folder ``CDD_PROJECT``
        names, else the current folder. A true ``ping`` argument answers without entering the tool."""
        resolved = self._checkout_toolsets.resolve_call_name(name)
        return self.answer(self.call_sent(arguments, project or self._project_named_outside_a_chat(), self.tool_request(resolved)))

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
        if self._checkout_toolsets.enrolled(tool) is None:
            raise ToolNotEnrolled(tool)
        return {"ping": PONG, "tool": tool}

    def _log_failure(self, call: ToolCall, failure: BaseException) -> None:
        session = call.session
        if session is not None:
            session.log_failure(call, failure)

    def serve(self, daemon: McpDaemon, listener: socket.socket) -> None:
        """Answer every chat over HTTP on ``listener``, which ``daemon`` claimed, until the process is stopped."""
        self._http_endpoints.serve(daemon, listener)

    def restart(self) -> dict[str, Any]:
        """Swap in a server on the code as it is now, for every chat. Connections, and this host object holding them,
        stay. Each project's toolsets start again on the new code the next time a call names it."""
        # A call running on the old classes would find their modules gone, so the restart waits for it to end.
        with self._restart_gate.restarting():
            self._checkout_toolsets = self._checkout_toolsets.restarted()
            with self._servers_lock:
                self._servers = {self._checkout_toolsets.project: self._checkout_toolsets}
        self._publish_mods()
        tools = self._checkout_toolsets.tools
        return {"is_restarted": True, "tools": len(tools) + len(self._checkout_toolsets.prompts), "exceptions": self._checkout_toolsets.skipped.as_data}

    def _publish_mods(self) -> None:
        """Publish the chat bar and the prompt queue from the code the server now runs into its own lane's marketplace,
        so a chat watching the published copy reloads it with the server's restart rather than at the next install."""
        if self._home is not None and self._home.is_installed:
            self._home.marketplace.publish_mods(self._home.source)

    def diagnose(self) -> dict[str, Any]:
        """What this host publishes: the ping's answer, every tool name, and what start-up skipped."""
        server = self._checkout_toolsets
        return {
            "ok": True,
            "ping": PONG,
            "tools": [BUILTIN_PING_TOOL, BUILTIN_RESTART_TOOL, *sorted(server.tools), *sorted(server.prompts)],
            "exceptions": server.skipped.as_data,
            "notice": server.skipped.notice,
        }

    @classmethod
    def from_repo(cls, repo: Path | str, lanes: ServerLanes | None = None, home: CddHome | None = None) -> McpHost:
        """A host over every annotated toolset in ``repo``: in this process, to check it stands up, or as the server
        serving chats, with its lanes and home."""
        return cls(ProjectToolsets.of_repo(repo), lanes, home)

    @classmethod
    def from_refs(
        cls,
        toolset_refs: tuple[str, ...],
        *,
        repo: str | None = None,
        project: str | None = None,
        lanes: ServerLanes | None = None,
        home: CddHome | None = None,
    ) -> McpHost:
        """A host over the toolsets the ``module:Class`` references name, as a process is started with them."""
        return cls(ProjectToolsets.of_refs(toolset_refs, repo=repo, project=project), lanes, home)


def _listed_tool(name: str, description: str | None, input_schema: dict[str, Any]) -> dict[str, Any]:
    """One tool as a chat's tool list shows it, as the MCP SDK's ``Tool`` reads it; a tool with no description has none."""
    listed: dict[str, Any] = {"name": name, "inputSchema": input_schema}
    if description:
        listed["description"] = description
    return listed


# The tools every host lists before its toolsets' own.
_BUILTIN_TOOLS = (
    _listed_tool(BUILTIN_PING_TOOL, "Health check for the CDD MCP host process.", {"type": "object", "properties": {}}),
    _listed_tool(
        BUILTIN_RESTART_TOOL,
        "Restart the CDD MCP host on the code as it is now: reload its Python and start its toolsets again, on the same connection.",
        {"type": "object", "properties": {}},
    ),
)


class ChatProtocol:
    """The MCP protocol a host speaks to chats: the SDK's protocol server with the host's handlers, made the first time
    the host speaks MCP, so a call dispatched in process (a probe, a script, a spec) never loads the SDK. Each request a
    chat sends is one *ChatRequest*; each call runs on a worker thread, and one still running at its time limit is
    answered as still running."""

    def __init__(self, host: McpHost) -> None:
        self._host = host
        self._protocol_server: Any = None
        self._tool_calls = _ToolCalls(host.answer_for_chat)
        # A user-level cdd entry names Claude Code's own settings folder as its project; calls naming it are refused.
        self._claude_settings = IdeLayout("Claude").user_settings_folder.resolve()

    @property
    def protocol(self) -> Any:
        """The MCP protocol server answering chats, made with its handlers the first time it is asked for."""
        if self._protocol_server is None:
            self._protocol_server = self._cdd_protocol_server("cdd")
            self._register_handlers()
        return self._protocol_server

    def content_blocks(self, answer: SentValue) -> list[types.TextContent]:
        """The answer as the chat reads it: text, or its data as JSON."""
        types = self._mcp_types()
        text = answer if isinstance(answer, str) else json.dumps(data_of(answer))
        return [types.TextContent(type="text", text=text)]

    def _request_context(self) -> Any:
        """The MCP request being answered; none outside one, which is always so before the protocol server is made."""
        if self._protocol_server is None:
            return None
        try:
            return self._protocol_server.request_context
        except LookupError:
            return None

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

        @self.protocol.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            import anyio.to_thread

            listed = await anyio.to_thread.run_sync(self._host.tools_listed_for, self._listing_project())
            return [types.Tool(**tool) for tool in listed]

        @self.protocol.call_tool()
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

        @self.protocol.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            return []

        @self.protocol.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
            prompt = self._host.checkout_toolsets.prompts.get(name)
            if prompt is None:
                raise ToolNotEnrolled(name)
            text = prompt.description or ""
            message = types.PromptMessage(role="user", content=types.TextContent(type="text", text=text))
            return types.GetPromptResult(description=prompt.description or None, messages=[message])

    def _listing_project(self) -> Path | None:
        """The project the chat listing its tools works on; none when it names none, which lists this server's own."""
        try:
            return self._chat_request().project_for(BUILTIN_LIST_TOOLS)
        except (ProjectNotNamed, ProjectIsClaudeSettings):
            return None

    async def _answer_chat(self, name: str, arguments: dict[str, object] | None) -> types.CallToolResult:
        """Answer one call a chat sent. A failure is logged and raised as *_ChatCallFailed*, which the protocol answers
        as an error result naming it, so the client shows a failed call rather than the tool's output."""
        types = self._mcp_types()
        try:
            call = self._call_from_chat(name, arguments)
            value = await self._answer_off_loop(call)
            if call.request.tool == BUILTIN_RESTART_TOOL:
                await self._announce_tool_list_changed()
            if isinstance(value, _StillRunning):
                return types.CallToolResult(content=self.content_blocks(value.message), structuredContent=value.structured)
            return types.CallToolResult(content=self.content_blocks(value))
        except Exception as failure:
            logger.exception("MCP tool %s failed", name)
            raise _ChatCallFailed(failure) from failure

    def _call_from_chat(self, name: str, arguments: dict[str, object] | None) -> ToolCall:
        """The call as the chat sent it: the tool it names, the project its header names, and the chat its arguments
        name, answered by the host for that chat."""
        resolved = self._host.checkout_toolsets.resolve_call_name(name)
        request = self._chat_request()
        return self._host.call_sent(arguments, request.project_for(resolved), request.tool_request(resolved, self._host))

    def _chat_request(self) -> ChatRequest:
        """The request being answered, made from this module as it is now, so a restarted server names chats and calls
        with the classes its tools know; one with no headers outside a request."""
        context = self._request_context()
        request = context.request if context is not None else None
        client = getattr(request, "client", None)
        headers = request.headers if request is not None else {}
        return importlib.import_module(__name__).ChatRequest(headers, client[1] if client else None, self._claude_settings)

    async def _answer_off_loop(self, call: ToolCall) -> SentValue | _StillRunning:
        """Run the call on a worker thread, because a synchronous call on the event loop holds every other chat's
        requests. A call still running at its time limit keeps running and is answered as still running, not failed.
        ``cdd.ping`` answers on the event loop itself, so it says whether the loop answers, whatever the worker threads
        are busy with."""
        if call.request.tool == BUILTIN_PING_TOOL:
            return PONG
        seconds = self._host.checkout_toolsets.call_seconds(call.request.tool)
        return await self._tool_calls.run(call, seconds, self._progress_reporter())

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


class HttpEndpoints:
    """Where a host answers over HTTP: MCP over Streamable HTTP at ``/mcp``, a ``/ping`` that says which pid and checkout
    are serving, and ``/lane-call``, where the other lane's server hands over a chat's call. Only this machine's own
    clients get in: the Host must name the port, and a browser page's Origin is refused."""

    def __init__(self, host: McpHost, chat_protocol: ChatProtocol) -> None:
        self._host = host
        self._chat_protocol = chat_protocol

    def serve(self, daemon: McpDaemon, listener: socket.socket) -> None:
        """Answer every chat on ``listener``, which ``daemon`` claimed, until the process is stopped."""
        import uvicorn

        from harness.mcp.listening_loop import _ListeningLoop

        daemon.this_process.publish(self._host.checkout_toolsets.repo)
        try:
            server = uvicorn.Server(uvicorn.Config(self.app(daemon.port), log_level="warning"))
            asyncio.run(server.serve(sockets=[listener]), loop_factory=_ListeningLoop(server).new_event_loop)
        finally:
            daemon.this_process.withdraw()

    def app(self, port: int) -> Any:
        """The web app answering on port."""
        from mcp.server.fastmcp.server import StreamableHTTPASGIApp
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
        from mcp.server.transport_security import TransportSecuritySettings
        from starlette.applications import Starlette
        from starlette.routing import Route

        security = TransportSecuritySettings(allowed_hosts=[f"127.0.0.1:{port}", f"localhost:{port}"], allowed_origins=[])
        # A chat can sit idle for hours, so its session lives until the chat closes it.
        manager = StreamableHTTPSessionManager(app=self._chat_protocol.protocol, security_settings=security, session_idle_timeout=None)

        return Starlette(
            routes=[
                Route(PING_PATH, self._answer_ping),
                Route(LANE_CALL_PATH, self._answer_lane_call, methods=["POST"]),
                Route(MCP_PATH, endpoint=StreamableHTTPASGIApp(manager)),
            ],
            lifespan=lambda _app: manager.run(),
        )

    async def _answer_lane_call(self, request: Request) -> JSONResponse:
        """Answer a tool call the other lane's server handed over, for the chat that sent it there: the answer, or the
        failure named by its kind and message, so the chat sees the same failure it would have seen here. Only a server
        on this machine may hand one over: a browser page, which names its Origin, is refused."""
        from starlette.responses import JSONResponse

        if request.headers.get("origin"):
            refused = LaneReply(failure={"kind": "LaneCallRefused", "message": "a browser page may not hand over tool calls"})
            return JSONResponse(refused.as_data, status_code=403)
        # Made from ``tool_call`` as it is now, for the same reason as ``McpHost.call_sent``.
        call = importlib.import_module("harness.agent_tools.tool_call").ToolCall.from_sent(await request.json(), self._host)
        try:
            return JSONResponse(LaneReply(await self._answer_off_loop(call)).as_data)
        except _LaneCallFailed as failed:
            return JSONResponse(LaneReply.failed(failed.failure).as_data)

    async def _answer_off_loop(self, call: ToolCall) -> object:
        """The call's answer, run on a worker thread; a failure is raised as *_LaneCallFailed*, which carries it back."""
        import anyio.to_thread

        try:
            return await anyio.to_thread.run_sync(self._host.answer_for_chat, call, None)
        except Exception as failure:
            raise _LaneCallFailed(failure) from failure

    async def _answer_ping(self, _request: Request) -> JSONResponse:
        """The ``/ping`` answer: which process and checkout serve, and the projects its chats work on."""
        from starlette.responses import JSONResponse

        host = self._host
        return JSONResponse({"ok": True, "pid": os.getpid(), "source": str(host.checkout_toolsets.repo), "projects": [str(project) for project in host.projects]})


SERVER_CHANNELS.register(McpInstallation)
