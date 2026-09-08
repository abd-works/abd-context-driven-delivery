"""In-memory MCP registration catalogs."""
from __future__ import annotations

from .bindings import _BindingCatalog, _InstructionBinding, _ToolBinding


class _McpToolCatalog(_BindingCatalog[_ToolBinding]):
    """Registry of AI tool bindings keyed by dotted MCP name."""

    def register_tool(self, binding: _ToolBinding) -> None:
        self.register(binding, mcp_name=binding.mcp_name)


class _McpInstructionCatalog(_BindingCatalog[_InstructionBinding]):
    """Registry of agent guidance bindings keyed by dotted MCP name."""

    def register_instruction(self, binding: _InstructionBinding) -> None:
        self.register(binding, mcp_name=binding.mcp_name)
