"""MCP mark, install, and runtime — one destination packager."""
from __future__ import annotations

import atexit
import inspect
import json
import logging
import os
import re
import sys
import threading
import time
import types as py_types
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Union, get_args, get_origin, get_type_hints

import anyio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from harness.agent_tools.agent_tools import AgentToolSet, InstallDestination
from installation.destination import Destination, Installation

logger = logging.getLogger(__name__)
BUILTIN_PING_TOOL = "cdd.ping"
HOST_PID_NAME = "mcp-host.pid"
NUDGE_NAME = "mcp-host-nudge"
NUDGE_MIN_SECONDS = 5.0
_UNION_ORIGINS = {Union, py_types.UnionType}
_ARRAY_ORIGINS = {list, tuple, Sequence}
_OBJECT_ORIGINS = {dict, Mapping}


class Mcp(Destination):
    flag = "_mcp"

    def __new__(cls, fn: Any = None):
        inst = object.__new__(cls)
        inst.name = None
        if callable(fn):
            return inst.annotate(fn)
        return inst


mcp = Mcp


class HostPid:
    """The MCP host pid file under an IDE path."""

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

    def __init__(self, pid_file: Path | str) -> None:
        self._path = Path(pid_file)

    @classmethod
    def from_ide(cls, ide_path: Path | str) -> HostPid:
        return cls(Path(ide_path) / HOST_PID_NAME)

    def is_running(self) -> bool:
        pid = self._read_pid()
        if pid is None:
            return False
        return self._process_is_running(pid)

    def claim(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(str(os.getpid()), encoding="utf-8")
        atexit.register(self._release_this_pid)

    def release(self, pid: int | None = None) -> None:
        expected = str(pid if pid is not None else os.getpid())
        try:
            if self._path.is_file() and self._path.read_text(encoding="utf-8").strip() == expected:
                self._path.unlink()
        except OSError:
            return

    def _release_this_pid(self) -> None:
        self.release(os.getpid())

    def _read_pid(self) -> int | None:
        if not self._path.is_file():
            return None
        try:
            pid = int(self._path.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            return None
        if pid <= 0:
            return None
        return pid

    def _process_is_running(self, pid: int) -> bool:
        if os.name == "nt":
            return self._windows_process_is_running(pid)
        return self._posix_process_is_running(pid)

    def _windows_process_is_running(self, pid: int) -> bool:
        import ctypes

        handle = ctypes.windll.kernel32.OpenProcess(
            self.PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if not handle:
            return False
        ctypes.windll.kernel32.CloseHandle(handle)
        return True

    def _posix_process_is_running(self, pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except PermissionError:
            return True
        except OSError:
            return False
        return True


class CursorMcpJson:
    """User- and project-level Cursor mcp.json entries for the CDD stdio host."""

    def user_cursor_mcp_json(self) -> Path:
        return Path.home() / ".cursor" / "mcp.json"

    def cdd_stdio_names(self, servers: Mapping[str, Any]) -> list[str]:
        names: list[str] = []
        for name, spec in servers.items():
            if not isinstance(spec, dict):
                continue
            blob = " ".join(str(item) for item in spec.get("args") or [])
            if "start_host.py" not in blob and "harness.mcp" not in blob:
                continue
            if name == "cdd" or str(name).startswith("cdd"):
                names.append(str(name))
        return names

    def server_identity(self, spec: Mapping[str, Any]) -> tuple:
        env = spec.get("env") if isinstance(spec.get("env"), dict) else {}
        return (
            spec.get("command"),
            tuple(str(item) for item in spec.get("args") or []),
            spec.get("cwd"),
            tuple(sorted((key, env[key]) for key in env if key != "CDD_HOST_NUDGE")),
        )

    def start_host_script(self, spec: Mapping[str, Any]) -> Path | None:
        for item in spec.get("args") or []:
            text = str(item)
            if text.endswith("start_host.py"):
                return Path(text)
        return None

    def host_repo(self, spec: Mapping[str, Any]) -> str:
        env = spec.get("env") if isinstance(spec.get("env"), dict) else {}
        fallback = str(env.get("CDD_REPO") or spec.get("cwd") or "")
        script = self.start_host_script(spec)
        if script is None:
            return fallback
        try:
            return str(script.resolve().parents[3])
        except (IndexError, OSError) as error:
            logger.debug("start_host script %s has no checkout parents: %s", script, error)
            return fallback

    def touch_mcp_manifest(self, path: Path, *, bump_env: bool = False) -> None:
        if not path.is_file():
            return
        text = path.read_text(encoding="utf-8")
        if "start_host.py" not in text and "harness.mcp" not in text:
            return
        if not bump_env:
            path.write_text(text, encoding="utf-8")
            return
        self._rewrite_nudge(path, text)

    def _rewrite_nudge(self, path: Path, text: str) -> None:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            path.write_text(text, encoding="utf-8")
            return
        servers = data.get("mcpServers") or {}
        if not self._nudge_cdd_servers(servers):
            path.write_text(text, encoding="utf-8")
            return
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def _nudge_cdd_servers(self, servers: Mapping[str, Any]) -> bool:
        changed = False
        for spec in servers.values():
            if self._nudge_spec(spec):
                changed = True
        return changed

    def _nudge_spec(self, spec: object) -> bool:
        if not isinstance(spec, dict):
            return False
        blob = " ".join(str(item) for item in spec.get("args") or [])
        if "start_host.py" not in blob and "harness.mcp" not in blob:
            return False
        env = spec.setdefault("env", {})
        if not isinstance(env, dict):
            return False
        env["CDD_HOST_NUDGE"] = str(time.time())
        return True

    def sync_user_cursor_server(self, server: Mapping[str, Any], *, canonical: bool = False) -> bool:
        """Point user-level Cursor mcp.json at this checkout. Returns True if rewritten.

        A temp-path install must not replace a same-repo host (that is how SampleMcpOps
        wiped the real tool list). Same-repo toolset updates require the repo ``.cursor``.
        """
        data = self._mcp_document(self.user_cursor_mcp_json())
        if data is None:
            return False
        servers = data["mcpServers"]
        if not self.cdd_stdio_names(servers):
            return False
        if not canonical and self._same_repo_scripts_exist(servers, server):
            return False
        if self._user_host_matches(servers, server):
            return False
        self._rewrite_user_cdd_server(data, server)
        return True

    def _mcp_document(self, path: Path) -> dict[str, Any] | None:
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(data.get("mcpServers"), dict):
            return None
        return data

    def _same_repo_scripts_exist(self, servers: Mapping[str, Any], server: Mapping[str, Any]) -> bool:
        this_repo = self.host_repo(server)
        stale = self.cdd_stdio_names(servers)
        if not any(self.host_repo(servers[name]) == this_repo for name in stale):
            return False
        scripts = [self.start_host_script(servers[name]) for name in stale]
        return bool(scripts) and all(script is not None and script.is_file() for script in scripts)

    def _user_host_matches(self, servers: Mapping[str, Any], server: Mapping[str, Any]) -> bool:
        identity = self.server_identity(server)
        return all(
            self.server_identity(servers[name]) == identity
            for name in self.cdd_stdio_names(servers)
        )

    def _rewrite_user_cdd_server(self, data: dict[str, Any], server: Mapping[str, Any]) -> None:
        servers = data["mcpServers"]
        for name in self.cdd_stdio_names(servers):
            servers.pop(name, None)
        spec = dict(server)
        env = dict(spec.get("env") or {})
        env["CDD_HOST_NUDGE"] = str(time.time())
        spec["env"] = env
        servers["cdd"] = spec
        data["mcpServers"] = servers
        self.user_cursor_mcp_json().write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


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


@dataclass
class McpOperationDefinition:
    mcp_name: str
    kind: str
    tool: Any
    operation: str
    member: Any
    description: str = ""

    @classmethod
    def from_tool(cls, tool: Any) -> McpOperationDefinition:
        kind = "tool" if tool.kind == "tool" else "prompt"
        toolset = tool.toolset
        if getattr(toolset, "practice_guidance", None) is not None:
            mcp_name = tool.slug
        else:
            mcp_name = f"{tool.slug}.{tool.name}"
        return cls(
            mcp_name=mcp_name,
            kind=kind,
            tool=toolset,
            operation=tool.name,
            member=tool.callable,
            description=tool.description,
        )

    def invoke_line(self) -> str:
        try:
            signature = inspect.signature(self.member)
            params = inspect.Signature(
                [p for n, p in signature.parameters.items() if n != "self"]
            )
            suffix = str(params)
        except (TypeError, ValueError):
            suffix = "()"
        return f"Use MCP tool: `{self.mcp_name}{suffix}`"


class McpInstallation(Installation):
    """Record ``@Mcp`` ops, write ``mcp.json``, enroll at server start."""

    channel = "mcp"

    def __init__(self, ide: str, path: Path | str, toolset_ref: str = "", repo: Path | str | None = None) -> None:
        super().__init__(ide, path, toolset_ref, repo=repo)
        self.mcp_operations: list[McpOperationDefinition] = []
        self._bound = False
        self.host: McpHost | None = None
        self.diagnosis: dict[str, Any] | None = None

    def write(self, tool: Any) -> None:
        if not tool.install_to_mcp:
            return
        self.record_operation(tool)
        self.write_mcp_manifest()

    def record_operation(self, tool: Any) -> None:
        if not tool.install_to_mcp:
            return
        self.mcp_operations.append(McpOperationDefinition.from_tool(tool))

    def write_mcp_manifest(self) -> None:
        if not self.mcp_operations:
            return
        from installation.installer import Installer

        repo = self.repo or Path(__file__).resolve().parents[2]
        host = repo / "harness" / "mcp" / "scripts" / "start_host.py"
        payload = {
            "mcpServers": {
                "cdd": {
                    "type": "stdio",
                    "command": sys.executable,
                    "args": ["-u", str(host)],
                    "env": {
                        "PYTHONPATH": Installer(repo=repo).pythonpath(),
                        "PYTHONIOENCODING": "utf-8",
                    },
                }
            }
        }
        dest = self.path / "mcp.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(payload, indent=2) + "\n"
        if dest.is_file() and dest.read_text(encoding="utf-8") == text:
            self.track_write(dest)
            return
        dest.write_text(text, encoding="utf-8")
        self.track_write(dest)

    def bind(self, server: Any) -> None:
        self._bound = True
        for op in self.mcp_operations:
            server.enroll(op)

    def standup(self) -> McpHost:
        self.host = McpHost.standup(self.path / "mcp.json", repo=self.repo)
        return self.host

    def diagnose(self) -> dict[str, Any]:
        host = self.host if self.host is not None else self.standup()
        self.diagnosis = host.diagnose()
        return self.diagnosis

    def cursor_host_is_running(self) -> bool:
        return HostPid.from_ide(self.path).is_running()

    def ensure_cursor_host(self) -> str:
        manifest = self.path / "mcp.json"
        spec = McpHost.from_refs((), repo=str(self.repo), project=str(self.repo)).server_entry_from_manifest(
            manifest
        )
        repo_cursor = (Path(self.repo) / ".cursor").resolve() if self.repo is not None else None
        canonical = repo_cursor is not None and Path(self.path).resolve() == repo_cursor
        cursor = CursorMcpJson()
        if spec and cursor.sync_user_cursor_server(spec, canonical=canonical):
            cursor.touch_mcp_manifest(manifest)
            return "nudged"
        if self.cursor_host_is_running():
            return "running"
        if not manifest.is_file():
            return "missing"
        cursor.touch_mcp_manifest(cursor.user_cursor_mcp_json(), bump_env=True)
        nudge_file = self.path / NUDGE_NAME
        now = time.time()
        try:
            last = float(nudge_file.read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            last = 0.0
        if now - last < NUDGE_MIN_SECONDS:
            return "waiting"
        cursor.touch_mcp_manifest(manifest)
        nudge_file.write_text(str(now), encoding="utf-8")
        return "nudged"


def _prompt_message(op: McpOperationDefinition) -> str:
    if op.operation == "instructions":
        overview = getattr(op.tool, "overview", None)
        if isinstance(overview, str) and overview.strip():
            return overview.strip()
    function = getattr(op.member, "__func__", op.member)
    return (inspect.getdoc(function) or "").strip()


class McpTool:
    """One MCP tool enrolled from a deploy-recorded ``McpOperationDefinition``."""

    def __init__(self, op: McpOperationDefinition) -> None:
        self.mcp_name = op.mcp_name
        self._op = op
        self.callable = op.member
        self.description = op.description or _prompt_message(op)

    def invoke(self, arguments: dict[str, object] | None = None) -> object:
        if callable(self.callable):
            return self.callable(**dict(arguments or {}))
        return self.callable


class McpPrompt:
    """One MCP prompt enrolled from a deploy-recorded ``McpOperationDefinition``."""

    def __init__(self, op: McpOperationDefinition) -> None:
        self.mcp_name = op.mcp_name
        self._op = op
        self.callable = op.member
        self.prompt_text = op.description or _prompt_message(op)

    def invoke(self, arguments: dict[str, object] | None = None) -> object:
        tool = self._op.tool
        name = self._op.operation
        if name == "instructions" and hasattr(tool, "instructions"):
            return tool.instructions
        member = self.callable
        if callable(member):
            try:
                result = member(**dict(arguments or {}))
            except TypeError:
                result = None
            if result is not None:
                return result
            return self.prompt_text or getattr(tool, "instructions", "")
        if hasattr(tool, "instructions"):
            return tool.instructions
        return member


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
        self._tools: dict[str, McpTool] = {}
        self._prompts: dict[str, McpPrompt] = {}
        self.exceptions: list[McpIllegitimateTool] = []
        self._started = False
        self._session = None

    def _apply_catalog_import_path(self) -> None:
        from installation.installer import Installer

        Installer(repo=self.repo).ensure_import_path()

    @property
    def session(self):
        if self._session is None:
            from harness.session import Session

            self._session = Session()
        return self._session

    @property
    def started(self) -> bool:
        return self._started

    @property
    def tools(self) -> dict[str, McpTool]:
        return self._tools

    @property
    def prompts(self) -> dict[str, McpPrompt]:
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

    def enroll(self, op: McpOperationDefinition) -> None:
        if not _is_legal_mcp_name(op.mcp_name):
            self.skip(
                op.mcp_name,
                McpIllegitimateTool(
                    op.mcp_name,
                    "illegal MCP tool name",
                ),
            )
            return
        if op.kind == "tool":
            self._tools[op.mcp_name] = McpTool(op)
        else:
            self._prompts[op.mcp_name] = McpPrompt(op)

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

    def _enroll_toolset(self, toolset: Any) -> None:
        if getattr(toolset, "practice_guidance", "missing") is None:
            return
        installation = McpInstallation("Cursor", ".", toolset.registration_name)
        for tool in toolset.tools_for(InstallDestination.MCP):
            installation.record_operation(tool)
        installation.bind(self)
        self.mcp_installations.append(installation)

    def resolve_call_name(self, name: str) -> str:
        """Map Cursor's underscore tool id (`slug_op`) back to the enrolled `slug.op`."""
        if name in self._tools or name in self._prompts:
            return name
        if name == BUILTIN_PING_TOOL.replace(".", "_", 1):
            return BUILTIN_PING_TOOL
        for enrolled in (*self._tools, *self._prompts):
            if enrolled.replace(".", "_", 1) == name:
                return enrolled
        return name

    def invoke_tool(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        return self._tools[self.resolve_call_name(mcp_name)].invoke(arguments)

    def invoke_prompt(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        return self._prompts[self.resolve_call_name(mcp_name)].invoke(arguments)


class McpHost:
    """stdio MCP process — one CDD runtime, many protocol requests."""

    def __init__(self, runtime: McpServer) -> None:
        self._runtime = runtime
        self._server = Server("cdd")
        self.codeql_server = None
        self._codeql_closed = False
        self._codeql_lock = threading.Lock()
        self._register_handlers()

    def input_schema_for_callable(self, callable: Callable[..., object]) -> dict[str, Any]:
        hints = self._callable_hints(callable)
        properties: dict[str, Any] = {}
        required: list[str] = []
        for name, param in inspect.signature(callable).parameters.items():
            if not self._is_schema_parameter(name, param):
                continue
            properties[name] = self._parameter_schema(hints, name, param)
            if param.default is inspect.Parameter.empty:
                required.append(name)
        result: dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            result["required"] = required
        return result

    def _callable_hints(self, callable: Callable[..., object]) -> dict[str, Any]:
        function = getattr(callable, "__func__", callable)
        try:
            return get_type_hints(function)
        except (NameError, TypeError, AttributeError):
            return {}

    def _is_schema_parameter(self, name: str, param: inspect.Parameter) -> bool:
        if name == "self":
            return False
        return param.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )

    def _parameter_schema(
        self, hints: dict[str, Any], name: str, param: inspect.Parameter
    ) -> dict[str, Any]:
        annotation = hints.get(name, param.annotation)
        if annotation is inspect.Parameter.empty:
            return {"type": "string"}
        return self._annotation_schema(annotation)

    def _annotation_schema(self, annotation: object) -> dict[str, Any]:
        origin = get_origin(annotation)
        if origin in _UNION_ORIGINS:
            return self._union_schema(annotation)
        if annotation is list or origin in _ARRAY_ORIGINS:
            return self._array_schema(annotation)
        if annotation is dict or origin in _OBJECT_ORIGINS:
            return self._object_schema(annotation)
        return self._scalar_schema(annotation)

    def _union_schema(self, annotation: object) -> dict[str, Any]:
        variants = [self._annotation_schema(arg) for arg in get_args(annotation)]
        if len(variants) == 1:
            return variants[0]
        return {"anyOf": variants}

    def _array_schema(self, annotation: object) -> dict[str, Any]:
        args = get_args(annotation)
        item_schema = self._annotation_schema(args[0]) if args else {"type": "string"}
        return {"type": "array", "items": item_schema}

    def _object_schema(self, annotation: object) -> dict[str, Any]:
        args = get_args(annotation)
        schema: dict[str, Any] = {"type": "object"}
        if len(args) >= 2:
            schema["additionalProperties"] = self._annotation_schema(args[1])
        return schema

    def _scalar_schema(self, annotation: object) -> dict[str, Any]:
        if inspect.isclass(annotation) and annotation not in (
            str,
            int,
            float,
            bool,
            type(None),
            Path,
            bytes,
        ):
            return {"type": "object"}
        if annotation is str:
            return {"type": "string"}
        if annotation is int:
            return {"type": "integer"}
        if annotation is float:
            return {"type": "number"}
        if annotation is bool:
            return {"type": "boolean"}
        if annotation is type(None):
            return {"type": "null"}
        return {"type": "string"}

    def _register_handlers(self) -> None:
        @self._server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            tools = [
                types.Tool(
                    name=BUILTIN_PING_TOOL,
                    description="Health check for the CDD MCP host process.",
                    inputSchema={"type": "object", "properties": {}},
                )
            ]
            tools.extend(
                listed
                for listed in (
                    self._listed_tool(tool) for tool in self._runtime._tools.values()
                )
                if listed is not None
            )
            tools.extend(
                listed
                for listed in (
                    self._listed_prompt_tool(prompt)
                    for prompt in self._runtime._prompts.values()
                )
                if listed is not None
            )
            return tools

        @self._server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, object] | None
        ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            try:
                name = self._runtime.resolve_call_name(name)
                if name == BUILTIN_PING_TOOL:
                    return self._content_blocks("pong")
                if name in self._runtime._prompts:
                    return self._content_blocks(
                        self._runtime.invoke_prompt(name, dict(arguments or {}))
                    )
                return self._content_blocks(
                    self._runtime.invoke_tool(name, dict(arguments or {}))
                )
            except Exception as error:
                logger.exception("MCP tool %s failed", name)
                return self._content_blocks(f"{type(error).__name__}: {error}")

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
                description=prompt.prompt_text or None,
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=prompt.prompt_text or "",
                        ),
                    )
                ],
            )

    def _mcp_tool(self, tool: McpTool) -> types.Tool:
        return types.Tool(
            name=tool.mcp_name,
            description=tool.description or None,
            inputSchema=self.input_schema_for_callable(tool.callable),
        )

    def _listed_tool(self, tool: McpTool) -> types.Tool | None:
        try:
            return self._mcp_tool(tool)
        except Exception as error:
            self._runtime.skip(tool.mcp_name, error)
            return None

    def _mcp_prompt_tool(self, prompt: McpPrompt) -> types.Tool:
        return types.Tool(
            name=prompt.mcp_name,
            description=prompt.prompt_text or None,
            inputSchema=self.input_schema_for_callable(prompt.callable),
        )

    def _listed_prompt_tool(self, prompt: McpPrompt) -> types.Tool | None:
        try:
            return self._mcp_prompt_tool(prompt)
        except Exception as error:
            self._runtime.skip(prompt.mcp_name, error)
            return None

    def _as_prompt(self, prompt: McpPrompt) -> types.Prompt:
        return types.Prompt(
            name=prompt.mcp_name,
            description=prompt.prompt_text or None,
        )

    def _content_blocks(self, value: object) -> list[types.TextContent]:
        text = value if isinstance(value, str) else json.dumps(value, default=str)
        return [types.TextContent(type="text", text=text)]

    async def run_stdio(self) -> None:
        init_options = InitializationOptions(
            server_name="cdd",
            server_version="0.1.0",
            capabilities=self._server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={},
            ),
        )
        async with stdio_server() as (read_stream, write_stream):
            await self._server.run(
                read_stream,
                write_stream,
                init_options,
                raise_exceptions=False,
            )

    def run(self) -> None:
        threading.Thread(
            target=self._start_codeql_server,
            name="codeql-query-server",
            daemon=True,
        ).start()
        try:
            while True:
                try:
                    anyio.run(self.run_stdio)
                    return
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception:
                    logger.exception("MCP stdio host crashed; restarting")
        finally:
            self._stop_codeql_server()

    def _start_codeql_server(self) -> None:
        from harness.knowledge_graph.model.codeql import attach_query_server
        from harness.mcp.codeql_query_daemon import QueryServerClient

        try:
            server = QueryServerClient().ensure_query_server(Path(self._runtime.repo))
        except Exception:
            logger.exception("CodeQL query server did not start; queries will use the CLI")
            return
        with self._codeql_lock:
            if self._codeql_closed:
                return
            self.codeql_server = server
            attach_query_server(server)
        logger.info("codeql query-server daemon pid=%s", getattr(server, "pid", None))

    def _stop_codeql_server(self) -> None:
        from harness.knowledge_graph.model.codeql import detach_query_server

        with self._codeql_lock:
            self._codeql_closed = True
            server = self.codeql_server
            self.codeql_server = None
        if server is None:
            return
        detach_query_server(server)

    def ping(self) -> str:
        return "pong"

    def diagnose(self) -> dict[str, Any]:
        reply = self.ping()
        if reply != "pong":
            raise McpStandupFailed("diagnose", self, "MCP host ping failed")
        tools = [
            BUILTIN_PING_TOOL,
            *sorted(self._runtime.tools),
            *sorted(self._runtime.prompts),
        ]
        exceptions = [
            {"tool": item.tool, "reason": item.reason}
            for item in self._runtime.exceptions
        ]
        server = self.codeql_server
        return {
            "ok": True,
            "ping": reply,
            "tools": tools,
            "exceptions": exceptions,
            "notice": self.notice(),
            "codeqlServer": server.pid if server is not None and server.alive else None,
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

    def _arg_after(self, args: list[str], flag: str) -> str:
        if flag not in args:
            return ""
        index = args.index(flag)
        if index + 1 >= len(args):
            return ""
        return str(args[index + 1])

    def server_key(self, repo: Path | str) -> str:
        return "cdd"

    def server_entry_from_manifest(
        self, servers: Mapping[str, Any] | Path | str
    ) -> dict[str, Any]:
        raw = self._mcp_servers(servers)
        if not isinstance(raw, Mapping):
            return {}
        preferred = raw.get("cdd")
        if isinstance(preferred, dict) and preferred:
            return preferred
        named = self._named_cdd_server(raw)
        if named:
            return named
        hosted = self._hosted_cdd_server(raw)
        if hosted:
            return hosted
        first = next(iter(raw.values()), {})
        return first if isinstance(first, dict) else {}

    def _mcp_servers(self, servers: Mapping[str, Any] | Path | str) -> object:
        if not isinstance(servers, (Path, str)):
            return servers
        path = Path(servers)
        if not path.is_file():
            return {}
        return json.loads(path.read_text(encoding="utf-8")).get("mcpServers") or {}

    def _named_cdd_server(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        for name, spec in raw.items():
            if isinstance(spec, dict) and str(name).startswith("cdd"):
                return spec
        return {}

    def _hosted_cdd_server(self, raw: Mapping[str, Any]) -> dict[str, Any]:
        for spec in raw.values():
            if not isinstance(spec, dict):
                continue
            blob = " ".join(str(item) for item in spec.get("args") or [])
            if "start_host.py" in blob or "harness.mcp" in blob:
                return spec
        return {}

    def refs_from_manifest(self, manifest: Path | str) -> tuple[str, ...]:
        args = [str(item) for item in self.server_entry_from_manifest(manifest).get("args") or []]
        raw = self._arg_after(args, "--toolsets")
        return tuple(ref.strip() for ref in raw.split(",") if ref.strip())

    @classmethod
    def standup(cls, manifest: Path | str, *, repo: Path | str | None = None) -> McpHost:
        resolved = Path(repo).resolve() if repo is not None else Path(__file__).resolve().parents[2]
        refs = cls.from_refs((), repo=str(resolved), project=str(resolved)).refs_from_manifest(
            Path(manifest)
        )
        if not refs:
            from installation.installer import Installer

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
