# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""MCP-native CDD runtime — discover AI tools and agent guidance, register with MCP, invoke directly."""
from __future__ import annotations

from mcp_server.runtime.authoring import (
    _mcp_instruction as mcp_instruction,
    _reset_runtime_context,
    _runtime_context_token,
    _tool as tool,
)
from mcp_server.runtime.bindings import (
    _InstructionBinding as InstructionBinding,
    _ToolBinding as ToolBinding,
)
from mcp_server.runtime.catalogs import (
    _McpInstructionCatalog as McpInstructionCatalog,
    _McpToolCatalog as McpToolCatalog,
)
from mcp_server.runtime.formatter import _McpNameFormatter as McpNameFormatter
from mcp_server.runtime.loader import _ToolsetLoader as ToolsetLoader
from mcp_server.runtime.types import _AnnotatedToolset as AnnotatedToolset


class McpServer:
    """Persistent local MCP server for CDD tool and instruction discovery."""

    def __init__(
        self,
        *,
        tool_catalog: McpToolCatalog,
        instruction_catalog: McpInstructionCatalog,
        loader: ToolsetLoader,
        name_formatter: McpNameFormatter,
    ) -> None:
        self._tool_catalog = tool_catalog
        self._instruction_catalog = instruction_catalog
        self._loader = loader
        self._name_formatter = name_formatter
        self._instances: dict[str, AnnotatedToolset] = {}
        self._started = False

    @property
    def started(self) -> bool:
        return self._started

    @property
    def name_formatter(self) -> McpNameFormatter:
        return self._name_formatter

    def start(
        self,
        toolset_refs: tuple[str, ...],
        *,
        constructor_context: dict[str, object] | None = None,
    ) -> None:
        for instance in self._loader.load_instances(
            toolset_refs, constructor_context=constructor_context
        ):
            slug = self._loader.toolset_slug(instance)
            self._instances[slug] = instance
            for binding in self._loader.collect_tool_bindings(instance):
                self._tool_catalog.register_tool(binding)
            for binding in self._loader.collect_instruction_bindings(instance):
                self._instruction_catalog.register_instruction(binding)
        self._started = True

    def list_tools(self) -> tuple[str, ...]:
        return self._tool_catalog.names

    def list_instructions(self) -> tuple[str, ...]:
        return self._instruction_catalog.names

    def instruction_for(self, mcp_name: str) -> InstructionBinding | None:
        return self._instruction_catalog.binding_for(mcp_name)

    def invocable_parameters_for(self, mcp_name: str) -> tuple[str, ...]:
        binding = self._tool_catalog.binding_for(mcp_name)
        if binding is None:
            raise KeyError(mcp_name)
        return binding.invocable_parameters()

    def invoke_tool(
        self, mcp_name: str, arguments: dict[str, object] | None = None
    ) -> object:
        binding = self._tool_catalog.binding_for(mcp_name)
        if binding is None:
            raise KeyError(mcp_name)
        return binding.callable(**dict(arguments or {}))

    def invoke_instruction(
        self, mcp_name: str, arguments: dict[str, object] | None = None
    ) -> object:
        binding = self._instruction_catalog.binding_for(mcp_name)
        if binding is None:
            raise KeyError(mcp_name)
        token = _runtime_context_token(self, binding.toolset_slug)
        try:
            return binding.callable(**dict(arguments or {}))
        finally:
            _reset_runtime_context(token)


__all__ = [
    "AnnotatedToolset",
    "InstructionBinding",
    "McpInstructionCatalog",
    "McpNameFormatter",
    "McpServer",
    "McpToolCatalog",
    "ToolBinding",
    "ToolsetLoader",
    "mcp_instruction",
    "tool",
]
