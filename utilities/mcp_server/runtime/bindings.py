"""Registration records for MCP catalogs."""
from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

_TBinding = TypeVar("_TBinding")


@dataclass(frozen=True)
class _ToolBinding:
    """A registered AI-callable operation exposed to MCP under a dotted name."""

    mcp_name: str
    toolset_slug: str
    method_name: str
    callable: Callable[..., object]
    description: str

    def invocable_parameters(self) -> tuple[str, ...]:
        sig = inspect.signature(self.callable)
        return tuple(
            name
            for name, param in sig.parameters.items()
            if name != "self"
            and param.kind
            in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            )
        )


@dataclass(frozen=True)
class _InstructionBinding:
    """Agent guidance registered for discovery; body executes when invoked."""

    mcp_name: str
    toolset_slug: str
    method_name: str
    prompt_text: str
    referenced_tool_names: tuple[str, ...]
    callable: Callable[..., object]


class _BindingCatalog(Generic[_TBinding]):
    def __init__(self) -> None:
        self._bindings: dict[str, _TBinding] = {}

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._bindings))

    def register(self, binding: _TBinding, *, mcp_name: str) -> None:
        if mcp_name in self._bindings:
            raise ValueError(f"duplicate MCP name: {mcp_name}")
        self._bindings[mcp_name] = binding

    def binding_for(self, mcp_name: str) -> _TBinding | None:
        if mcp_name in self._bindings:
            return self._bindings[mcp_name]
        return None
