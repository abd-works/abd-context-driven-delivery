"""MCP stdio host — wire the official MCP SDK to our CDD runtime."""
from __future__ import annotations

import inspect
import json
import logging
import types as py_types
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Union, get_args, get_origin, get_type_hints

import anyio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from mcp_server.mcp_server import McpPrompt, McpServer, McpTool

logger = logging.getLogger(__name__)

BUILTIN_PING_TOOL = "cdd.ping"
_UNION_ORIGINS = {Union, py_types.UnionType}
_ARRAY_ORIGINS = {list, tuple, Sequence}
_OBJECT_ORIGINS = {dict, Mapping}


def _json_text(value: object) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, default=str)


def _annotation_schema(annotation: object) -> dict[str, Any]:
    origin = get_origin(annotation)
    if origin in _UNION_ORIGINS:
        return _union_schema(get_args(annotation))
    if annotation is list or origin in _ARRAY_ORIGINS:
        return _array_schema(annotation)
    if annotation is dict or origin in _OBJECT_ORIGINS:
        return _object_schema(annotation)
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


def _union_schema(args: tuple[object, ...]) -> dict[str, Any]:
    variants = [_annotation_schema(arg) for arg in args]
    if len(variants) == 1:
        return variants[0]
    return {"anyOf": variants}


def _array_schema(annotation: object) -> dict[str, Any]:
    args = get_args(annotation)
    item_schema = _annotation_schema(args[0]) if args else {"type": "string"}
    return {"type": "array", "items": item_schema}


def _object_schema(annotation: object) -> dict[str, Any]:
    args = get_args(annotation)
    schema: dict[str, Any] = {"type": "object"}
    if len(args) >= 2:
        schema["additionalProperties"] = _annotation_schema(args[1])
    return schema


def _resolved_hints(callable: Callable[..., object]) -> dict[str, object]:
    function = getattr(callable, "__func__", callable)
    try:
        return get_type_hints(function)
    except (NameError, TypeError, AttributeError):
        return {}


def _input_schema_for_callable(callable: Callable[..., object]) -> dict[str, Any]:
    hints = _resolved_hints(callable)
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
            properties[name] = _annotation_schema(annotation)
        if param.default is inspect.Parameter.empty:
            required.append(name)
    result: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        result["required"] = required
    return result


def _input_schema(tool: McpTool) -> dict[str, Any]:
    return _input_schema_for_callable(tool.callable)


def _mcp_tool(tool: McpTool) -> types.Tool:
    return types.Tool(
        name=tool.mcp_name,
        description=tool.description or None,
        inputSchema=_input_schema(tool),
    )


def _mcp_prompt_tool(prompt: McpPrompt) -> types.Tool:
    return types.Tool(
        name=prompt.mcp_name,
        description=prompt.prompt_text or None,
        inputSchema=_input_schema_for_callable(prompt.callable),
    )


def _mcp_prompt(prompt: McpPrompt) -> types.Prompt:
    return types.Prompt(
        name=prompt.mcp_name,
        description=prompt.prompt_text or None,
    )


def _content_blocks(value: object) -> list[types.TextContent]:
    return [types.TextContent(type="text", text=_json_text(value))]


class McpHost:
    """stdio MCP process — one CDD runtime, many protocol requests."""

    def __init__(self, runtime: McpServer) -> None:
        self._runtime = runtime
        self._server = Server("cdd")
        self._register_handlers()

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
            tools.extend(_mcp_tool(tool) for tool in self._runtime._tools.values())
            tools.extend(
                _mcp_prompt_tool(prompt) for prompt in self._runtime._prompts.values()
            )
            return tools

        @self._server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, object] | None
        ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            if name == BUILTIN_PING_TOOL:
                return _content_blocks("pong")
            if name in self._runtime._prompts:
                return _content_blocks(
                    self._runtime.invoke_prompt(name, dict(arguments or {}))
                )
            return _content_blocks(
                self._runtime.invoke_tool(name, dict(arguments or {}))
            )

        @self._server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            return [_mcp_prompt(prompt) for prompt in self._runtime._prompts.values()]

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


def build_host(
    toolset_refs: tuple[str, ...],
    *,
    constructor_context: dict[str, object] | None = None,
) -> McpHost:
    runtime = McpServer()
    if toolset_refs:
        runtime.start(toolset_refs, constructor_context=constructor_context)
    return McpHost(runtime)
