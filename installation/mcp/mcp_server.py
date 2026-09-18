"""MCP mark, install, and runtime — one destination packager."""
from __future__ import annotations

import inspect
import json
import logging
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


@dataclass
class McpOperationDefinition:
    mcp_name: str
    kind: str
    tool: Any
    operation: str
    member: Any

    @classmethod
    def from_tool(cls, tool: Any) -> McpOperationDefinition:
        kind = "tool" if tool.kind == "tool" else "prompt"
        return cls(
            mcp_name=f"{tool.slug}.{tool.name}",
            kind=kind,
            tool=tool.toolset,
            operation=tool.name,
            member=tool.callable,
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

        refs = sorted({op.tool.registration_name for op in self.mcp_operations})
        repo = self.repo or Path(__file__).resolve().parents[2]
        payload = {
            "mcpServers": {
                "cdd": {
                    "command": "python",
                    "args": [
                        "-m",
                        "installation.mcp",
                        "--toolsets",
                        ",".join(refs),
                    ],
                    "env": {"PYTHONPATH": Installer.pythonpath(repo)},
                }
            }
        }
        dest = self.path / "mcp.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def bind(self, server: Any) -> None:
        self._bound = True
        for op in self.mcp_operations:
            server.enroll(op)


class McpTool:
    """One MCP tool enrolled from a deploy-recorded ``McpOperationDefinition``."""

    def __init__(self, op: McpOperationDefinition) -> None:
        self.mcp_name = op.mcp_name
        self._op = op
        self.callable = op.member
        function = getattr(self.callable, "__func__", self.callable)
        self.description = (inspect.getdoc(function) or "").strip()

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
        function = getattr(self.callable, "__func__", self.callable)
        self.prompt_text = (inspect.getdoc(function) or "").strip()

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
        from installation.installer import Installer

        Installer.ensure_import_path(self.repo)
        self.mcp_installations: list[McpInstallation] = []
        self._tools: dict[str, McpTool] = {}
        self._prompts: dict[str, McpPrompt] = {}
        self._started = False

    @property
    def started(self) -> bool:
        return self._started

    @property
    def tools(self) -> dict[str, McpTool]:
        return self._tools

    @property
    def prompts(self) -> dict[str, McpPrompt]:
        return self._prompts

    def enroll(self, op: McpOperationDefinition) -> None:
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
        for toolset in AgentToolSet.load_toolsets(list(toolset_refs), context=context):
            installation = McpInstallation("Cursor", ".", toolset.registration_name)
            for tool in toolset.tools_for(InstallDestination.MCP):
                installation.record_operation(tool)
            installation.bind(self)
            self.mcp_installations.append(installation)
        self._started = True

    def invoke_tool(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        return self._tools[mcp_name].invoke(arguments)

    def invoke_prompt(self, mcp_name: str, arguments: dict[str, object] | None = None) -> object:
        return self._prompts[mcp_name].invoke(arguments)


class McpHost:
    """stdio MCP process — one CDD runtime, many protocol requests."""

    def __init__(self, runtime: McpServer) -> None:
        self._runtime = runtime
        self._server = Server("cdd")
        self._register_handlers()

    @staticmethod
    def input_schema_for_callable(callable: Callable[..., object]) -> dict[str, Any]:
        function = getattr(callable, "__func__", callable)
        try:
            hints = get_type_hints(function)
        except (NameError, TypeError, AttributeError):
            hints = {}
        properties: dict[str, Any] = {}
        required: list[str] = []
        for name, param in inspect.signature(callable).parameters.items():
            if name == "self":
                continue
            if param.kind not in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                continue
            annotation = hints.get(name, param.annotation)
            if annotation is inspect.Parameter.empty:
                properties[name] = {"type": "string"}
            else:
                properties[name] = McpHost._annotation_schema(annotation)
            if param.default is inspect.Parameter.empty:
                required.append(name)
        result: dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            result["required"] = required
        return result

    @staticmethod
    def _annotation_schema(annotation: object) -> dict[str, Any]:
        origin = get_origin(annotation)
        if origin in _UNION_ORIGINS:
            variants = [McpHost._annotation_schema(arg) for arg in get_args(annotation)]
            if len(variants) == 1:
                return variants[0]
            return {"anyOf": variants}
        if annotation is list or origin in _ARRAY_ORIGINS:
            args = get_args(annotation)
            item_schema = (
                McpHost._annotation_schema(args[0]) if args else {"type": "string"}
            )
            return {"type": "array", "items": item_schema}
        if annotation is dict or origin in _OBJECT_ORIGINS:
            args = get_args(annotation)
            schema: dict[str, Any] = {"type": "object"}
            if len(args) >= 2:
                schema["additionalProperties"] = McpHost._annotation_schema(args[1])
            return schema
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
            tools.extend(self._mcp_tool(tool) for tool in self._runtime._tools.values())
            tools.extend(
                self._mcp_prompt_tool(prompt) for prompt in self._runtime._prompts.values()
            )
            return tools

        @self._server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, object] | None
        ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            if name == BUILTIN_PING_TOOL:
                return self._content_blocks("pong")
            if name in self._runtime._prompts:
                return self._content_blocks(
                    self._runtime.invoke_prompt(name, dict(arguments or {}))
                )
            return self._content_blocks(
                self._runtime.invoke_tool(name, dict(arguments or {}))
            )

        @self._server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            return [self._as_prompt(prompt) for prompt in self._runtime._prompts.values()]

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

    def _mcp_prompt_tool(self, prompt: McpPrompt) -> types.Tool:
        return types.Tool(
            name=prompt.mcp_name,
            description=prompt.prompt_text or None,
            inputSchema=self.input_schema_for_callable(prompt.callable),
        )

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
                raise_exceptions=True,
            )

    def run(self) -> None:
        anyio.run(self.run_stdio)

    @classmethod
    def build(
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
        return cls(runtime)
