# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""MCP-native CDD runtime — discover AI tools and agent guidance, register with MCP, invoke directly."""
from __future__ import annotations

import ast
import contextvars
import importlib
import inspect
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from tools.tool import _ToolsetLoader

_MCP_CTX: contextvars.ContextVar["_McpRuntimeContext | None"] = contextvars.ContextVar(
    "mcp_runtime_context", default=None
)


@dataclass(frozen=True)
class _McpRuntimeContext:
    server: McpServer
    toolset_slug: str


@dataclass(frozen=True)
class ToolBinding:
    """A registered AI-callable operation exposed to MCP under a dotted name."""

    mcp_name: str
    toolset_slug: str
    method_name: str
    callable: Callable[..., Any]
    description: str

    def invocable_parameters(self) -> tuple[str, ...]:
        sig = inspect.signature(self.callable)
        return tuple(
            name
            for name, param in sig.parameters.items()
            if name != "self" and param.kind
            in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            )
        )


@dataclass(frozen=True)
class InstructionBinding:
    """Agent guidance registered for discovery; body executes when invoked."""

    mcp_name: str
    toolset_slug: str
    method_name: str
    prompt_text: str
    referenced_tool_names: tuple[str, ...]
    callable: Callable[..., Any]


def mcp_instruction(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a method as runnable agent guidance for MCP."""
    func._is_mcp_instruction = True  # type: ignore[attr-defined]
    return func


def tool(bound_method: Callable[..., Any], /, **arguments: Any) -> Any:
    """Invoke an AI-callable tool from within agent guidance orchestration."""
    ctx = _MCP_CTX.get()
    if ctx is None:
        raise RuntimeError("tool(...) is only valid during instruction invocation")
    method_name = getattr(bound_method, "__name__", "")
    mcp_name = ctx.server._name_formatter.format(ctx.toolset_slug, method_name)
    return ctx.server.invoke_tool(mcp_name, arguments)


class McpNameFormatter:
    """Derives stable dotted MCP names from CDD toolset identity."""

    def format(self, toolset_slug: str, method_name: str) -> str:
        return f"{toolset_slug}.{method_name}"


class McpToolCatalog:
    """Registry of AI tool bindings keyed by dotted MCP name."""

    def __init__(self) -> None:
        self._bindings: dict[str, ToolBinding] = {}

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._bindings))

    def register(self, binding: ToolBinding) -> None:
        if binding.mcp_name in self._bindings:
            raise ValueError(f"duplicate MCP tool name: {binding.mcp_name}")
        self._bindings[binding.mcp_name] = binding

    def binding_for(self, mcp_name: str) -> ToolBinding | None:
        return self._bindings.get(mcp_name)


class McpInstructionCatalog:
    """Registry of agent guidance bindings keyed by dotted MCP name."""

    def __init__(self) -> None:
        self._bindings: dict[str, InstructionBinding] = {}

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._bindings))

    def register(self, binding: InstructionBinding) -> None:
        if binding.mcp_name in self._bindings:
            raise ValueError(f"duplicate MCP instruction name: {binding.mcp_name}")
        self._bindings[binding.mcp_name] = binding

    def binding_for(self, mcp_name: str) -> InstructionBinding | None:
        return self._bindings.get(mcp_name)


class ToolsetLoader:
    """Discover toolsets, construct instances, and collect MCP bindings."""

    def __init__(self, *, name_formatter: McpNameFormatter) -> None:
        self._name_formatter = name_formatter
        self._toolset_loader = _ToolsetLoader.instance()

    def load_instances(
        self,
        toolset_refs: tuple[str, ...],
        *,
        constructor_context: dict[str, Any] | None = None,
    ) -> tuple[Any, ...]:
        context = dict(constructor_context or {})
        instances: list[Any] = []
        for ref in toolset_refs:
            toolset_cls = self._toolset_loader.load(ref)
            instances.append(toolset_cls(**context))
        return tuple(instances)

    def collect_tool_bindings(self, instance: Any) -> tuple[ToolBinding, ...]:
        slug = _toolset_slug(instance)
        bindings: list[ToolBinding] = []
        for name, member in inspect.getmembers(instance.__class__, predicate=inspect.isfunction):
            if not _is_ai_tool(member):
                continue
            bound = member.__get__(instance, instance.__class__)
            bindings.append(
                ToolBinding(
                    mcp_name=self._name_formatter.format(slug, name),
                    toolset_slug=slug,
                    method_name=name,
                    callable=bound,
                    description=(inspect.getdoc(member) or "").strip(),
                )
            )
        return tuple(bindings)

    def collect_instruction_bindings(self, instance: Any) -> tuple[InstructionBinding, ...]:
        slug = _toolset_slug(instance)
        bindings: list[InstructionBinding] = []
        for name, member in inspect.getmembers(instance.__class__, predicate=inspect.isfunction):
            if not getattr(member, "_is_mcp_instruction", False):
                continue
            bound = member.__get__(instance, instance.__class__)
            bindings.append(
                InstructionBinding(
                    mcp_name=self._name_formatter.format(slug, name),
                    toolset_slug=slug,
                    method_name=name,
                    prompt_text=(inspect.getdoc(member) or "").strip(),
                    referenced_tool_names=_referenced_tool_names(member),
                    callable=bound,
                )
            )
        return tuple(bindings)


class McpServer:
    """Persistent local MCP server for CDD tool and instruction discovery."""

    def __init__(
        self,
        *,
        tool_catalog: McpToolCatalog,
        instruction_catalog: McpInstructionCatalog,
        loader: ToolsetLoader,
        name_formatter: McpNameFormatter | None = None,
    ) -> None:
        self._tool_catalog = tool_catalog
        self._instruction_catalog = instruction_catalog
        self._loader = loader
        self._name_formatter = name_formatter or McpNameFormatter()
        self._instances: dict[str, Any] = {}
        self._started = False

    @property
    def started(self) -> bool:
        return self._started

    def start(
        self,
        toolset_refs: tuple[str, ...],
        *,
        constructor_context: dict[str, Any] | None = None,
    ) -> None:
        for instance in self._loader.load_instances(
            toolset_refs, constructor_context=constructor_context
        ):
            slug = _toolset_slug(instance)
            self._instances[slug] = instance
            for binding in self._loader.collect_tool_bindings(instance):
                self._tool_catalog.register(binding)
            for binding in self._loader.collect_instruction_bindings(instance):
                self._instruction_catalog.register(binding)
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

    def invoke_tool(self, mcp_name: str, arguments: dict[str, Any] | None = None) -> Any:
        binding = self._tool_catalog.binding_for(mcp_name)
        if binding is None:
            raise KeyError(mcp_name)
        return binding.callable(**dict(arguments or {}))

    def invoke_instruction(self, mcp_name: str, arguments: dict[str, Any] | None = None) -> Any:
        binding = self._instruction_catalog.binding_for(mcp_name)
        if binding is None:
            raise KeyError(mcp_name)
        token = _MCP_CTX.set(
            _McpRuntimeContext(server=self, toolset_slug=binding.toolset_slug)
        )
        try:
            return binding.callable(**dict(arguments or {}))
        finally:
            _MCP_CTX.reset(token)


def _is_ai_tool(member: Callable[..., Any]) -> bool:
    return bool(getattr(member, "_is_agent_tool", False))


def _toolset_slug(instance: Any) -> str:
    explicit = getattr(instance.__class__, "TOOLSET_SLUG", None)
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    module = instance.__class__.__module__.split(".")[-1]
    return module.replace("-", "_")


def _referenced_tool_names(method: Callable[..., Any]) -> tuple[str, ...]:
    try:
        source = textwrap.dedent(inspect.getsource(method))
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
