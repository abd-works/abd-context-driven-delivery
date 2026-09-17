"""Harness transport rendering — CLI YAML fences or MCP tool references."""
from __future__ import annotations

import importlib
import inspect
from collections.abc import Callable
from typing import Any


def mcp_slug_for_toolset(toolset_ref: str) -> str:
    ref = toolset_ref.strip()
    if ":" in ref:
        module_name, class_name = ref.rsplit(":", 1)
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            instance = cls()
            return instance.toolset_name
        except Exception:
            return module_name.rsplit(".", 1)[-1] or class_name
    return ref or "toolset"


def mcp_name_for(toolset_ref: str, member: str) -> str:
    return f"{mcp_slug_for_toolset(toolset_ref)}.{member.strip()}"


def _signature_for(toolset_ref: str, member: str) -> inspect.Signature | None:
    if ":" not in toolset_ref:
        return None
    module_name, class_name = toolset_ref.rsplit(":", 1)
    try:
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        instance = cls()
        method = getattr(instance, member)
        return inspect.signature(method)
    except Exception:
        return None


def render_mcp_tool_reference(
    toolset_ref: str,
    member: str,
    *,
    callable_obj: Callable[..., Any] | None = None,
) -> str:
    name = mcp_name_for(toolset_ref, member)
    if callable_obj is not None:
        signature = inspect.signature(callable_obj)
    else:
        signature = _signature_for(toolset_ref, member)
    suffix = str(signature) if signature is not None else ""
    return f"Use MCP tool: `{name}{suffix}`"


def render_mcp_invoke(
    toolset_ref: str,
    *,
    action: str | None = None,
    tool: str | None = None,
    fidelity: str | None = None,
) -> str:
    if tool:
        return render_mcp_tool_reference(toolset_ref, tool)
    if action:
        return render_mcp_tool_reference(toolset_ref, action)
    if fidelity:
        return render_mcp_tool_reference(toolset_ref, "generate")
    return render_mcp_tool_reference(toolset_ref, "generate")
