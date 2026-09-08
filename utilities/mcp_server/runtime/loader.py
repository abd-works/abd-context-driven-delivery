"""Discover toolsets and collect MCP bindings."""
from __future__ import annotations

import ast
import inspect
import textwrap
from collections.abc import Callable

from tools.tool import _ToolsetLoader as _CddToolsetLoader

from .bindings import _InstructionBinding, _ToolBinding
from .formatter import _McpNameFormatter
from .types import _AnnotatedToolset


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
    ) -> tuple[_AnnotatedToolset, ...]:
        context = dict(constructor_context or {})
        instances: list[_AnnotatedToolset] = []
        for ref in toolset_refs:
            toolset_cls = self._toolset_loader.load(ref)
            instances.append(toolset_cls(**context))
        return tuple(instances)

    def collect_tool_bindings(self, instance: _AnnotatedToolset) -> tuple[_ToolBinding, ...]:
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
        self, instance: _AnnotatedToolset
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
    def toolset_slug(instance: _AnnotatedToolset) -> str:
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
