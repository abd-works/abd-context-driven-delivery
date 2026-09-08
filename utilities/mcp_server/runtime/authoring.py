"""Instruction authoring helpers and runtime context."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .types import _McpRuntimeHost

_ACTIVE_CTX: _McpRuntimeContext | None = None


@dataclass(frozen=True)
class _McpRuntimeContext:
    server: _McpRuntimeHost
    toolset_slug: str


def _mcp_instruction(func: Callable[..., object]) -> Callable[..., object]:
    """Mark a method as runnable agent guidance for MCP."""
    func._is_mcp_instruction = True  # type: ignore[attr-defined]
    return func


def _lookup_runtime_context() -> _McpRuntimeContext | None:
    return _ACTIVE_CTX


def _require_runtime_context() -> _McpRuntimeContext:
    ctx = _lookup_runtime_context()
    if ctx is None:
        raise RuntimeError("tool(...) is only valid during instruction invocation")
    return ctx


def _invoke_registered_tool(
    ctx: _McpRuntimeContext,
    bound_method: Callable[..., object],
    arguments: dict[str, object],
) -> object:
    method_name = getattr(bound_method, "__name__", "")
    mcp_name = ctx.server.name_formatter.format(ctx.toolset_slug, method_name)
    return ctx.server.invoke_tool(mcp_name, arguments)


def _tool(bound_method: Callable[..., object], /, **arguments: object) -> object:
    """Invoke an AI-callable tool from within agent guidance orchestration."""
    ctx = _require_runtime_context()
    return _invoke_registered_tool(ctx, bound_method, dict(arguments))


def _runtime_context_token(
    server: _McpRuntimeHost, toolset_slug: str
) -> _McpRuntimeContext | None:
    global _ACTIVE_CTX
    previous = _ACTIVE_CTX
    _ACTIVE_CTX = _McpRuntimeContext(server=server, toolset_slug=toolset_slug)
    return previous


def _reset_runtime_context(previous: _McpRuntimeContext | None) -> None:
    global _ACTIVE_CTX
    _ACTIVE_CTX = previous
