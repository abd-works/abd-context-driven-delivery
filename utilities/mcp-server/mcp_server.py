"""MCP-native CDD runtime — discover @tool and @instruction, register with MCP, invoke directly."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolBinding:
    """A registered @tool exposed to MCP under a dotted name."""

    mcp_name: str
    toolset_slug: str
    method_name: str
    callable: Callable[..., Any]
    description: str


@dataclass(frozen=True)
class InstructionBinding:
    """An @instruction registered for discovery; body executes when invoked."""

    mcp_name: str
    toolset_slug: str
    method_name: str
    prompt_text: str
    referenced_tool_names: tuple[str, ...]
    callable: Callable[..., Any]


class McpNameFormatter:
    """Derives stable dotted MCP names from CDD toolset identity."""

    def format(self, toolset_slug: str, method_name: str) -> str:
        """Return ``{toolset_slug}.{method_name}`` — always dot notation."""
        ...


class McpToolCatalog:
    """Registry of @tool bindings keyed by dotted MCP name."""

    def __init__(self) -> None:
        self._bindings: dict[str, ToolBinding] = {}

    @property
    def names(self) -> tuple[str, ...]:
        """Registered MCP tool names in deterministic order."""
        ...

    def register(self, binding: ToolBinding) -> None:
        """Add a tool binding; reject duplicate dotted names."""
        ...

    def binding_for(self, mcp_name: str) -> ToolBinding | None:
        """Look up a registered tool by dotted MCP name."""
        ...


class McpInstructionCatalog:
    """Registry of @instruction prompt text and declared tool references."""

    def __init__(self) -> None:
        self._bindings: dict[str, InstructionBinding] = {}

    @property
    def names(self) -> tuple[str, ...]:
        """Registered instruction prompt names in deterministic order."""
        ...

    def register(self, binding: InstructionBinding) -> None:
        """Add an instruction binding; reject duplicate dotted names."""
        ...

    def binding_for(self, mcp_name: str) -> InstructionBinding | None:
        """Look up prompt text and tool refs for an instruction."""
        ...


class ToolsetLoader:
    """Minimal discovery — find toolsets, construct instances, collect bindings."""

    def __init__(self, *, name_formatter: McpNameFormatter) -> None:
        self._name_formatter = name_formatter

    def load_instances(
        self,
        toolset_refs: tuple[str, ...],
        *,
        constructor_context: dict[str, Any] | None = None,
    ) -> tuple[Any, ...]:
        """Construct toolset instances for the given ``module:Class`` references."""
        ...

    def collect_tool_bindings(self, instance: Any) -> tuple[ToolBinding, ...]:
        """Discover @tool methods on an instance and wrap them as ToolBinding values."""
        ...

    def collect_instruction_bindings(self, instance: Any) -> tuple[InstructionBinding, ...]:
        """Discover @instruction methods; capture docstring, tool(...) refs, and bound callable."""
        ...


class McpServer:
    """Persistent local MCP server for CDD tool and instruction discovery."""

    def __init__(
        self,
        *,
        tool_catalog: McpToolCatalog,
        instruction_catalog: McpInstructionCatalog,
        loader: ToolsetLoader,
    ) -> None:
        self._tool_catalog = tool_catalog
        self._instruction_catalog = instruction_catalog
        self._loader = loader
        self._instances: dict[str, Any] = {}
        self._started = False

    @property
    def started(self) -> bool:
        """Whether the server has completed startup registration."""
        ...

    def start(
        self,
        toolset_refs: tuple[str, ...],
        *,
        constructor_context: dict[str, Any] | None = None,
    ) -> None:
        """Discover toolsets, register MCP tools and instruction prompts, retain instances."""
        ...

    def list_tools(self) -> tuple[str, ...]:
        """Return dotted MCP tool names exposed by this server."""
        ...

    def list_instructions(self) -> tuple[str, ...]:
        """Return dotted MCP instruction prompt names exposed by this server."""
        ...

    def instruction_for(self, mcp_name: str) -> InstructionBinding | None:
        """Return discovery metadata for an @instruction (prompt text and declared tools)."""
        ...

    def invoke_tool(self, mcp_name: str, arguments: dict[str, Any]) -> Any:
        """Call the bound Python callable for a registered @tool."""
        ...

    def invoke_instruction(self, mcp_name: str, arguments: dict[str, Any]) -> Any:
        """Run an @instruction body; execute tool(...) calls and return the instruction result."""
        ...
