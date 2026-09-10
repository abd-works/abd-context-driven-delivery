# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""MCP-native CDD runtime — discover AI tools and agent guidance, register with MCP, invoke directly."""
from __future__ import annotations

import ast
import inspect
import textwrap
from collections.abc import Callable
from typing import Protocol

from primitives.instructions import set_active_tool_invoker
from tools.tool import _ToolsetLoader as _CddToolsetLoader


class AnnotatedToolset(Protocol):
    """CDD toolset instance constructed for MCP discovery."""

    @property
    def toolset_name(self) -> str:
        """Public toolset name — first segment of every MCP name on this instance."""


def _unbound(method: Callable[..., object]) -> Callable[..., object]:
    return getattr(method, "__func__", method)


def _toolset_from_bound(method: Callable[..., object]) -> AnnotatedToolset:
    instance = getattr(method, "__self__", None)
    if instance is None:
        raise TypeError("expected a bound method on a toolset instance")
    return instance


class _McpPrimitive:
    """Shared identity for MCP tools and prompts.

    MCP defines separate primitives (tools, prompts, resources) with no protocol-level
    superclass. This base holds only what our tool and prompt types share locally.
    """

    def __init__(self, bound_method: Callable[..., object]) -> None:
        instance = _toolset_from_bound(bound_method)
        self.toolset_name = instance.toolset_name
        self.method_name = bound_method.__name__
        self.callable = bound_method

    @property
    def mcp_name(self) -> str:
        return f"{self.toolset_name}.{self.method_name}"

    def register_on(self, registry: dict[str, _McpPrimitive]) -> None:
        if self.mcp_name in registry:
            raise ValueError(f"duplicate MCP name: {self.mcp_name}")
        registry[self.mcp_name] = self


class McpTool(_McpPrimitive):
    """One MCP tool — an @agent_tool on a loaded toolset instance."""

    def __init__(self, bound_method: Callable[..., object]) -> None:
        function = _unbound(bound_method)
        if not (
            getattr(function, "_is_agent_tool", False)
            or getattr(function, "_is_agent_instructions", False)
        ):
            raise TypeError(f"{function.__name__} is not an @agent_tool or @agent_instructions")
        super().__init__(bound_method)
        self.description = (inspect.getdoc(function) or "").strip()

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

    def invoke(self, arguments: dict[str, object] | None = None) -> object:
        return self.callable(**dict(arguments or {}))


class McpPrompt(_McpPrimitive):
    """One MCP prompt — an @instruction orchestration body on a loaded toolset instance."""

    def __init__(self, bound_method: Callable[..., object]) -> None:
        function = _unbound(bound_method)
        if not getattr(function, "_is_instruction_orchestration", False):
            raise TypeError(f"{function.__name__} is not an @instruction orchestration body")
        super().__init__(bound_method)
        self.prompt_text = (inspect.getdoc(function) or "").strip()
        self.referenced_tool_names = self._referenced_tool_names(function)

    def invoke(self, server: McpServer, arguments: dict[str, object] | None = None) -> object:
        def invoke_referenced_tool(
            referenced: Callable[..., object], call_args: dict[str, object]
        ) -> object:
            method_name = getattr(referenced, "__name__", "")
            return server.invoke_tool(f"{self.toolset_name}.{method_name}", call_args)

        set_active_tool_invoker(invoke_referenced_tool)
        try:
            return self.callable(**dict(arguments or {}))
        finally:
            set_active_tool_invoker(None)

    @staticmethod
    def _referenced_tool_names(function: Callable[..., object]) -> tuple[str, ...]:
        try:
            source = textwrap.dedent(inspect.getsource(function))
        except (OSError, TypeError):
            return ()
        tree = ast.parse(source)
        names: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Name) or node.func.id != "tool":
                continue
            if not node.args:
                continue
            target = node.args[0]
            if isinstance(target, ast.Attribute):
                names.append(target.attr)
        return tuple(dict.fromkeys(names))


class McpToolset:
    """MCP view of one loaded CDD toolset — discover operations and register them on a server."""

    def __init__(self, instance: AnnotatedToolset) -> None:
        self.instance = instance
        self.toolset_name = instance.toolset_name
        self.tools: dict[str, McpTool] = {}
        self.prompts: dict[str, McpPrompt] = {}
        for name, function in inspect.getmembers(
            instance.__class__, predicate=inspect.isfunction
        ):
            bound = getattr(instance, name)
            if getattr(function, "_is_agent_tool", False) or getattr(
                function, "_is_agent_instructions", False
            ):
                McpTool(bound).register_on(self.tools)
            elif getattr(function, "_is_instruction_orchestration", False):
                McpPrompt(bound).register_on(self.prompts)

    def register_on(self, server: McpServer) -> None:
        for tool in self.tools.values():
            tool.register_on(server._tools)
        for prompt in self.prompts.values():
            prompt.register_on(server._prompts)


class McpServer:
    """Persistent local MCP server — load toolsets, find tools and prompts, delegate."""

    def __init__(self, *, toolset_loader: _CddToolsetLoader | None = None) -> None:
        self._toolset_loader = toolset_loader or _CddToolsetLoader.instance()
        self._toolsets: dict[str, McpToolset] = {}
        self._tools: dict[str, McpTool] = {}
        self._prompts: dict[str, McpPrompt] = {}
        self._started = False

    @property
    def started(self) -> bool:
        return self._started

    @property
    def toolsets(self) -> dict[str, McpToolset]:
        return self._toolsets

    def start(
        self,
        toolset_refs: tuple[str, ...],
        *,
        constructor_context: dict[str, object] | None = None,
    ) -> None:
        context = dict(constructor_context or {})
        for ref in toolset_refs:
            instance = self._toolset_loader.load(ref)(**context)
            toolset = McpToolset(instance)
            toolset.register_on(self)
            self._toolsets[toolset.toolset_name] = toolset
        self._started = True

    def list_tools(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    def list_prompts(self) -> tuple[str, ...]:
        return tuple(sorted(self._prompts))

    def invoke_tool(
        self, mcp_name: str, arguments: dict[str, object] | None = None
    ) -> object:
        tool = self._tools.get(mcp_name)
        if tool is None:
            raise KeyError(mcp_name)
        return tool.invoke(arguments)

    def invoke_prompt(
        self, mcp_name: str, arguments: dict[str, object] | None = None
    ) -> object:
        prompt = self._prompts.get(mcp_name)
        if prompt is None:
            raise KeyError(mcp_name)
        return prompt.invoke(self, arguments)


__all__ = [
    "AnnotatedToolset",
    "McpPrompt",
    "McpServer",
    "McpTool",
    "McpToolset",
]
