# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""MCP-native CDD runtime — discover AI tools and agent guidance, register with MCP, invoke directly."""
from __future__ import annotations

import ast
import inspect
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from tools.tool import _ToolsetLoader as _CddToolsetLoader

_TBinding = TypeVar("_TBinding")
_ACTIVE_CTX: _McpRuntimeContext | None = None


class AnnotatedToolset(Protocol):
    """CDD toolset instance constructed for MCP discovery."""


@dataclass(frozen=True)
class _McpRuntimeContext:
    server: _McpServer
    toolset_slug: str


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

    def _register(self, binding: _TBinding, *, mcp_name: str) -> None:
        if mcp_name in self._bindings:
            raise ValueError(f"duplicate MCP name: {mcp_name}")
        self._bindings[mcp_name] = binding

    def binding_for(self, mcp_name: str) -> _TBinding | None:
        if mcp_name in self._bindings:
            return self._bindings[mcp_name]
        return None


class _McpToolCatalog(_BindingCatalog[_ToolBinding]):
    """Registry of AI tool bindings keyed by dotted MCP name."""

    def register(self, binding: _ToolBinding) -> None:
        self._register(binding, mcp_name=binding.mcp_name)


class _McpInstructionCatalog(_BindingCatalog[_InstructionBinding]):
    """Registry of agent guidance bindings keyed by dotted MCP name."""

    def register(self, binding: _InstructionBinding) -> None:
        self._register(binding, mcp_name=binding.mcp_name)


class _McpNameFormatter:
    """Derives stable dotted MCP names from CDD toolset identity."""

    def format(self, toolset_slug: str, method_name: str) -> str:
        return f"{toolset_slug}.{method_name}"


def mcp_instruction(func: Callable[..., object]) -> Callable[..., object]:
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


def tool(bound_method: Callable[..., object], /, **arguments: object) -> object:
    """Invoke an AI-callable tool from within agent guidance orchestration."""
    ctx = _require_runtime_context()
    return _invoke_registered_tool(ctx, bound_method, dict(arguments))


class _ToolsetLoader:
    """Discover toolsets, construct instances, and collect MCP bindings."""

    def __init__(
        self,
        *,
        name_formatter: _McpNameFormatter,
        toolset_loader: _CddToolsetLoader | None = None,
    ) -> None:
        self._name_formatter = name_formatter
        self._toolset_loader = toolset_loader or _CddToolsetLoader.instance()

    def load_instances(
        self,
        toolset_refs: tuple[str, ...],
        *,
        constructor_context: dict[str, object] | None = None,
    ) -> tuple[AnnotatedToolset, ...]:
        context = dict(constructor_context or {})
        instances: list[AnnotatedToolset] = []
        for ref in toolset_refs:
            toolset_cls = self._toolset_loader.load(ref)
            instances.append(toolset_cls(**context))
        return tuple(instances)

    def collect_tool_bindings(self, instance: AnnotatedToolset) -> tuple[_ToolBinding, ...]:
        slug = self.toolset_slug(instance)
        bindings: list[_ToolBinding] = []
        for name, member in inspect.getmembers(instance.__class__, predicate=inspect.isfunction):
            if not self._is_ai_tool(member):
                continue
            bound = member.__get__(instance, instance.__class__)
            bindings.append(
                _ToolBinding(
                    mcp_name=self._name_formatter.format(slug, name),
                    toolset_slug=slug,
                    method_name=name,
                    callable=bound,
                    description=(inspect.getdoc(member) or "").strip(),
                )
            )
        return tuple(bindings)

    def collect_instruction_bindings(
        self, instance: AnnotatedToolset
    ) -> tuple[_InstructionBinding, ...]:
        slug = self.toolset_slug(instance)
        bindings: list[_InstructionBinding] = []
        for name, member in inspect.getmembers(instance.__class__, predicate=inspect.isfunction):
            if not getattr(member, "_is_mcp_instruction", False):
                continue
            bound = member.__get__(instance, instance.__class__)
            bindings.append(
                _InstructionBinding(
                    mcp_name=self._name_formatter.format(slug, name),
                    toolset_slug=slug,
                    method_name=name,
                    prompt_text=(inspect.getdoc(member) or "").strip(),
                    referenced_tool_names=self._referenced_tool_names(member),
                    callable=bound,
                )
            )
        return tuple(bindings)

    @staticmethod
    def toolset_slug(instance: AnnotatedToolset) -> str:
        explicit = getattr(instance.__class__, "TOOLSET_SLUG", None)
        if isinstance(explicit, str) and explicit.strip():
            return explicit.strip()
        module = instance.__class__.__module__.split(".")[-1]
        return module.replace("-", "_")

    @staticmethod
    def _is_ai_tool(member: Callable[..., object]) -> bool:
        return bool(getattr(member, "_is_agent_tool", False))

    @staticmethod
    def _referenced_tool_names(method: Callable[..., object]) -> tuple[str, ...]:
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


class _McpServer:
    """Persistent local MCP server for CDD tool and instruction discovery."""

    def __init__(
        self,
        *,
        tool_catalog: _McpToolCatalog,
        instruction_catalog: _McpInstructionCatalog,
        loader: _ToolsetLoader,
        name_formatter: _McpNameFormatter,
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
    def name_formatter(self) -> _McpNameFormatter:
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
                self._tool_catalog.register(binding)
            for binding in self._loader.collect_instruction_bindings(instance):
                self._instruction_catalog.register(binding)
        self._started = True

    def list_tools(self) -> tuple[str, ...]:
        return self._tool_catalog.names

    def list_instructions(self) -> tuple[str, ...]:
        return self._instruction_catalog.names

    def instruction_for(self, mcp_name: str) -> _InstructionBinding | None:
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
        token = self._push_runtime_context(binding.toolset_slug)
        try:
            return binding.callable(**dict(arguments or {}))
        finally:
            self._pop_runtime_context(token)

    def _push_runtime_context(self, toolset_slug: str) -> _McpRuntimeContext | None:
        global _ACTIVE_CTX
        previous = _ACTIVE_CTX
        _ACTIVE_CTX = _McpRuntimeContext(server=self, toolset_slug=toolset_slug)
        return previous

    def _pop_runtime_context(self, previous: _McpRuntimeContext | None) -> None:
        global _ACTIVE_CTX
        _ACTIVE_CTX = previous


ToolBinding = _ToolBinding
InstructionBinding = _InstructionBinding
McpToolCatalog = _McpToolCatalog
McpInstructionCatalog = _McpInstructionCatalog
McpNameFormatter = _McpNameFormatter
ToolsetLoader = _ToolsetLoader
McpServer = _McpServer

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
