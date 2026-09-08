"""Shared types for the MCP runtime."""
from __future__ import annotations

from typing import Protocol

from .formatter import _McpNameFormatter


class _AnnotatedToolset(Protocol):
    """CDD toolset instance constructed for MCP discovery."""


class _McpRuntimeHost(Protocol):
    """Minimal server surface used while an instruction orchestrates tools."""

    def invoke_tool(
        self, mcp_name: str, arguments: dict[str, object] | None = None
    ) -> object: ...

    @property
    def name_formatter(self) -> _McpNameFormatter: ...
